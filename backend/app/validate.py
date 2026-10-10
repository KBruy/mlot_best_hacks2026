"""Walidacja historii: kontrakt (Pydantic) i graf (cele, cykle, osiągalność, długość tras).

Użycie (z katalogu backend/, bez bazy):
    uv run python -m app.validate [plik.json ...]   # domyślnie content/*.json
"""
import sys
from pathlib import Path

from pydantic import ValidationError

from .models import Decision, Story

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"
DECISIONS_PER_ROUTE = 6
CHOICES_PER_DECISION = 2


class InvalidStory(Exception):
    pass


def _duplicates(ids: list[str]) -> set[str]:
    seen: set[str] = set()
    return {i for i in ids if i in seen or seen.add(i)}


def check_graph(story: Story) -> list[str]:
    """Zwraca listę błędów grafu; pusta lista oznacza poprawną historię."""
    errors = []
    nodes = {node.id: node for node in story.nodes}
    for dup in sorted(_duplicates([n.id for n in story.nodes])):
        errors.append(f"Powtórzone id węzła {dup!r}")
    for dup in sorted(_duplicates([c.id for c in story.characters])):
        errors.append(f"Powtórzone id postaci {dup!r}")
    for character in story.characters:
        entry = nodes.get(character.entry_node_id)
        if not isinstance(entry, Decision):
            errors.append(
                f"Postać {character.id!r}: wejście {character.entry_node_id!r}"
                " nie istnieje albo nie jest decyzją"
            )
    for node in story.nodes:
        if not isinstance(node, Decision):
            continue
        if len(node.choices) != CHOICES_PER_DECISION:
            errors.append(
                f"Węzeł {node.id!r} ma {len(node.choices)} opcji"
                f" zamiast {CHOICES_PER_DECISION}"
            )
        for dup in sorted(_duplicates([c.id for c in node.choices])):
            errors.append(f"Węzeł {node.id!r}: powtórzone id opcji {dup!r}")
        for choice in node.choices:
            if choice.next_node_id not in nodes:
                errors.append(
                    f"Węzeł {node.id!r}, opcja {choice.id!r}:"
                    f" cel {choice.next_node_id!r} nie istnieje"
                )
    if errors:
        return errors  # dalsza analiza wymaga poprawnych odwołań

    # Dla każdego węzła: zbiór liczb decyzji na trasach od niego do finału.
    route_lengths: dict[str, set[int]] = {}
    on_path: set[str] = set()

    def lengths(node_id: str) -> set[int]:
        if node_id in route_lengths:
            return route_lengths[node_id]
        if node_id in on_path:
            raise InvalidStory(f"Cykl przechodzący przez węzeł {node_id!r}")
        node = nodes[node_id]
        on_path.add(node_id)
        result = (
            {n + 1 for c in node.choices for n in lengths(c.next_node_id)}
            if isinstance(node, Decision)
            else {0}
        )
        on_path.discard(node_id)
        route_lengths[node_id] = result
        return result

    try:
        for character in story.characters:
            found = lengths(character.entry_node_id)
            if found != {DECISIONS_PER_ROUTE}:
                errors.append(
                    f"Postać {character.id!r}: trasy mają {sorted(found)} decyzji"
                    f" zamiast dokładnie {DECISIONS_PER_ROUTE}"
                )
    except InvalidStory as e:
        return [str(e)]

    for node_id in sorted(nodes.keys() - route_lengths.keys()):
        errors.append(f"Węzeł {node_id!r} jest nieosiągalny z wejść postaci")
    return errors


def load_story(path: Path) -> Story:
    try:
        story = Story.model_validate_json(path.read_text(encoding="utf-8"))
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
