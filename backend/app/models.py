"""Modele historii (jedno źródło prawdy dla importera, walidatora i API).

Docstringi klas i opisy pól trafiają do schematów OpenAPI (/docs).
"""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


def _audio(what: str):
    return Field(
        None,
        description=f"Opcjonalna ścieżka do nagrania {what} (MP3 serwowany statycznie"
        " przez frontend, np. /audio/<id historii>/<plik>.mp3). Pole może nie występować.",
    )


class Choice(_Model):
    """Opcja w scenie decyzyjnej. Po wyborze frontend pokazuje `consequence`, potem przechodzi do `next_node_id`."""

    id: str = Field(description="Unikalne w obrębie sceny.")
    text: str
    consequence: str = Field(description="Tekst konsekwencji pokazywany po wyborze.")
    next_node_id: str = Field(description="Id węzła (sceny lub finału), do którego prowadzi „Dalej”.")
    audio_url: str | None = _audio("konsekwencji")


class Decision(_Model):
    """Scena decyzyjna z dokładnie dwiema opcjami."""

    id: str = Field(description="Unikalne w historii.")
    type: Literal["decision"]
    text: str = Field(description="Narracja; zwykły tekst, akapity rozdzielone pustą linią.")
    choices: list[Choice]
    audio_url: str | None = _audio("tekstu sceny")


class Ending(_Model):
    """Finał historii; nie ma przejść dalej."""

    id: str = Field(description="Unikalne w historii.")
    type: Literal["ending"]
    title: str
    text: str = Field(description="Narracja; zwykły tekst, akapity rozdzielone pustą linią.")
    audio_url: str | None = _audio("tekstu finału")


Node = Annotated[Decision | Ending, Field(discriminator="type")]


class Character(_Model):
    """Grywalna postać; wybór postaci nie jest decyzją fabularną."""

    id: str = Field(description="Unikalne w historii.")
    name: str
    description: str
    entry_node_id: str = Field(description="Id pierwszej sceny (decyzji) tej postaci.")


class Story(_Model):
    """Pełna historia: frontend pobiera ją raz i wykonuje wszystkie przejścia lokalnie."""

    id: str = Field(description="Stałe id historii; jego zmiana tworzy w bazie nową historię.")
    title: str
    intro: str
    characters: list[Character]
    nodes: list[Node] = Field(
        description="Wszystkie węzły grafu. Każda trasa od wejścia postaci ma 6 decyzji i kończy się finałem."
    )


class StorySummary(_Model):
    """Pozycja listy historii (bez grafu)."""

    id: str
    title: str
    intro: str
