import pytest

from script import normalize, parse_script, split_sentences


def test_normalize_strips_diacritics_and_case():
    assert normalize(" Wiedźma ") == "wiedzma"
    assert normalize("Łódź") == "lodz"


def test_parse_script_single_and_multi_line():
    lines = parse_script("[Adrian, starzec] Witajcie, dzieci.\n\n[Kristina, wiedźma] Ha!")
    assert lines == [("adrian", "starzec", "Witajcie, dzieci."), ("kristina", "wiedzma", "Ha!")]


@pytest.mark.parametrize("bad", ["", "  \n ", "Brak nawiasow", "[Adrian] tekst", "[Adrian, starzec]"])
def test_parse_script_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        parse_script(bad)


def test_split_sentences_merges_short_and_keeps_long_ones_apart():
    text = "Tak. Nie wierzcie wszystkiemu, co szepczą mury starej kamienicy. Trzymajcie się mocno, bo lecimy nad dachami miasta!"
    assert split_sentences(text) == [
        "Tak. Nie wierzcie wszystkiemu, co szepczą mury starej kamienicy.",
        "Trzymajcie się mocno, bo lecimy nad dachami miasta!",
    ]


def test_split_sentences_cuts_overlong_sentence_on_commas():
    text = ", ".join(["to jest dosyć długi fragment zdania"] * 12) + "."
    chunks = split_sentences(text, max_len=100)
    assert len(chunks) > 1 and all(len(c) <= 100 for c in chunks)
    assert " ".join(chunks).replace(",", "").split() == text.replace(",", "").split()


def test_split_sentences_trailing_short_piece_joins_previous():
    assert split_sentences("To jest całkiem długie pierwsze zdanie testowe. Tak!") == [
        "To jest całkiem długie pierwsze zdanie testowe. Tak!"
    ]
