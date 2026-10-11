"""Walidacja historii: kontrakt (Pydantic) i graf scen (cele, cykle, osiągalność,
długość ścieżek, warunki i stan, zakończenia).

Użycie (z katalogu backend/, bez bazy):
    uv run python -m app.validate [plik.json ...]   # domyślnie content/*.json
"""
import itertools
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from .models import Story, Text, Variant

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"
DECISIONS_PER_ROUTE = 6
MIN_OPTIONS, MAX_OPTIONS = 2, 3
VIEW_FIELD = "widok"  # pole stanu ustawiane przez frontend z GPS (id punktu widokowego)


class InvalidStory(Exception):
    pass


def strip_notes(value):
    """Usuwa pola zaczynające się od `_` (notatki dla ludzi, np. `_note`)."""
    if isinstance(value, dict):
        return {k: strip_notes(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [strip_notes(v) for v in value]
    return value


def _variants(text: Text) -> list[Variant]:
    if isinstance(text, str):
        return []
    return [text] if isinstance(text, Variant) else text


def check_graph(story: Story) -> list[str]:
    """Zwraca listę błędów; pusta lista oznacza poprawną historię."""
    errors = []
    domains = story.state
    scenes = story.scenes

    audio_prefix = f"/audio/{story.id}/"
    audio_texts: dict[str, str] = {}
    art_prefix = f"/art/{story.id}/"

    def check_art(url: str, where: str) -> None:
        if not (url.startswith(art_prefix) and url.endswith((".png", ".webp"))):
            errors.append(f"{where}: grafika {url!r} spoza {art_prefix}*.png|webp")

    def check_text(text: Text, where: str, spoken: bool = True) -> None:
        for variant in _variants(text):
            for key, allowed in variant.if_.items():
                if key not in domains or not set(allowed) <= set(domains[key]):
                    errors.append(f"{where}: zły warunek {key}={allowed}")
            if variant.chars is not None:
                if not spoken:
                    errors.append(f"{where}: tekst nie jest czytany, nie może zmieniać postaci")
                for url in (variant.chars.left, variant.chars.right):
                    if url is not None:
                        check_art(url, where)
            url = variant.audio_url
            if url is None:
                continue
            if not spoken:
                errors.append(f"{where}: tekst nie jest czytany, nie może mieć audio_url")
            elif not (url.startswith(audio_prefix) and url.endswith(".mp3")):
                errors.append(f"{where}: audio_url {url!r} spoza {audio_prefix}*.mp3")
            elif audio_texts.setdefault(url, variant.text) != variant.text:
                errors.append(f"{where}: audio_url {url!r} użyte dla innego tekstu")

    views = set(domains.get(VIEW_FIELD, []))
    if story.location.default_view not in views:
        errors.append(f"location: default_view spoza state.{VIEW_FIELD}")
    for vp in story.location.viewpoints:
        if vp.id not in views:
            errors.append(f"location: punkt widokowy {vp.id!r} spoza state.{VIEW_FIELD}")
    for stop_id in (story.route.legs if story.route else {}):
        if stop_id not in story.stops:
            errors.append(f"route: odcinek do nieznanego przystanku {stop_id!r}")
    for stop_id in (story.streetview.stops if story.streetview else {}):
        if stop_id not in story.stops:
            errors.append(f"streetview: ujęcie nieznanego przystanku {stop_id!r}")

    for item in story.intro.paragraphs:
        check_text(item, "intro")
    for item in story.finale.paragraphs:
        check_text(item, "finale")
    for item in story.reveal.paragraphs:
        check_text(item, "reveal")
    check_text(story.heritage, "heritage")
    check_text(story.look_up, "look_up")

    if story.start not in scenes:
        errors.append(f"start: nieznana scena {story.start!r}")
    for sid, scene in scenes.items():
        if scene.before is not None and scene.before not in story.stops:
            errors.append(f"Scena {sid!r}: nieznany przystanek {scene.before!r}")
        if scene.bg is not None:
            check_art(scene.bg, f"Scena {sid!r}")
        if not MIN_OPTIONS <= len(scene.options) <= MAX_OPTIONS:
            errors.append(
                f"Scena {sid!r} ma {len(scene.options)} opcji"
                f" zamiast {MIN_OPTIONS}–{MAX_OPTIONS}"
            )
        for i, item in enumerate(scene.scene, 1):
            check_text(item, f"Scena {sid!r}, akapit {i}")
        for i, option in enumerate(scene.options, 1):
            where = f"Scena {sid!r}, opcja {i}"
            if option.next is not None and option.next not in scenes:
                errors.append(f"{where}: cel {option.next!r} nie istnieje")
            check_text(option.text, where, spoken=False)
            for item in option.result:
                check_text(item, f"{where} (skutek)")
            for key, val in option.set.items():
                if val not in domains.get(key, []):
                    errors.append(f"{where}: zły set {key}={val}")
    for field in story.ending_by:
        if field not in domains:
            errors.append(f"ending_by: pole {field!r} spoza state")
    for key, ending in story.endings.items():
        if ending.bg is not None:
            check_art(ending.bg, f"Zakończenie {key!r}")
        for item in ending.paragraphs:
            check_text(item, f"Zakończenie {key!r}")
    if not any(r.min == 0 for r in story.ranks):
        errors.append("ranks: brak progu min=0")
    if errors:
        return errors  # analiza ścieżek wymaga poprawnych odwołań

    # Wszystkie ścieżki od startu: (lista scen, stan na końcu). Opcji jest najwyżej 3,
    # a decyzji 6, więc ścieżek jest najwyżej 3^6.
    paths: list[tuple[list[str], dict[str, str]]] = []

    def walk(sid: str, visited: list[str], state: dict[str, str]) -> None:
        if sid in visited:
            raise InvalidStory(f"Cykl przechodzący przez scenę {sid!r}")
        visited = visited + [sid]
        for option in scenes[sid].options:
            step_state = {**state, **option.set}
            if option.next is None:
                paths.append((visited, step_state))
            else:
                walk(option.next, visited, step_state)

    try:
        walk(story.start, [], {})
    except InvalidStory as e:
        return [str(e)]

    reached_endings = set()
    for visited, state in paths:
        route = " → ".join(visited)
        if len(visited) != DECISIONS_PER_ROUTE:
            errors.append(
                f"Ścieżka {route}: {len(visited)} decyzji zamiast {DECISIONS_PER_ROUTE}"
            )
        if any(field not in state for field in story.ending_by):
            errors.append(f"Ścieżka {route}: nie ustala pól zakończenia {story.ending_by}")
        else:
            reached_endings.add("|".join(state[f] for f in story.ending_by))
    reachable = {sid for visited, _ in paths for sid in visited}
    for sid in scenes:
        if sid not in reachable:
            errors.append(f"Scena {sid!r} jest nieosiągalna")
    possible = {"|".join(c) for c in itertools.product(*(domains[f] for f in story.ending_by))}
    for key in sorted(possible - story.endings.keys()):
        errors.append(f"Brak zakończenia {key!r}")
    for key in sorted(story.endings.keys() - possible):
        errors.append(f"Zakończenie {key!r} nie pasuje do pól {story.ending_by}")
    for key in sorted((story.endings.keys() & possible) - reached_endings):
        errors.append(f"Zakończenie {key!r} jest nieosiągalne")
    return errors


def parse_story(data: dict) -> Story:
    """Waliduje kontrakt (bez grafu); pola `_...` są pomijane."""
    return Story.model_validate(strip_notes(data))


def load_story(path: Path) -> Story:
    try:
        story = parse_story(json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as e:
        raise InvalidStory(f"{path}: niepoprawny JSON: {e}") from e
    except ValidationError as e:
        raise InvalidStory(f"{path}: plik nie zgadza się z kontraktem:\n{e}") from e
    errors = check_graph(story)
    if errors:
        raise InvalidStory(f"{path}: błędy grafu:\n" + "\n".join(f"- {e}" for e in errors))
    return story


def story_paths(args: list[str]) -> list[Path]:
    return [Path(a) for a in args] or sorted(CONTENT_DIR.glob("*.json"))


def main() -> None:
    paths = story_paths(sys.argv[1:])
    if not paths:
        sys.exit(f"Brak plików .json w {CONTENT_DIR}")
    failed = False
    for path in paths:
        try:
            story = load_story(path)
        except InvalidStory as e:
            failed = True
            print(e, file=sys.stderr)
        else:
            print(f"OK {story.id!r} ({path})")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
