"""Testy API z podmienioną warstwą db (bez Dockera i Postgresa)."""
import json

import pytest
from fastapi.testclient import TestClient

from app import db, import_story
from app.main import app

client = TestClient(app)


def unavailable(*_):
    raise db.DatabaseUnavailable("test")


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_list_stories(monkeypatch):
    summary = {"id": "s1", "title": "T", "intro": {"title": "T", "paragraphs": ["I"]}}
    monkeypatch.setattr(db, "list_stories", lambda: [summary])
    response = client.get("/api/stories")
    assert response.status_code == 200
    assert response.json() == [summary]


def test_get_story_returns_stored_json(monkeypatch, story_dict):
    stored = json.dumps(story_dict)
    monkeypatch.setattr(db, "get_story_json", lambda story_id: stored)
    response = client.get("/api/stories/legenda-fixture")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == story_dict


def test_unknown_story_is_404(monkeypatch):
    monkeypatch.setattr(db, "get_story_json", lambda story_id: None)
    assert client.get("/api/stories/nie-ma").status_code == 404


@pytest.mark.parametrize("url, func", [
    ("/api/stories", "list_stories"),
    ("/api/stories/s1", "get_story_json"),
])
def test_database_down_is_503(monkeypatch, url, func):
    monkeypatch.setattr(db, func, unavailable)
    response = client.get(url)
    assert response.status_code == 503
    assert response.json() == {"detail": "Baza danych jest niedostępna."}


def test_missing_database_url_is_unavailable(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(db.DatabaseUnavailable):
        db.connect()


def test_import_rejects_invalid_file_before_touching_db(monkeypatch, story_dict, tmp_path):
    story_dict["scenes"]["s1"]["options"][0]["next"] = "nie_ma"
    file = tmp_path / "zla.json"
    file.write_text(json.dumps(story_dict), encoding="utf-8")
    monkeypatch.setattr(import_story.db, "connect", unavailable)
    monkeypatch.setattr("sys.argv", ["import_story", str(file)])
    with pytest.raises(SystemExit, match="błędy grafu"):
        import_story.main()


def test_openapi_documents_error_responses():
    paths = client.get("/openapi.json").json()["paths"]
    assert {"200", "503"} <= paths["/api/stories"]["get"]["responses"].keys()
    assert {"200", "404", "503"} <= paths["/api/stories/{story_id}"]["get"]["responses"].keys()
