import pytest

import keys


@pytest.fixture(autouse=True)
def keys_file(tmp_path, monkeypatch):
    monkeypatch.setattr(keys, "KEYS_FILE", tmp_path / "api_keys.json")
    monkeypatch.setattr(keys, "_cache", None)


def test_create_verify_and_hash_only_storage():
    key = keys.create("gra")
    assert key.startswith("vs_")
    assert keys.verify(key) == "gra"
    assert keys.verify(key + "x") is None
    assert key not in keys.KEYS_FILE.read_text(encoding="utf-8")


def test_duplicate_name_is_rejected_and_revoke_invalidates():
    key = keys.create("gra")
    with pytest.raises(ValueError):
        keys.create("gra")
    assert keys.revoke("gra") is True
    assert keys.verify(key) is None
    assert keys.revoke("gra") is False


def test_keys_are_unique_per_creation():
    assert keys.create("a") != keys.create("b")
    assert [n for n, _ in keys.listing()] == ["a", "b"]
