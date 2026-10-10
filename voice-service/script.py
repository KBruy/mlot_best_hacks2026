"""Parsowanie notacji `[Glos, postac] Kwestia` i dzielenie tekstu na zdania."""
import re
from typing import NamedTuple

_PL = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
_LINE = re.compile(r"^\[\s*([^,\]]+?)\s*,\s*([^\]]+?)\s*\]\s*(\S.*)$")


class Line(NamedTuple):
    voice: str
    character: str
    text: str


def normalize(name: str) -> str:
    """'Wiedźma ' -> 'wiedzma' (identyfikatory glosow i postaci sa ascii, male litery)."""
    return name.strip().translate(_PL).lower()


def parse_script(script: str) -> list[Line]:
    lines = []
    for n, raw in enumerate(script.splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        m = _LINE.match(raw)
        if not m:
            raise ValueError(f"Linia {n}: oczekiwano formatu '[Głos, postać] Kwestia'.")
        lines.append(Line(normalize(m[1]), normalize(m[2]), m[3]))
    if not lines:
        raise ValueError("Pusty skrypt.")
    return lines


def _split_long(sentence: str, max_len: int) -> list[str]:
    """Zdanie dluzsze niz max_len tnie na przecinkach/srednikach, pakujac do max_len."""
    parts, current = [], ""
    for piece in re.split(r"(?<=[,;:])\s+", sentence):
        if current and len(current) + 1 + len(piece) > max_len:
            parts.append(current)
            current = piece
        else:
            current = f"{current} {piece}".strip()
    return parts + [current] if current else parts


def split_sentences(text: str, max_len: int = 200, min_len: int = 25) -> list[str]:
    """Dzieli tekst na kawalki do osobnej generacji: krotkie zdania skleja z sasiednim,
    bardzo dlugie tnie na przecinkach (model gubi koncowki przy dlugich wejsciach)."""
    atoms: list[str] = []
    for s in re.split(r"(?<=[.!?…])\s+", text.strip()):
        atoms.extend([s] if len(s) <= max_len else _split_long(s, max_len))
    chunks: list[str] = []
    for atom in atoms:
        if chunks and len(chunks[-1]) < min_len:
            chunks[-1] += " " + atom
        else:
            chunks.append(atom)
    if len(chunks) > 1 and len(chunks[-1]) < min_len:
        tail = chunks.pop()
        chunks[-1] += " " + tail
    return chunks
