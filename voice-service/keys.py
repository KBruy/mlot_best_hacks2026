"""Klucze API serwisu: w pliku trzymamy tylko skroty SHA-256, nigdy sam klucz.

Klucz ma ~256 bitow losowosci, wiec zwykly SHA-256 (bez soli) wystarcza.
Plik jest czytany ponownie po zmianie, wiec odwolanie klucza dziala bez restartu.
"""
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

KEYS_FILE = Path(__file__).parent / "api_keys.json"
PREFIX = "vs_"

_cache: tuple[int, dict] | None = None  # (mtime_ns, dane)


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _read() -> dict:
    global _cache
    if not KEYS_FILE.exists():
        return {}
    mtime = KEYS_FILE.stat().st_mtime_ns
    if _cache is None or _cache[0] != mtime:
        _cache = (mtime, json.loads(KEYS_FILE.read_text(encoding="utf-8")))
    return _cache[1]


def _write(data: dict) -> None:
    tmp = KEYS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, KEYS_FILE)


def create(name: str) -> str:
    """Tworzy klucz dla podanej nazwy i zwraca go - to jedyny moment, gdy jest widoczny."""
    data = dict(_read())
    if name in data:
        raise ValueError(f"Klucz o nazwie '{name}' już istnieje (najpierw go odwołaj).")
    key = PREFIX + secrets.token_urlsafe(32)
    data[name] = {"hash": _hash(key), "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    _write(data)
    return key


def revoke(name: str) -> bool:
    data = dict(_read())
    if data.pop(name, None) is None:
        return False
    _write(data)
    return True


def listing() -> list[tuple[str, str]]:
    return [(name, meta["created"]) for name, meta in _read().items()]


def verify(key: str) -> str | None:
    """Zwraca nazwe klucza, jesli pasuje, w przeciwnym razie None."""
    candidate = _hash(key)
    match = None
    for name, meta in _read().items():  # bez wczesnego wyjscia: staly czas
        if hmac.compare_digest(candidate, meta["hash"]):
            match = name
    return match
