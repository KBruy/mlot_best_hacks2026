"""Modele historii zgodne z kontraktem z CLAUDE.md (jedno źródło prawdy dla importera, walidatora i API)."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Choice(_Model):
    id: str
    text: str
    consequence: str
    next_node_id: str
    audio_url: str | None = None  # nagranie konsekwencji


class Decision(_Model):
    id: str
    type: Literal["decision"]
    text: str
    choices: list[Choice]
    audio_url: str | None = None  # nagranie tekstu sceny


class Ending(_Model):
    id: str
    type: Literal["ending"]
    title: str
    text: str
    audio_url: str | None = None  # nagranie tekstu finału


Node = Annotated[Decision | Ending, Field(discriminator="type")]


class Character(_Model):
    id: str
    name: str
    description: str
    entry_node_id: str


class Story(_Model):
    id: str
    title: str
    intro: str
    characters: list[Character]
    nodes: list[Node]


class StorySummary(_Model):
    id: str
    title: str
    intro: str
