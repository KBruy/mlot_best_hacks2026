import contextlib
import io
import json
import unittest
import urllib.error
import urllib.request

import main
import mapa

STORY = main.load_story()
SCENES = STORY["scenes"]
PATHS = main.scene_paths(STORY)
DEMO_GPS = main.demo_gps(STORY)
POINTS = {p["label"]: (p["lat"], p["lon"]) for p in STORY["test_points"]}
FAR = POINTS["Daleko: Dworzec Główny"]
TOWERS = (STORY["stops"]["wieze"]["lat"], STORY["stops"]["wieze"]["lon"])
NAMES = ("Tekl", "Martynk", "Michał")

ALL_LEGEND = [0, 0, 0, 0, 0, 0]   # bal → kawaler → wyrok → czarownica → pomoc → uwolnienie
NO_LEGEND = [1, 1, 1, 1, 1, 1]    # czeladnik → ucieczka → błaganie → milczenie → kradzież → zamiana


def resolve_intro(view):
    return main.resolve_all(STORY["intro"]["paragraphs"], {"widok": view})


def play_path(path, view="ogolny"):
    """Przechodzi ścieżkę bez terminala; zwraca (stan, wynik, wyświetlone teksty)."""
    state, score, texts = {"widok": view}, 0, resolve_intro(view)
    for sid, i in path:
        rendered = main.render_decision(SCENES[sid], state)
        texts += rendered["scene"] + rendered["options"]
        outcome = main.choose(SCENES[sid], i, state)
        texts += outcome["result"]
        score += outcome["legend"]
    ending = main.render_ending(STORY, state, score)
    texts += [ending["title"]] + ending["paragraphs"]
    texts += main.resolve_all(STORY["finale"]["paragraphs"], state)
    texts += [SCENES[sid]["fact"] for sid, _ in path]
    return state, score, texts


# (ścieżka, strefa, stan końcowy, wynik, teksty) dla każdej ścieżki i każdej strefy startu
ROUTES = [(path, view) + play_path(path, view) for view in STORY["state"]["widok"] for path in PATHS]


def path_for(choices):
    sid, path = STORY["start"], []
    for i in choices:
        path.append((sid, i))
        sid = SCENES[sid]["options"][i]["next"]
    return path


def run_game(story, answers, width=80, color=False, gps=DEMO_GPS):
    """Uruchamia grę na skryptowych odpowiedziach; zwraca (status, całe wyjście)."""
    answers = iter(answers)
    out = []

    def fake_input(prompt):
        out.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise EOFError

    status = main.play(story, fake_input, out.append, width=width, color=color, gps=gps)
    return status, "\n".join(out)


def script(choices, restart="n"):
    """Enter po intro, numer wyboru i Enter przy każdej decyzji, potem odpowiedź na restart."""
    answers = [""]
    for c in choices:
        answers += [str(c + 1), ""]
    return answers + [restart]


class StoryStructure(unittest.TestCase):
    def test_story_validates(self):
        self.assertEqual(main.validate_story(STORY), [])

    def test_every_scene_has_two_or_three_options_a_fact_and_both_kinds_of_choice(self):
        for sid, scene in SCENES.items():
            self.assertIn(len(scene["options"]), (2, 3), sid)
            self.assertTrue(scene["fact"], sid)
            self.assertTrue(any(o["legend"] for o in scene["options"]), sid)
            self.assertTrue(any(not o["legend"] for o in scene["options"]), sid)

    def test_every_path_has_six_decisions_and_reaches_an_ending(self):
        for path in PATHS:
            self.assertEqual(len(path), 6)
        for _, _, state, _, _ in ROUTES:
            self.assertIn(state["los"], STORY["endings"])

    def test_every_scene_ending_score_and_rank_is_reachable(self):
        self.assertEqual({sid for path in PATHS for sid, _ in path}, set(SCENES))
        self.assertEqual({r[2]["los"] for r in ROUTES}, set(STORY["endings"]))
        self.assertEqual({r[3] for r in ROUTES}, set(range(7)))
        ranks = {main.rank_for(STORY, r[3])["title"] for r in ROUTES}
        self.assertEqual(ranks, {r["title"] for r in STORY["ranks"]})


class Branching(unittest.TestCase):
    def test_choices_lead_to_really_different_scenes(self):
        start = [o["next"] for o in SCENES[STORY["start"]]["options"]]
        self.assertEqual(len(set(start)), 3)                       # trzy różne drogi panny
        rynek = [o["next"] for o in SCENES["starzec"]["options"]]
        self.assertEqual(len(set(rynek)), 3)                       # trzy różne scenariusze na Rynku
        routes = {tuple(sid for sid, _ in path) for path in PATHS}
        self.assertGreaterEqual(len(routes), 9)

    def test_keypoints_are_on_every_path_in_order(self):
        for path in PATHS:
            visited = [sid for sid, _ in path]
            self.assertEqual(visited[2], "wyrok", visited)
            self.assertEqual(visited[4], "starzec", visited)
            self.assertEqual(SCENES[visited[2]]["keypoint"], "wyrok")
            self.assertEqual(SCENES[visited[4]]["keypoint"], "rynek")

    def test_verdict_always_ends_on_the_bridge(self):
        for sciezka in STORY["state"]["sciezka"]:
            scene = " ".join(main.render_decision(SCENES["wyrok"], {"sciezka": sciezka})["scene"])
            self.assertIn("Przeklinam", scene)
            for i in range(len(SCENES["wyrok"]["options"])):
                result = " ".join(main.choose(SCENES["wyrok"], i, {"sciezka": sciezka})["result"])
                self.assertIn("na tym mostku", result)
                self.assertIn("miotłę", result)

    def test_the_witch_always_decides_to_help(self):
        for sciezka in STORY["state"]["sciezka"]:
            for i in range(len(SCENES["mostek"]["options"])):
                result = " ".join(main.choose(SCENES["mostek"], i, {"sciezka": sciezka})["result"])
                self.assertIn("Postanawiasz jej pomóc", result)

    def test_earlier_path_changes_the_verdict_and_the_old_womans_tale(self):
        verdicts, tales = set(), set()
        for sciezka in STORY["state"]["sciezka"]:
            verdicts.add(tuple(main.render_decision(SCENES["wyrok"], {"sciezka": sciezka})["scene"]))
            tales.add(tuple(main.choose(SCENES["mostek"], 0, {"sciezka": sciezka})["result"]))
        self.assertEqual(len(verdicts), len(STORY["state"]["sciezka"]))
        self.assertEqual(len(tales), len(STORY["state"]["sciezka"]))

    def test_empty_bridge_only_when_she_is_freed(self):
        for path, _, state, _, texts in ROUTES:
            if state["los"] != "wolna":
                self.assertFalse(any("panny już tam nie ma" in t for t in texts), path)

    def test_every_option_has_distinct_result(self):
        state = {"widok": "ogolny", "sciezka": "proznosc"}
        for sid, scene in SCENES.items():
            results = [" ".join(main.choose(scene, i, dict(state))["result"])
                       for i in range(len(scene["options"]))]
            self.assertEqual(len(set(results)), len(results), sid)


class Gameplay(unittest.TestCase):
    def test_full_playthrough_shows_phases_and_score_only_at_the_end(self):
        status, out = run_game(STORY, script(ALL_LEGEND))
        self.assertEqual(status, "finished")
        for n in range(1, 7):
            self.assertIn(f"Decyzja {n}/6", out)
        phases = [out.index(f"FAZA {n}/4") for n in range(1, 5)]
        self.assertEqual(phases, sorted(phases))
        game, finale = out.split("Twoja wersja a legenda:")
        self.assertNotIn("✓", game)
        self.assertNotIn("Zgodność", game)
        for sid, _ in path_for(ALL_LEGEND):
            self.assertNotIn(SCENES[sid]["fact"][:40], game)
            self.assertIn(f"✓ {SCENES[sid]['title']}:", finale)
        self.assertIn("■■■■■■ 6/6", finale)
        self.assertIn("Kronikarz legend", finale)
        self.assertIn("Pusty mostek", out)
        self.assertIn(STORY["finale"]["paragraphs"][1], out)
        self.assertIn(STORY["heritage"], finale)

    def test_zero_score_route(self):
        _, out = run_game(STORY, script(NO_LEGEND))
        self.assertEqual(out.split("Twoja wersja a legenda:")[1].count("✗ "), 6)
        self.assertIn("□□□□□□ 0/6", out)
        self.assertIn("Totalny remiks", out)
        self.assertIn("Czeladnik", out)
        self.assertIn(STORY["endings"]["zamiana"]["title"], out)

    def test_enter_pauses_are_not_decisions(self):
        _, out = run_game(STORY, script(ALL_LEGEND))
        self.assertEqual(out.count("[Enter - dalej]"), 7)  # po intro i po każdej decyzji
        self.assertEqual(out.count("Decyzja "), 6)
        _, out = run_game(STORY, ["", "", "1", ""])  # pusty Enter przy wyborze nie wybiera
        self.assertEqual(out.count("Wpisz numer od 1 do 3"), 1)
        self.assertEqual(out.count("Decyzja "), 2)

    def test_invalid_input_asks_again(self):
        status, out = run_game(STORY, ["", "x", "", "0", "9", "-1", "1.5", "²", "1", ""])
        self.assertEqual(status, "interrupted")  # skończyły się odpowiedzi
        self.assertEqual(out.count("Wpisz numer od 1 do 3"), 7)
        self.assertEqual(out.count("Decyzja "), 2)

    def test_quit_with_q(self):
        status, out = run_game(STORY, ["", "q"])
        self.assertEqual(status, "quit")
        self.assertIn("Koniec gry", out)

    def test_quit_mid_game_and_at_restart_prompt(self):
        self.assertEqual(run_game(STORY, ["q"])[0], "quit")            # na pauzie po intro
        self.assertEqual(run_game(STORY, ["", "1", "q"])[0], "quit")  # na pauzie po decyzji
        self.assertEqual(run_game(STORY, ["", "1", "", "Q"])[0], "quit")
        self.assertEqual(run_game(STORY, script(ALL_LEGEND, restart="q"))[0], "quit")

    def test_ctrl_c_exits_gracefully(self):
        def interrupt(prompt):
            raise KeyboardInterrupt

        out = []
        self.assertEqual(main.play(STORY, interrupt, out.append, gps=DEMO_GPS), "interrupted")
        self.assertTrue(any("Przerwano" in line for line in out))

    def test_restart_starts_fresh_with_zero_score(self):
        answers = script(ALL_LEGEND, restart="t") + script(NO_LEGEND, restart="n")
        status, out = run_game(STORY, answers)
        self.assertEqual(status, "finished")
        self.assertEqual(out.count("Decyzja 1/6"), 2)
        second = out.split("Zagrać jeszcze raz?")[1]
        self.assertIn("0/6", second)
        self.assertNotIn("Pusty mostek", second)

    def test_invalid_restart_answer_asks_again(self):
        status, out = run_game(STORY, script(ALL_LEGEND, restart="może") + ["n"])
        self.assertEqual(status, "finished")
        self.assertIn("Wpisz t (tak) albo n (nie).", out)

    def test_output_wraps_to_width_and_keeps_paragraphs(self):
        for width in (40, 80):
            _, out = run_game(STORY, script(ALL_LEGEND), width=width)
            self.assertTrue(all(len(line) < width for line in out.splitlines()), width)
        self.assertIn("\n\n", out)

    def test_color_only_when_enabled(self):
        _, plain = run_game(STORY, script(ALL_LEGEND))
        self.assertNotIn("\x1b[", plain)
        _, colored = run_game(STORY, script(ALL_LEGEND), color=True)
        self.assertIn("\x1b[1;36m", colored)
        self.assertIn("\x1b[1;32m✓", colored)

    def test_ascii_art_fits_narrow_terminal(self):
        _, out = run_game(STORY, script(ALL_LEGEND), width=40)
        self.assertIn(SCENES["mostek"]["art"][2], out)
        for scene in SCENES.values():
            for line in scene.get("art", []):
                self.assertLess(len(line), 40)

    def test_route_is_not_too_long(self):
        extra = sum(len(p.split()) for p in STORY["reveal"]["paragraphs"])
        extra += len(STORY["heritage"].split()) + len(STORY["look_up"].split())
        extra += sum(len((s["walk"] + " " + s["arrive"]).split()) for s in STORY["stops"].values())
        for path, _, _, _, texts in ROUTES:
            words = sum(len(t.split()) for t in texts) + extra
            self.assertTrue(600 <= words <= 1000, (words, path))


class Location(unittest.TestCase):
    def test_distance_is_sane(self):
        self.assertAlmostEqual(main.distance_m(51.0, 17.0, 52.0, 17.0), 111_195, delta=200)
        self.assertEqual(main.distance_m(51.1, 17.0, 51.1, 17.0), 0)

    def test_each_viewpoint_is_detected(self):
        for vp in STORY["location"]["viewpoints"]:
            where = main.locate(STORY, (vp["lat"], vp["lon"]))
            self.assertTrue(where["unlocked"])
            self.assertEqual(where["view"], vp["id"])

    def test_near_but_outside_zones_uses_general_view(self):
        where = main.locate(STORY, POINTS["W pobliżu kościoła, poza strefami"])
        self.assertTrue(where["unlocked"])
        self.assertEqual(where["view"], "ogolny")

    def test_far_or_missing_position_is_locked(self):
        self.assertFalse(main.locate(STORY, FAR)["unlocked"])
        self.assertFalse(main.locate(STORY, None)["unlocked"])

    def test_every_view_has_its_own_intro(self):
        intros = {tuple(resolve_intro(v)) for v in STORY["state"]["widok"]}
        self.assertEqual(len(intros), len(STORY["state"]["widok"]))

    def test_no_gps_means_no_game(self):
        status, out = run_game(STORY, [], gps=lambda target: None)
        self.assertEqual(status, "locked")
        self.assertIn("działa tylko na miejscu", out)
        self.assertNotIn("Decyzja", out)

    def test_far_away_asks_to_come_closer_until_unlocked(self):
        readings = iter([FAR, FAR, TOWERS])

        def gps(target):
            return next(readings) if target is None else (target["lat"], target["lon"])

        status, out = run_game(STORY, ["", ""] + script(ALL_LEGEND), gps=gps)
        self.assertEqual(status, "finished")
        self.assertEqual(out.count("Podejdź bliżej"), 2)
        self.assertEqual(out.count("Legenda odblokowana"), 1)
        self.assertLess(out.index("Legenda odblokowana"), out.index("Decyzja 1/6"))

    def test_walk_waits_for_arrival_and_allows_manual_skip(self):
        start = POINTS["Kościół: boczna ściana (południe)"]
        readings = iter([start, start, TOWERS, TOWERS])  # start, 2x w drodze pod wieże, 1x „na Rynku”

        def gps(target):
            return next(readings)

        answers = ([""] + ["1", ""] * 2          # intro i faza 1 (dwie decyzje)
                   + [""]                        # jeszcze nie pod wieżami: sprawdź ponownie
                   + ["1", ""] * 2               # faza 2: wyrok i czarownica
                   + ["j"]                       # GPS nie widzi Rynku: „jestem na miejscu”
                   + ["1", ""] * 2 + ["n"])      # faza 3
        status, out = run_game(STORY, answers, gps=gps)
        self.assertEqual(status, "finished")
        self.assertIn("spójrz w lewo", out)
        self.assertRegex(out, r"Do celu zostało ok\. \d+ m")
        wieze, rynek = STORY["stops"]["wieze"]["arrive"], STORY["stops"]["rynek"]["arrive"]
        self.assertLess(out.index(wieze), out.index("Decyzja 3/6"))
        self.assertLess(out.index(rynek), out.index("Decyzja 5/6"))

    def test_walk_fits_in_ten_minutes_with_reading(self):
        for choices in (ALL_LEGEND, NO_LEGEND, [2, 0, 2, 2, 2, 2]):
            _, out = run_game(STORY, script(choices))
            reading = len(out.split()) / 200  # słów na minutę przy spokojnym czytaniu
            self.assertLessEqual(main.walk_minutes(STORY) + reading, 10, choices)

    def test_names_are_revealed_only_at_the_end(self):
        for choices in (ALL_LEGEND, NO_LEGEND, [2, 1, 2, 2, 2, 2]):
            _, out = run_game(STORY, script(choices))
            game, finale = out.split(STORY["reveal"]["title"])
            for name in NAMES:
                self.assertNotIn(name, game, choices)
                self.assertIn(name, finale)


class RouteWalk(unittest.TestCase):
    def test_route_is_about_as_long_as_google_says(self):
        meters = sum(main.path_length_m(leg) for leg in main.route_legs(STORY).values())
        self.assertTrue(220 <= meters <= 300, meters)  # Google Maps: ok. 260 m

    def test_route_starts_in_a_zone_and_every_leg_ends_at_its_stop(self):
        start = tuple(STORY["route"]["start"])
        self.assertTrue(main.locate(STORY, start)["unlocked"])
        self.assertNotEqual(main.locate(STORY, start)["view"], "ogolny")
        for name, leg in main.route_legs(STORY).items():
            stop = STORY["stops"][name]
            self.assertLessEqual(main.distance_m(*leg[-1], stop["lat"], stop["lon"]), stop["radius_m"])

    def test_densify_keeps_steps_short(self):
        for leg in main.route_legs(STORY).values():
            points = main.densify(leg, 20)
            steps = [main.distance_m(*a, *b) for a, b in zip(points, points[1:])]
            self.assertLessEqual(max(steps), 20.5)
            self.assertEqual(points[-1], leg[-1])

    def test_route_gps_plays_the_whole_walk_without_enter(self):
        status, out = run_game(STORY, script(ALL_LEGEND), gps=main.RouteGps(STORY))
        self.assertEqual(status, "finished")
        self.assertNotIn("sprawdź pozycję", out)
        self.assertEqual(out.count("jesteś na miejscu"), 2)
        self.assertGreaterEqual(out.count("jeszcze ok."), 6)
        self.assertIn("spójrz w lewo", out)  # trasa zaczyna się od południa
        for name in ("wieze", "rynek"):
            self.assertIn(STORY["stops"][name]["arrive"], out)

    def test_tempo_waits_between_readings(self):
        waits = []
        gps = main.RouteGps(STORY, tempo=0.5, sleep=waits.append)
        run_game(STORY, script(ALL_LEGEND), gps=gps)
        self.assertTrue(waits)
        self.assertTrue(all(w == 0.5 for w in waits))


class LiveMapTests(unittest.TestCase):
    def setUp(self):
        self.live = mapa.LiveMap(port=0)  # wolny port wybrany przez system
        self.addCleanup(self.live.close)

    def get(self, path):
        with urllib.request.urlopen(self.live.url.rstrip("/") + path, timeout=5) as r:
            return r.headers.get("Content-Type"), r.read().decode()

    def test_page_embeds_street_view_and_minimap_and_polls_position(self):
        kind, body = self.get("/")
        self.assertIn("text/html", kind)
        self.assertIn("output=svembed", body)          # Street View bez klucza API
        self.assertIn("maps.google.com/maps?q=", body)  # mała mapa satelitarna
        self.assertIn('fetch("/pos"', body)

    def test_position_endpoint_follows_updates(self):
        self.assertEqual(json.loads(self.get("/pos")[1])["lat"], None)
        view = {"lat": 51.1, "lon": 17.03, "heading": 90, "pitch": 0}
        self.live.update((51.1, 17.03), "test", view)
        self.live.update(title="FAZA 1/4")  # zmienia tylko tytuł, reszta zostaje
        self.assertEqual(json.loads(self.get("/pos")[1]),
                         {"lat": 51.1, "lon": 17.03, "note": "test", "title": "FAZA 1/4", "view": view})

    def test_unknown_path_is_404(self):
        with self.assertRaises(urllib.error.HTTPError):
            self.get("/nie-ma")

    def test_mapped_gps_reports_every_reading_of_a_walk(self):
        gps = mapa.MappedGps(main.RouteGps(STORY), self.live, STORY, main.distance_m)
        self.assertTrue(gps.live)
        status, _ = run_game(STORY, script(ALL_LEGEND), gps=gps)
        self.assertEqual(status, "finished")
        last = self.live.snapshot()
        stop = STORY["stops"]["rynek"]
        self.assertLessEqual(main.distance_m(last["lat"], last["lon"], stop["lat"], stop["lon"]),
                             stop["radius_m"])
        self.assertIn("jesteś: " + stop["label"], last["note"])

    def test_street_view_follows_the_walk_and_ends_on_the_bridge(self):
        gps = mapa.MappedGps(main.RouteGps(STORY), self.live, STORY, main.distance_m)
        views = []
        original = self.live.update

        def spy(*args, **kwargs):
            original(*args, **kwargs)
            views.append(self.live.snapshot())
        self.live.update = spy
        answers = iter(script(ALL_LEGEND))
        main.play(STORY, lambda prompt: next(answers), lambda text: None, gps=gps,
                  observer=gps.notify)
        sv = STORY["streetview"]
        anchors = {tuple(a) for a in sv["anchors"]}
        shown = [v["view"] for v in views if v["view"]]
        for view in shown:
            self.assertTrue(0 <= view["heading"] < 360)
            spot = (view["lat"], view["lon"])
            special = [sv["finale"]] + list(sv["stops"].values())
            self.assertTrue(spot in anchors or any(spot == (s["lat"], s["lon"]) for s in special), spot)
        for name in ("wieze", "rynek"):
            self.assertIn(sv["stops"][name], shown)  # na przystankach ustalone ujęcia
        last = views[-1]
        self.assertEqual((last["view"]["lat"], last["view"]["lon"]), (sv["finale"]["lat"], sv["finale"]["lon"]))
        self.assertIn("mostka", last["note"])
        self.assertEqual(last["title"], STORY["finale"]["act"])

    def test_street_view_data_matches_the_route(self):
        sv = STORY["streetview"]
        route = [p for leg in main.route_legs(STORY).values() for p in main.densify(leg, 10)]
        for anchor in sv["anchors"]:
            self.assertLess(min(main.distance_m(*anchor, *p) for p in route), 25, anchor)
        for name, view in sv["stops"].items():
            stop = STORY["stops"][name]
            self.assertLess(main.distance_m(view["lat"], view["lon"], stop["lat"], stop["lon"]),
                            stop["radius_m"] + 20, name)
        self.assertLess(main.distance_m(sv["finale"]["lat"], sv["finale"]["lon"], *TOWERS), 30)

    def test_bearing(self):
        self.assertEqual(mapa.bearing_deg(51.0, 17.0, 51.1, 17.0), 0)    # na północ
        self.assertEqual(mapa.bearing_deg(51.0, 17.0, 51.0, 17.1), 90)   # na wschód
        self.assertEqual(mapa.bearing_deg(51.0, 17.0, 50.9, 17.0), 180)  # na południe

    def test_game_notifies_scenes_and_finale(self):
        events = []
        answers = iter(script(ALL_LEGEND))
        main.play(STORY, lambda prompt: next(answers), lambda text: None, gps=DEMO_GPS,
                  observer=lambda event, data: events.append((event, data)))
        self.assertEqual([e for e, _ in events].count("scene"), 6)
        self.assertEqual(events[-1], ("finale", {"act": STORY["finale"]["act"]}))
        self.assertEqual(events[0][1]["act"], SCENES[STORY["start"]]["act"])


class CommandLine(unittest.TestCase):
    def run_main(self, argv, answers=()):
        answers = iter(answers)
        out = []

        def fake_input(prompt):
            out.append(prompt)
            try:
                return next(answers)
            except StopIteration:
                raise EOFError

        code = main.main(argv, fake_input, out.append)
        return code, "\n".join(out)

    def test_demo_mode_plays_without_menu(self):
        code, out = self.run_main(["--demo"], script(ALL_LEGEND))
        self.assertEqual(code, 0)
        self.assertNotIn("Symulacja GPS", out)
        self.assertIn("Kronikarz legend", out)

    def test_route_flag_plays_the_walk(self):
        code, out = self.run_main(["--trasa", "--tempo", "0"], script(ALL_LEGEND))
        self.assertEqual(code, 0)
        self.assertNotIn("Symulacja GPS", out)
        self.assertIn("jesteś na miejscu", out)

    def test_route_only_walks_every_stop_without_story(self):
        code, out = self.run_main(["--tylko-trasa", "--tempo", "0"], [""] * 5)
        self.assertEqual(code, 0)
        for name in STORY["route"]["legs"]:
            self.assertIn(f"Przystanek „{name}”", out)
        self.assertIn("Ujęcie finału", out)
        self.assertNotIn("Decyzja 1/6", out)

    def test_route_only_quits_on_q(self):
        code, out = self.run_main(["--tylko-trasa", "--tempo", "0"], ["q"])
        self.assertEqual(code, 0)
        self.assertNotIn("Ujęcie finału", out)
        self.assertIn("Koniec podglądu trasy", out)

    def test_map_flag_prints_local_address(self):
        code, out = self.run_main(["--trasa", "--tempo", "0", "--mapa", "--port", "0"],
                                  script(ALL_LEGEND))
        self.assertEqual(code, 0)
        self.assertRegex(out, r"Mapa na żywo: http://127\.0\.0\.1:\d+/")

    def test_no_gps_flag_locks(self):
        code, out = self.run_main(["--no-gps"])
        self.assertEqual(code, 1)
        self.assertIn("działa tylko na miejscu", out)

    def test_gps_flag_far_away_shows_lock_then_menu(self):
        _, out = self.run_main(["--gps", f"{FAR[0]},{FAR[1]}"], ["", "q"])
        self.assertIn("Podejdź bliżej", out)
        self.assertIn("Symulacja GPS", out)

    def test_bad_gps_flag_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main.main(["--gps", "tutaj"])


if __name__ == "__main__":
    unittest.main()
