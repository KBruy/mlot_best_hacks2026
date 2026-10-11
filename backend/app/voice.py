"""Klient voice-service. Klucz API zostaje w backendzie; przeglądarka woła tylko /api/voice/*."""
import json
import os
import socket
import urllib.error
import urllib.request

# Generacja na CPU trwa ok. 10× czasu nagrania (voice-service/API.md, sekcja 7).
TIMEOUT_S = 180


class VoiceUnavailable(Exception):
    pass


class VoiceTimeout(Exception):
    pass


def request(method: str, path: str, body: dict | None = None) -> tuple[int, str, bytes]:
    """Zwraca (status, Content-Type, treść) odpowiedzi voice-service, także dla kodów błędów."""
    url = os.environ.get("VOICE_SERVICE_URL")
    key = os.environ.get("VOICE_API_KEY")
    if not url or not key:
        raise VoiceUnavailable("Brak VOICE_SERVICE_URL lub VOICE_API_KEY (sprawdź plik .env).")
    req = urllib.request.Request(
        url.rstrip("/") + path,
        method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"X-API-Key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            return r.status, r.headers.get("Content-Type", "application/json"), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", "application/json"), e.read()
    except (TimeoutError, socket.timeout) as e:
        raise VoiceTimeout(str(e)) from e
    except urllib.error.URLError as e:
        if isinstance(e.reason, (TimeoutError, socket.timeout)):
            raise VoiceTimeout(str(e)) from e
        raise VoiceUnavailable(str(e)) from e
