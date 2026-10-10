import json

import pytest

from app.validate import CONTENT_DIR, InvalidStory, check_graph, load_story, parse_story


def errors(story: dict) -> list[str]:
    return check_graph(parse_story(story))


def test_fixture_is_valid(story_dict):
    assert errors(story_dict) == []


def test_all_content_files_are_valid():
    for file in CONTENT_DIR.glob("*.json"):
        load_story(file)


def test_notes_are_ignored(story_dict):
    story_dict["_note"] = "dla ludzi"
    story_dict["location"]["_note"] = "dla ludzi"
    assert errors(story_dict) == []


def test_missing_target(story_dict):
    story_dict["scenes"]["s3"]["options"][0]["next"] = "nie_ma"
    assert errors(story_dict) == ["Scena 's3', opcja 1: cel 'nie_ma' nie istnieje"]


def test_unknown_start(story_dict):
    story_dict["start"] = "nie_ma"
    assert "start: nieznana scena 'nie_ma'" in errors(story_dict)


def test_cycle(story_dict):
    story_dict["scenes"]["s5"]["options"][0]["next"] = "s3"
    assert errors(story_dict) == ["Cykl przechodzący przez scenę 's3'"]


def test_route_with_five_decisions(story_dict):
    # Ścieżka a pomija s2a; s2a staje się nieosiągalna.
    story_dict["scenes"]["s1"]["options"][0]["next"] = "s3"
    errs = errors(story_dict)
    assert "Ścieżka s1 → s3 → s4 → s5 → s6: 5 decyzji zamiast 6" in errs
    assert "Scena 's2a' jest nieosiągalna" in errs


def test_route_ending_early(story_dict):
    story_dict["scenes"]["s5"]["options"][0] |= {"next": None, "set": {"los": "final_1"}}
    assert any("5 decyzji zamiast 6" in e for e in errors(story_dict))


@pytest.mark.parametrize("count", [1, 4])
def test_wrong_number_of_options(story_dict, count):
    options = story_dict["scenes"]["s4"]["options"]
    story_dict["scenes"]["s4"]["options"] = (options * 2)[:count]
    assert errors(story_dict) == [f"Scena 's4' ma {count} opcji zamiast 2–3"]


def test_three_options_are_allowed(story_dict):
    options = story_dict["scenes"]["s4"]["options"]
    options.append(dict(options[0]))
    assert errors(story_dict) == []


def test_unknown_condition_and_set(story_dict):
    story_dict["scenes"]["s3"]["scene"][1][0]["if"] = {"sciezka": ["zla"]}
    story_dict["scenes"]["s2a"]["options"][0]["set"] = {"nie_ma": "x"}
    assert sorted(errors(story_dict)) == [
        "Scena 's2a', opcja 1: zły set nie_ma=x",
        "Scena 's3', akapit 2: zły warunek sciezka=['zla']",
    ]


def test_view_outside_state(story_dict):
    story_dict["location"]["default_view"] = "nie_ma"
    assert errors(story_dict) == ["location: default_view spoza state.widok"]


def test_unknown_stop(story_dict):
    story_dict["scenes"]["s1"]["before"] = "nie_ma"
    assert errors(story_dict) == ["Scena 's1': nieznany przystanek 'nie_ma'"]


def test_missing_and_unreachable_endings(story_dict):
    story_dict["state"]["los"].append("final_3")
    story_dict["endings"]["final_3"] = story_dict["endings"]["final_1"]
    assert errors(story_dict) == ["Zakończenie 'final_3' jest nieosiągalne"]
    del story_dict["endings"]["final_3"]
    assert errors(story_dict) == ["Brak zakończenia 'final_3'"]


def test_route_must_set_ending_fields(story_dict):
    story_dict["scenes"]["s6"]["options"][1]["set"] = {}
    errs = errors(story_dict)
    assert any("nie ustala pól zakończenia" in e for e in errs)
    assert "Zakończenie 'final_2' jest nieosiągalne" in errs


def test_rank_zero_required(story_dict):
    story_dict["ranks"] = [r for r in story_dict["ranks"] if r["min"] != 0]
    assert errors(story_dict) == ["ranks: brak progu min=0"]


def test_contract_rejects_wrong_types(story_dict, tmp_path):
    story_dict["scenes"]["s2a"]["fact"] = 123
    file = tmp_path / "zla.json"
    file.write_text(json.dumps(story_dict), encoding="utf-8")
    with pytest.raises(InvalidStory, match="nie zgadza się z kontraktem"):
        load_story(file)


def test_contract_rejects_unknown_fields(story_dict):
    story_dict["extra"] = 1
    with pytest.raises(ValueError):
        parse_story(story_dict)


def test_dump_keeps_if_alias(story_dict):
    dumped = parse_story(story_dict).model_dump(exclude_unset=True, by_alias=True)
    assert dumped["scenes"]["s3"]["scene"][1][0] == {
        "if": {"sciezka": ["a"]}, "text": "Akapit dla ścieżki a."
    }
