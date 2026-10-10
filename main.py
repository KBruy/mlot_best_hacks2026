#!/usr/bin/env python3
"""Mostek Czarownic: krótki spacer z legendą wokół kościoła św. Marii Magdaleny.

Gra działa tylko na miejscu: bez lokalizacji albo zbyt daleko od kościoła
legenda pozostaje zablokowana. W terminalu GPS jest symulowany (patrz main()).

Historia to graf scen: każda opcja wskazuje następną scenę ("next", null = koniec).
Ścieżki rozchodzą się między punktami kluczowymi i spotykają się w nich znowu.
"""

import argparse
import itertools
import json
import math
import os
import shutil
import sys
import textwrap
import time
from pathlib import Path

STORY_PATH = Path(__file__).with_name("story.json")
DECISIONS = 6  # tyle decyzji ma każda ścieżka przez graf scen
WALK_SPEED_M_PER_MIN = 70  # spokojny spacer po Starym Mieście


class QuitGame(Exception):
    """Gracz wpisał q."""


# --- lokalizacja ------------------------------------------------------------

def distance_m(lat1, lon1, lat2, lon2):
    """Odległość po powierzchni Ziemi (wzór haversine), w metrach."""
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def locate(story, position):
    """Zwraca, czy legenda jest odblokowana, odległość od kościoła i strefę widoku."""
    loc = story["location"]
    if position is None:
        return {"unlocked": False, "distance": None, "view": None}
    lat, lon = position
    distance = distance_m(lat, lon, *loc["center"])
    view, best = loc["default_view"], None
    for vp in loc["viewpoints"]:
        d = distance_m(lat, lon, vp["lat"], vp["lon"])
        if d <= vp["radius_m"] and (best is None or d < best):
            view, best = vp["id"], d
    return {"unlocked": distance <= loc["unlock_radius_m"], "distance": distance, "view": view}


def format_distance(meters):
    if meters >= 1000:
        return f"{meters / 1000:.1f} km".replace(".", ",")
    return f"{round(meters / 10) * 10:.0f} m"


def path_length_m(points):
    return sum(distance_m(*a, *b) for a, b in zip(points, points[1:]))


def densify(points, step_m):
    """Dzieli łamaną na odcinki nie dłuższe niż step_m (proste przybliżenie liniowe)."""
    out = [tuple(points[0])]
    for a, b in zip(points, points[1:]):
        parts = max(1, math.ceil(distance_m(*a, *b) / step_m))
        for i in range(1, parts + 1):
            t = i / parts
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def route_legs(story):
    """Odcinki trasy spaceru: każdy od poprzedniej pozycji do kolejnego przystanku."""
    route = story["route"]
    position, legs = tuple(route["start"]), {}
    for name, points in route["legs"].items():
        stop = story["stops"][name]
        legs[name] = [position] + [tuple(p) for p in points] + [(stop["lat"], stop["lon"])]
        position = legs[name][-1]
    return legs


def walk_minutes(story):
    """Szacowany czas samego chodzenia: po prawdziwej trasie, a bez niej w linii prostej."""
    if "route" in story:
        return sum(path_length_m(leg) for leg in route_legs(story).values()) / WALK_SPEED_M_PER_MIN
    points = [tuple(story["location"]["center"])]
    for scene in story["scenes"].values():
        if scene.get("before"):
            stop = story["stops"][scene["before"]]
            points.append((stop["lat"], stop["lon"]))
    meters = sum(distance_m(*a, *b) for a, b in zip(points, points[1:]))
    return meters / WALK_SPEED_M_PER_MIN


# --- dane i logika historii -------------------------------------------------

def load_story(path=STORY_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def matches(cond, state):
    """Warunek to słownik {pole: [dozwolone wartości]}; wszystkie muszą pasować."""
    return all(state.get(key) in allowed for key, allowed in cond.items())


def resolve(value, state):
    """Tekst (str) albo lista wariantów {"if": ..., "text": ...}; wygrywa pierwszy pasujący."""
    if isinstance(value, str):
        return value
    variants = [value] if isinstance(value, dict) else value
    for variant in variants:
        if matches(variant.get("if", {}), state):
            return variant["text"]
    return ""


def resolve_all(items, state):
    texts = (resolve(item, state) for item in items)
    return [t for t in texts if t]


def render_decision(decision, state):
    return {
        "act": decision.get("act"),
        "title": decision["title"],
        "art": decision.get("art", []),
        "scene": resolve_all(decision["scene"], state),
        "options": [resolve(opt["text"], state) for opt in decision["options"]],
    }


def choose(decision, index, state):
    """Zapisuje wybór w state. Zwraca skutek, następną scenę, zgodność i fakt z legendy."""
    option = decision["options"][index]
    state.update(option["set"])
    return {
        "title": decision["title"],
        "result": resolve_all(option["result"], state),
        "next": option["next"],
        "legend": option["legend"],
        "fact": decision["fact"],
    }


def scene_paths(story):
    """Wszystkie ścieżki przez graf jako listy (id sceny, numer opcji)."""
    paths = []

    def walk(scene_id, path):
        if len(path) > 2 * DECISIONS:  # zabezpieczenie przed pętlą w grafie
            paths.append(path)
            return
        for i, option in enumerate(story["scenes"][scene_id]["options"]):
            step = path + [(scene_id, i)]
            if option["next"] is None:
                paths.append(step)
            elif option["next"] in story["scenes"]:
                walk(option["next"], step)

    walk(story["start"], [])
    return paths


def rank_for(story, score):
    return max((r for r in story["ranks"] if r["min"] <= score), key=lambda r: r["min"])


def render_ending(story, state, score):
    key = "|".join(state[field] for field in story["ending_by"])
    ending = story["endings"][key]
    return {
        "title": ending["title"],
        "paragraphs": resolve_all(ending["paragraphs"], state),
        "score": score,
        "rank": rank_for(story, score),
    }


def _check_value(value, where, domains, problems):
    if isinstance(value, str):
        return
    for variant in [value] if isinstance(value, dict) else value:
        if isinstance(variant, str) or "text" not in variant:
            problems.append(f"{where}: wariant bez pola text")
            continue
        for key, allowed in variant.get("if", {}).items():
            if key not in domains or not isinstance(allowed, list) \
                    or not set(allowed) <= set(domains[key]):
                problems.append(f"{where}: zły warunek {key}={allowed}")


def validate_story(story):
    """Zwraca listę problemów; pusta lista oznacza poprawną historię."""
    problems = []
    domains = story["state"]
    scenes = story["scenes"]
    loc = story["location"]
    views = set(domains.get("widok", []))
    if loc["default_view"] not in views:
        problems.append("location: default_view spoza state.widok")
    for vp in loc["viewpoints"]:
        if vp["id"] not in views:
            problems.append(f"location: punkt widokowy {vp['id']} spoza state.widok")
    for item in story["intro"]["paragraphs"]:
        _check_value(item, "intro", domains, problems)
    if story["start"] not in scenes:
        problems.append(f"start: nieznana scena {story['start']}")
        return problems
    for sid, scene in scenes.items():
        if scene.get("before") and scene["before"] not in story["stops"]:
            problems.append(f"scena {sid}: nieznany przystanek {scene['before']}")
        if not 2 <= len(scene["options"]) <= 3:
            problems.append(f"scena {sid}: {len(scene['options'])} opcji")
        if not isinstance(scene.get("act", ""), str):
            problems.append(f"scena {sid}: act musi być tekstem")
        if not isinstance(scene.get("fact"), str):
            problems.append(f"scena {sid}: brak faktu z legendy")
        if not all(isinstance(line, str) for line in scene.get("art", [])):
            problems.append(f"scena {sid}: art musi być listą tekstów")
        for i, item in enumerate(scene["scene"]):
            _check_value(item, f"scena {sid}, akapit {i}", domains, problems)
        for i, option in enumerate(scene["options"], 1):
            where = f"scena {sid}, opcja {i}"
            if not isinstance(option.get("legend"), bool):
                problems.append(f"{where}: brak pola legend (true/false)")
            if option.get("next", "?") is not None and option.get("next") not in scenes:
                problems.append(f"{where}: nieznana następna scena {option.get('next')}")
            _check_value(option["text"], where, domains, problems)
            for item in option["result"]:
                _check_value(item, where + " (skutek)", domains, problems)
            for key, val in option["set"].items():
                if val not in domains.get(key, []):
                    problems.append(f"{where}: zły set {key}={val}")
    for path in scene_paths(story):
        if len(path) != DECISIONS:
            names = " → ".join(sid for sid, _ in path)
            problems.append(f"ścieżka {names}: {len(path)} decyzji zamiast {DECISIONS}")
        state = {}
        for sid, i in path:
            state.update(scenes[sid]["options"][i]["set"])
        if any(field not in state for field in story["ending_by"]):
            problems.append(f"ścieżka kończąca się w {path[-1][0]} nie ustala pól zakończenia")
    reachable = {sid for path in scene_paths(story) for sid, _ in path}
    for sid in scenes:
        if sid not in reachable:
            problems.append(f"scena {sid} jest nieosiągalna")
    fields = story["ending_by"]
    for combo in itertools.product(*(domains[f] for f in fields)):
        key = "|".join(combo)
        if key not in story["endings"]:
            problems.append(f"brak zakończenia {key}")
            continue
        for item in story["endings"][key]["paragraphs"]:
            _check_value(item, f"zakończenie {key}", domains, problems)
    if not any(r["min"] == 0 for r in story["ranks"]):
        problems.append("ranks: brak progu min=0")
    return problems


# --- interfejs terminala ----------------------------------------------------

def play(story, input_fn=input, output_fn=print, width=None, color=False, gps=None,
         observer=None):
    """Prowadzi grę (z możliwością restartu).

    gps(cel) zwraca pozycję (lat, lon) albo None, gdy lokalizacja jest niedostępna;
    cel to przystanek, do którego gracz idzie (None na starcie). Bez GPS gra się
    nie zaczyna. Zwraca "finished", "quit", "interrupted" albo "locked".
    Zgodność z legendą jest liczona po cichu i pokazywana dopiero na końcu.
    observer(zdarzenie, dane) dostaje "scene" przy każdej scenie i "finale" na końcu
    (np. podgląd Street View w mapa.py).
    """

    def notify(event, data):
        if observer:
            observer(event, data)

    def line_width():
        columns = width or shutil.get_terminal_size((80, 24)).columns
        return max(columns - 1, 30)

    def paint(text, code):
        return f"\x1b[{code}m{text}\x1b[0m" if color else text

    def say(text, indent="", hanging="", style=None):
        lines = textwrap.fill(text, width=line_width(), initial_indent=indent,
                              subsequent_indent=hanging).split("\n")
        if style:
            lines = [paint(line, style) for line in lines]
        output_fn("\n".join(lines))

    def say_paragraphs(paragraphs, style=None):
        for paragraph in paragraphs:
            say(paragraph, style=style)
            output_fn("")

    def say_option(number, text):
        prefix = f"  {number}. "
        wrapped = textwrap.fill(text, width=line_width(), initial_indent=prefix,
                                subsequent_indent=" " * len(prefix))
        output_fn(wrapped.replace(prefix, paint(prefix, "1;33"), 1) if color else wrapped)

    def say_title_box(title):
        inner = f"  {title}  "
        for line in ("╔" + "═" * len(inner) + "╗", "║" + inner + "║", "╚" + "═" * len(inner) + "╝"):
            output_fn(paint(line, "1;33"))

    def ask(prompt):
        answer = input_fn(prompt).strip()
        if answer.lower() == "q":
            raise QuitGame
        return answer

    def pause():
        ask(paint("[Enter - dalej] ", "2"))
        output_fn("")

    def ask_choice(count):
        while True:
            answer = ask("Twój wybór: ")
            if answer.isdecimal() and 1 <= int(answer) <= count:
                return int(answer) - 1
            say(f"Wpisz numer od 1 do {count} albo q, aby wyjść.")

    def ask_restart():
        while True:
            answer = ask("Zagrać jeszcze raz? [t/n]: ").lower()
            if answer in ("t", "tak"):
                return True
            if answer in ("n", "nie"):
                return False
            say("Wpisz t (tak) albo n (nie).")

    def unlock():
        """Czeka, aż gracz będzie wystarczająco blisko kościoła. Zwraca strefę albo None."""
        loc = story["location"]
        while True:
            where = locate(story, gps(None) if gps else None)
            if where["distance"] is None:
                say("📍 Ta legenda działa tylko na miejscu. Włącz lokalizację i przyjdź "
                    f"pod {loc['name']}.", style="1;31")
                return None
            if where["unlocked"]:
                say("📍 Legenda odblokowana!", style="1;32")
                output_fn("")
                return where["view"]
            say(f"🔒 Jesteś {format_distance(where['distance'])} od miejsca, w którym "
                f"wydarzyła się ta legenda. Podejdź bliżej (do {loc['unlock_radius_m']} m) "
                f"pod {loc['name']}, żeby ją odblokować.", style="1;33")
            ask(paint("[Enter - sprawdź pozycję ponownie] ", "2"))
            output_fn("")

    def walk_to(name):
        stop = story["stops"][name]
        say(f"🚶 {stop['label']}", style="1;35")
        say(stop["walk"])
        output_fn("")
        if getattr(gps, "live", False) and walk_live(stop):
            say(stop["arrive"], style="1")
            output_fn("")
            return
        while True:
            position = gps(stop)
            if position is not None:
                left = distance_m(*position, stop["lat"], stop["lon"])
                if left <= stop["radius_m"]:
                    break
                say(f"📍 Do celu zostało ok. {format_distance(left)}.")
            else:
                say("📍 Nie widzę twojej pozycji.")
            answer = ask(paint("[Enter - sprawdź pozycję, j - jestem na miejscu] ", "2"))
            output_fn("")
            if answer.lower() == "j":
                break
        say(stop["arrive"], style="1")
        output_fn("")

    def walk_live(stop):
        """GPS na żywo (np. odtwarzana trasa): pozycja aktualizuje się sama, bez Entera."""
        total, shown = None, None
        for _ in range(500):
            position = gps(stop)
            if position is None:
                return False
            left = distance_m(*position, stop["lat"], stop["lon"])
            if left <= stop["radius_m"]:
                say(f"📍 {'▓' * 10} jesteś na miejscu")
                output_fn("")
                return True
            total = total or left
            span = max(total - stop["radius_m"], 1)
            done = max(0, min(9, int(10 * (total - left) / span)))
            line = f"📍 {'▓' * done}{'░' * (10 - done)} jeszcze ok. {format_distance(left)}"
            if line != shown:
                say(line)
                shown = line
        return False

    def play_once():
        view = unlock()
        if view is None:
            return False
        state, recap = {"widok": view}, []
        say_title_box(story["intro"]["title"])
        output_fn("")
        say_paragraphs(resolve_all(story["intro"]["paragraphs"], state))
        pause()
        scene_id, number = story["start"], 0
        while scene_id is not None:
            decision = story["scenes"][scene_id]
            number += 1
            notify("scene", {"id": scene_id, "title": decision["title"], "act": decision.get("act")})
            if decision.get("before"):
                walk_to(decision["before"])
            view_ = render_decision(decision, state)
            if view_["act"]:
                say(f"══ {view_['act']} ══", style="1;35")
                output_fn("")
            say(f"--- Decyzja {number}/{DECISIONS}: {view_['title']} ---", style="1;36")
            output_fn("")
            for line in view_["art"]:
                output_fn(paint(line, "36"))
            if view_["art"]:
                output_fn("")
            say_paragraphs(view_["scene"])
            for i, text in enumerate(view_["options"], 1):
                say_option(i, text)
            output_fn("")
            outcome = choose(decision, ask_choice(len(view_["options"])), state)
            recap.append(outcome)
            scene_id = outcome["next"]
            output_fn("")
            say_paragraphs(outcome["result"])
            pause()
        score = sum(o["legend"] for o in recap)
        ending = render_ending(story, state, score)
        notify("finale", {"act": story["finale"]["act"]})
        say(f"══ {story['finale']['act']} ══", style="1;35")
        output_fn("")
        say_title_box(ending["title"])
        output_fn("")
        say_paragraphs(ending["paragraphs"])
        say_paragraphs(resolve_all(story["finale"]["paragraphs"], state))
        say(story["reveal"]["title"], style="1;35")
        say_paragraphs(story["reveal"]["paragraphs"])
        say("Twoja wersja a legenda:", style="1")
        output_fn("")
        for o in recap:
            mark, style = ("✓", "1;32") if o["legend"] else ("✗", "1;31")
            lines = textwrap.fill(f"{mark} {o['title']}: {o['fact']}", width=line_width(),
                                  subsequent_indent="  ").split("\n")
            output_fn("\n".join([lines[0].replace(mark, paint(mark, style), 1)] + lines[1:]))
        output_fn("")
        bar = "■" * score + "□" * (DECISIONS - score)
        say(f"Zgodność z legendą: {bar} {score}/{DECISIONS}", style="1;35")
        say(f"{ending['rank']['title']}. {ending['rank']['text']}", style="1")
        output_fn("")
        say(story["heritage"])
        say(f"👀 {story['look_up']}", style="1;36")
        output_fn("")
        return True

    try:
        while True:
            if not play_once():
                return "locked"
            if not ask_restart():
                break
        say("Dzięki za grę!")
        return "finished"
    except QuitGame:
        output_fn("")
        say("Koniec gry. Do zobaczenia pod mostkiem!")
        return "quit"
    except (KeyboardInterrupt, EOFError):
        output_fn("")
        say("Przerwano. Do zobaczenia pod mostkiem!")
        return "interrupted"


# --- symulacja GPS ----------------------------------------------------------

def demo_gps(story):
    """Tryb prezentacji: start naprzeciw wież, potem natychmiast „dochodzisz” do celu."""
    def read(target):
        if target is None:
            return tuple(story["demo_start"])
        return target["lat"], target["lon"]
    return read


class RouteGps:
    """Odtwarza spacer po trasie z story.json: każdy odczyt to kolejne ok. step_m metrów.

    tempo to przerwa (w sekundach) między odczytami, przydatna na prezentacjach.
    """

    live = True

    def __init__(self, story, step_m=20, tempo=0.0, sleep=time.sleep):
        self.story, self.tempo, self.sleep = story, tempo, sleep
        self.legs = {name: densify(points, step_m) for name, points in route_legs(story).items()}
        self.position = tuple(story["route"]["start"])
        self.leg, self.queue = None, []

    def __call__(self, target):
        if target is None:
            return self.position
        name = next(n for n, s in self.story["stops"].items() if s is target)
        if name != self.leg:
            self.leg, self.queue = name, list(self.legs[name][1:])
        if self.queue:
            if self.tempo:
                self.sleep(self.tempo)
            self.position = self.queue.pop(0)
        return self.position


def fixed_gps(position):
    """Stała pozycja (np. z --gps): gracz nigdzie się nie rusza."""
    return lambda target: position


def menu_gps(story, input_fn=input, output_fn=print, first=None):
    """Symulacja chodzenia: przy każdym odczycie GPS gracz wybiera, gdzie teraz stoi."""
    pending = [first] if first else []
    points = story["test_points"]

    def read(target):
        if pending:
            return pending.pop()
        output_fn("📡 Symulacja GPS: gdzie teraz jesteś?")
        for i, point in enumerate(points, 1):
            output_fn(f"  {i}. {point['label']}")
        while True:
            answer = input_fn("Pozycja: ").strip()
            if answer.lower() == "q":
                raise QuitGame
            if answer.isdecimal() and 1 <= int(answer) <= len(points):
                output_fn("")
                point = points[int(answer) - 1]
                return point["lat"], point["lon"]
            output_fn(f"Wpisz numer od 1 do {len(points)} albo q, aby wyjść.")
    return read


def parse_position(text):
    try:
        lat, lon = (float(part) for part in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("podaj pozycję jako SZEROKOŚĆ,DŁUGOŚĆ, np. 51.1098,17.0348")
    return lat, lon


def main(argv=None, input_fn=input, output_fn=print):
    parser = argparse.ArgumentParser(description="Mostek Czarownic: legenda na spacer.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--gps", type=parse_position, metavar="LAT,LON",
                       help="symulowana pozycja startowa; dalszy spacer przez menu")
    group.add_argument("--demo", action="store_true",
                       help="tryb prezentacji: start pod kościołem, przystanki zaliczane od razu")
    group.add_argument("--trasa", action="store_true",
                       help="odtwarza prawdziwy spacer po trasie zapisanej w story.json")
    group.add_argument("--no-gps", action="store_true",
                       help="symuluje brak zgody na lokalizację")
    parser.add_argument("--tempo", type=float, default=None, metavar="SEKUNDY",
                        help="przy --trasa: przerwa między odczytami GPS (domyślnie 1 s, 0 = od razu)")
    parser.add_argument("--mapa", action="store_true",
                        help="pokazuje spacer na żywo w Street View i na mapie Google w przeglądarce")
    parser.add_argument("--port", type=int, default=8765, help="port strony z mapą (domyślnie 8765)")
    args = parser.parse_args(argv)

    story = load_story()
    problems = validate_story(story)
    if problems:
        raise SystemExit("Błąd w story.json:\n" + "\n".join(problems))
    if args.no_gps:
        gps = lambda target: None
    elif args.demo:
        gps = demo_gps(story)
    elif args.trasa:
        gps = RouteGps(story, tempo=1.0 if args.tempo is None else args.tempo)
    else:
        gps = menu_gps(story, input_fn, output_fn, first=args.gps)
    live_map = None
    if args.mapa:
        import webbrowser
        from mapa import LiveMap, MappedGps
        live_map = LiveMap(args.port)
        gps = MappedGps(gps, live_map, story, distance_m)
        output_fn(f"🗺️  Mapa na żywo: {live_map.url}")
        output_fn("")
        if output_fn is print:
            webbrowser.open(live_map.url)
    color = output_fn is print and sys.stdout.isatty() and "NO_COLOR" not in os.environ
    observer = getattr(gps, "notify", None)
    try:
        status = play(story, input_fn, output_fn, color=color, gps=gps, observer=observer)
    finally:
        if live_map:
            live_map.close()
    return 1 if status == "locked" else 0


if __name__ == "__main__":
    sys.exit(main())
