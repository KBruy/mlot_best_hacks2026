import json

import pytest

from app.models import Story
from app.validate import CONTENT_DIR, InvalidStory, check_graph, load_story


def node(story: dict, node_id: str) -> dict:
    return next(n for n in story["nodes"] if n["id"] == node_id)


def errors(story: dict) -> list[str]:
    return check_graph(Story.model_validate(story))


def test_fixture_is_valid(story_dict):
    assert errors(story_dict) == []


def test_all_content_files_are_valid():
    for file in CONTENT_DIR.glob("*.json"):
        load_story(file)


def test_missing_target(story_dict):
    node(story_dict, "n3")["choices"][0]["next_node_id"] = "nie_ma"
    assert errors(story_dict) == ["Węzeł 'n3', opcja 'a': cel 'nie_ma' nie istnieje"]


def test_cycle(story_dict):
    node(story_dict, "n5")["choices"][0]["next_node_id"] = "n2"
    assert any("Cykl" in e for e in errors(story_dict))


def test_route_with_five_decisions(story_dict):
    # Postać 1 pomija n2: jej trasy mają 5 decyzji; n2 nadal osiągalny z postaci 2.
    for choice in node(story_dict, "n1_postac1")["choices"]:
        choice["next_node_id"] = "n3"
    assert errors(story_dict) == [
        "Postać 'postac_1': trasy mają [5] decyzji zamiast dokładnie 6"
    ]


def test_mixed_route_lengths(story_dict):
    node(story_dict, "n6")["choices"][0]["next_node_id"] = "ending_1"
    node(story_dict, "n5")["choices"][0]["next_node_id"] = "ending_1"
    assert errors(story_dict) == [
        "Postać 'postac_1': trasy mają [5, 6] decyzji zamiast dokładnie 6",
        "Postać 'postac_2': trasy mają [5, 6] decyzji zamiast dokładnie 6",
    ]


def test_unreachable_node(story_dict):
    story_dict["nodes"].append(
        {"id": "sierota", "type": "ending", "title": "T", "text": "T"}
    )
    assert errors(story_dict) == ["Węzeł 'sierota' jest nieosiągalny z wejść postaci"]


def test_wrong_number_of_choices(story_dict):
    choices = node(story_dict, "n2")["choices"]
    choices.append({**choices[0], "id": "c"})
    assert errors(story_dict) == ["Węzeł 'n2' ma 3 opcji zamiast 2"]


def test_duplicate_ids(story_dict):
    node(story_dict, "n2")["choices"][1]["id"] = "a"
    story_dict["characters"][1]["id"] = story_dict["characters"][0]["id"]
    story_dict["nodes"].append(dict(node(story_dict, "ending_2")))
    assert sorted(errors(story_dict)) == [
        "Powtórzone id postaci 'postac_1'",
        "Powtórzone id węzła 'ending_2'",
        "Węzeł 'n2': powtórzone id opcji 'a'",
    ]


@pytest.mark.parametrize("entry", ["nie_ma", "ending_1"])
def test_bad_character_entry(story_dict, entry):
    story_dict["characters"][0]["entry_node_id"] = entry
    assert errors(story_dict) == [
        f"Postać 'postac_1': wejście {entry!r} nie istnieje albo nie jest decyzją"
    ]


def test_contract_rejects_wrong_types(story_dict, tmp_path):
    node(story_dict, "n2")["text"] = 123
    file = tmp_path / "zla.json"
    file.write_text(json.dumps(story_dict), encoding="utf-8")
    with pytest.raises(InvalidStory, match="nie zgadza się z kontraktem"):
        load_story(file)


def test_contract_rejects_unknown_fields_and_types(story_dict):
    bad = json.loads(json.dumps(story_dict))
    bad["nodes"][0]["type"] = "walka"
    with pytest.raises(ValueError):
        Story.model_validate(bad)
    story_dict["extra"] = 1
    with pytest.raises(ValueError):
        Story.model_validate(story_dict)
