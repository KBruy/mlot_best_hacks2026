import contextlib
import io
import unittest

import main

STORY = main.load_story()
DEMO_GPS = main.demo_gps(STORY)
POINTS = {p["label"]: (p["lat"], p["lon"]) for p in STORY["test_points"]}
FAR = POINTS["Daleko: Dworzec Główny"]
TOWERS = (STORY["stops"]["wieze"]["lat"], STORY["stops"]["wieze"]["lon"])
NAMES = ("Tekl", "Martynk", "Michał")


def all_routes(story=STORY):
    """Zwraca listę tras: (indeksy wyborów, końcowy stan, wynik, teksty wyświetlone w trasie)."""
    routes = []

    def walk(step, state, score, choices, texts):
        if step == len(story["decisions"]):
            ending = main.render_ending(story, state, score)
            facts = [d["fact"] for d in story["decisions"]]
            routes.append((choices, state, score,
                           texts + [ending["title"]] + ending["paragraphs"] + facts))
            return
        decision = story["decisions"][step]
        view = main.render_decision(decision, state)
        shown = texts + view["scene"] + view["options"]
        for i in range(len(decision["options"])):
            new_state = dict(state)
            outcome = main.choose(decision, i, new_state)
            walk(step + 1, new_state, score + outcome["legend"], choices + [i],
                 shown + outcome["result"])

    for view in STORY["state"]["widok"]:
        walk(0, {"widok": view}, 0, [], resolve_intro(view))
    return routes


def resolve_intro(view):
    return main.resolve_all(STORY["intro"]["paragraphs"], {"widok": view})


ROUTES = all_routes()


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


ALL_LEGEND = [0, 0, 0, 0, 0, 0]   # każdy wybór zgodny z legendą
NO_LEGEND = [2, 2, 2, 1, 1, 1]    # żaden wybór zgodny z legendą


class StoryStructure(unittest.TestCase):
    def test_story_validates(self):
        self.assertEqual(main.validate_story(STORY), [])

    def test_six_decisions_with_two_or_three_options(self):
        self.assertEqual(len(STORY["decisions"]), 6)
        for decision in STORY["decisions"]:
            self.assertIn(len(decision["options"]), (2, 3))

    def test_every_decision_has_legend_fact_and_a_legend_option(self):
        for decision in STORY["decisions"]:
            self.assertTrue(decision["fact"])
            self.assertTrue(any(o["legend"] for o in decision["options"]))
            self.assertTrue(any(not o["legend"] for o in decision["options"]))

    def test_every_route_has_six_decisions_and_reaches_an_ending(self):
        expected = len(STORY["state"]["widok"])
        for decision in STORY["decisions"]:
            expected *= len(decision["options"])
        self.assertEqual(len(ROUTES), expected)
        for choices, state, _, _ in ROUTES:
            self.assertEqual(len(choices), 6)
            self.assertIn(state["wish"], STORY["endings"])

    def test_all_endings_and_scores_reachable(self):
        self.assertEqual({s["wish"] for _, s, _, _ in ROUTES}, set(STORY["endings"]))
        self.assertEqual({score for _, _, score, _ in ROUTES}, set(range(7)))

    def test_every_rank_reachable(self):
        ranks = {main.rank_for(STORY, score)["title"] for _, _, score, _ in ROUTES}
        self.assertEqual(ranks, {r["title"] for r in STORY["ranks"]})


# Stałe punkty legendy: muszą wydarzyć się na każdej trasie, niezależnie od wyborów.
CANON = {
    2: ["Przeklinam cię", "mostku między wieżami"],   # klątwa i porwanie
    3: ["Postanawiasz jej pomóc"],                     # Martynkę porusza los Tekli
    4: ["różdżk", "pod pręgierzem"],                   # różdżka Michała się odnajduje
}


class Consistency(unittest.TestCase):
    def test_canon_beats_happen_on_every_choice(self):
        for step, phrases in CANON.items():
            decision = STORY["decisions"][step]
            for klatwa in STORY["state"]["klatwa"]:
                for i in range(len(decision["options"])):
                    result = " ".join(main.choose(decision, i, {"klatwa": klatwa})["result"])
                    for phrase in phrases:
                        self.assertIn(phrase, result, (step, i))

    def test_tekla_is_free_in_every_ending(self):
        for key, ending in STORY["endings"].items():
            text = " ".join(ending["paragraphs"])
            self.assertTrue("wolna" in text or "panny już tam nie ma" in text, key)

    def test_tekla_disappears_only_when_freed_by_the_wish(self):
        for choices, state, _, texts in ROUTES:
            if state["wish"] != "uwolnij":
                self.assertFalse(any("panny już tam nie ma" in t for t in texts), choices)

    def test_each_scene_follows_from_the_previous_choice(self):
        decisions = STORY["decisions"]
        # (decyzja, pole z poprzedniej decyzji, część: scena albo skutek)
        links = [(1, "dom", "scene"), (2, "swaty", "scene"), (3, "klatwa", "result"),
                 (4, "czarownica", "scene"), (5, "rynek", "scene")]
        for step, field, part in links:
            variants = set()
            for value in STORY["state"][field]:
                state = {field: value}
                if part == "scene":
                    variants.add(tuple(main.render_decision(decisions[step], state)["scene"]))
                else:
                    variants.add(tuple(main.choose(decisions[step], 0, state)["result"]))
            self.assertEqual(len(variants), len(STORY["state"][field]), (step, field))

    def test_every_option_has_distinct_result(self):
        state = {"widok": "ogolny", "klatwa": "smiech", "czarownica": "pytac", "rynek": "pomoc"}
        for decision in STORY["decisions"]:
            results = [" ".join(main.choose(decision, i, dict(state))["result"])
                       for i in range(len(decision["options"]))]
            self.assertEqual(len(set(results)), len(results))


class Gameplay(unittest.TestCase):
    def test_full_playthrough_shows_progress_and_score_only_at_the_end(self):
        status, out = run_game(STORY, script(ALL_LEGEND))
        self.assertEqual(status, "finished")
        for n in range(1, 7):
            self.assertIn(f"Decyzja {n}/6", out)
        self.assertIn("AKT I: PANNA Z KAMIENICY", out)
        self.assertIn("AKT II: MŁODA CZAROWNICA", out)
        game, finale = out.split("Twoja wersja a legenda:")
        self.assertNotIn("✓", game)
        self.assertNotIn("Zgodność", game)
        for decision in STORY["decisions"]:
            self.assertNotIn(decision["fact"][:40], game)
            self.assertIn(f"✓ {decision['title']}:", finale)
        self.assertIn("■■■■■■ 6/6", finale)
        self.assertIn("Kronikarz legend", finale)
        self.assertIn("Pusty mostek", out)
        self.assertIn(STORY["heritage"], finale)

    def test_zero_score_route(self):
        _, out = run_game(STORY, script(NO_LEGEND))
        self.assertEqual(out.split("Twoja wersja a legenda:")[1].count("✗ "), 6)
        self.assertIn("□□□□□□ 0/6", out)
        self.assertIn("Totalny remiks", out)

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
        self.assertIn(STORY["decisions"][3]["art"][2], out)
        for decision in STORY["decisions"]:
            for line in decision.get("art", []):
                self.assertLess(len(line), 40)

    def test_route_is_short(self):
        extra = sum(len(p.split()) for p in STORY["reveal"]["paragraphs"])
        extra += len(STORY["heritage"].split()) + len(STORY["look_up"].split())
        extra += sum(len((s["walk"] + " " + s["arrive"]).split()) for s in STORY["stops"].values())
        for _, _, _, texts in ROUTES:
            words = sum(len(t.split()) for t in texts) + extra  # trasy zawierają już intro
            self.assertTrue(600 <= words <= 900, words)


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

        answers = ([""] + ["1", ""] * 3        # intro i akt I
                   + [""]                       # jeszcze nie pod wieżami: sprawdź ponownie
                   + ["1", ""]                  # decyzja 4
                   + ["j"]                      # GPS nie widzi Rynku: „jestem na miejscu”
                   + ["1", ""] * 2 + ["n"])
        status, out = run_game(STORY, answers, gps=gps)
        self.assertEqual(status, "finished")
        self.assertIn("Wieże masz po lewej", out)
        self.assertIn("Do celu zostało ok. 100 m", out)
        wieze, rynek = STORY["stops"]["wieze"]["arrive"], STORY["stops"]["rynek"]["arrive"]
        self.assertLess(out.index(wieze), out.index("Decyzja 4/6"))
        self.assertLess(out.index(rynek), out.index("Decyzja 5/6"))

    def test_walk_fits_in_ten_minutes_with_reading(self):
        _, out = run_game(STORY, script(ALL_LEGEND))
        reading = len(out.split()) / 200  # słów na minutę przy spokojnym czytaniu
        self.assertLessEqual(main.walk_minutes(STORY) + reading, 10)

    def test_names_are_revealed_only_at_the_end(self):
        for choices in (ALL_LEGEND, NO_LEGEND):
            _, out = run_game(STORY, script(choices))
            game, finale = out.split(STORY["reveal"]["title"])
            for name in NAMES:
                self.assertNotIn(name, game, choices)
                self.assertIn(name, finale)


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
