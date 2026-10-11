"""Modele historii (jedno źródło prawdy dla importera, walidatora i API).

Format pochodzi z prototypu terminal-game (opis pól: terminal-game/docs/FORMAT_HISTORII.md),
uzupełniony o `id` i `title` potrzebne bazie i API. Docstringi klas i opisy pól trafiają
do schematów OpenAPI (/docs).

Teksty z warunkami: akapit sceny, tekst opcji, akapit skutku i zakończenia może być
napisem, jednym wariantem {"if": {pole: [wartości]}, "text": ...} albo listą wariantów
(wygrywa pierwszy pasujący; gdy nic nie pasuje, akapit się pomija). Warunek pasuje, gdy
każde wymienione pole stanu ma jedną z podanych wartości; brak `if` pasuje zawsze.

Nagrania: każdy czytany akapit (i każdy jego wariant) ma własne `audio_url`. Akapit bez
warunku z nagraniem zapisujemy jako wariant bez `if`: {"text": ..., "audio_url": ...}.
Teksty opcji nie są czytane.

Grafiki: scena i zakończenie mają tło `bg`, a czytany akapit (wariant) może zmienić postacie
w dwóch miejscach sceny (`chars.left`, `chars.right`). Pliki leżą w frontend/public/art/<id historii>/.
"""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


Condition = dict[str, list[str]]
LatLon = Annotated[list[float], Field(min_length=2, max_length=2, description="[lat, lon]")]


class Chars(_Model):
    """Postacie na scenie od tego akapitu. Brak klucza = postać w tym miejscu bez zmian,
    `null` = postać schodzi. Każdy ekran (scena, skutek, zakończenie) zaczyna bez postaci."""

    left: str | None = Field(None, description="Gracz: /art/<id historii>/<plik>.png.")
    right: str | None = Field(None, description="Rozmówca: /art/<id historii>/<plik>.png.")


class Variant(_Model):
    """Wariant tekstu pokazywany, gdy warunek `if` pasuje do stanu gry."""

    if_: Condition = Field(
        default_factory=dict,
        alias="if",
        description="{pole stanu: [dozwolone wartości]}; wszystkie pola muszą pasować. Brak = zawsze.",
    )
    text: str
    audio_url: str | None = Field(
        None,
        description="Nagranie tego akapitu lub wariantu: MP3 serwowany statycznie przez frontend,"
        " /audio/<id historii>/<plik>.mp3. Obok może leżeć <plik>.json ze znacznikami czasu słów (karaoke).",
    )
    chars: Chars | None = Field(None, description="Zmiana postaci na scenie od tego akapitu.")


Text = str | Variant | list[Variant]
Paragraphs = Annotated[
    list[Text], Field(description="Akapity; każdy to napis albo warianty z warunkami.")
]


class Viewpoint(_Model):
    """Strefa widokowa; jej `id` to wartość pola stanu `widok`, ustawiana przez frontend z GPS."""

    id: str
    label: str
    lat: float
    lon: float
    radius_m: int


class Location(_Model):
    """Miejsce legendy. Gra odblokowuje się w promieniu `unlock_radius_m` od `center`."""

    name: str
    center: LatLon
    unlock_radius_m: int
    default_view: str = Field(description="Wartość `widok`, gdy gracz nie stoi w żadnej strefie.")
    viewpoints: list[Viewpoint]


class Stop(_Model):
    """Przystanek spaceru; scena z `before` czeka, aż gracz do niego dojdzie."""

    label: str
    lat: float
    lon: float
    radius_m: int
    walk: str = Field(description="Polecenie, dokąd iść.")
    arrive: str = Field(description="Tekst po dotarciu.")


class Route(_Model):
    """Trasa piesza: punkt startu i odcinki (lista punktów) do każdego przystanku."""

    start: LatLon
    legs: dict[str, list[LatLon]] = Field(description="Klucz to id przystanku.")


class StreetViewShot(_Model):
    lat: float
    lon: float
    heading: int = Field(description="0 = północ.")
    pitch: int = Field(description="Ujemny = w górę.")
    note: str | None = None


class StreetView(_Model):
    """Panoramy Google Street View: sprawdzone punkty trasy i ujęcia przystanków."""

    anchors: list[LatLon]
    stops: dict[str, StreetViewShot] = Field(description="Klucz to id przystanku.")
    finale: StreetViewShot


class SimPoint(_Model):
    label: str
    lat: float
    lon: float


class Intro(_Model):
    title: str
    paragraphs: Paragraphs


class Option(_Model):
    """Opcja w scenie. Po wyborze: zapisz `set` w stanie, pokaż `result`, przejdź do `next`."""

    text: Text
    legend: bool = Field(description="Czy wybór zgadza się z legendą (+1 do wyniku).")
    set: dict[str, str] = Field(description="Pola stanu ustawiane po wyborze.")
    next: str | None = Field(
        description="Id następnej sceny albo null, gdy to ostatnia decyzja (zakończenie wybiera `ending_by`)."
    )
    result: Paragraphs


class Scene(_Model):
    """Scena decyzyjna z 2 albo 3 opcjami."""

    title: str = Field(description="Nagłówek decyzji i nazwa w zestawieniu na końcu.")
    scene: Paragraphs
    options: list[Option]
    fact: str = Field(description="Zdanie z prawdziwej legendy do zestawienia na końcu.")
    act: str | None = Field(None, description="Baner fazy, np. „FAZA 2/4: WYROK”.")
    before: str | None = Field(None, description="Id przystanku, do którego gracz dochodzi przed sceną.")
    keypoint: str | None = Field(None, description="Oznaczenie punktu kluczowego fabuły.")
    art: list[str] | None = Field(None, description="Linie grafiki ASCII.")
    bg: str | None = Field(None, description="Tło sceny i jej skutków: /art/<id historii>/<plik>.png.")


class Ending(_Model):
    title: str
    paragraphs: Paragraphs
    bg: str | None = Field(None, description="Tło zakończenia: /art/<id historii>/<plik>.png.")


class Finale(_Model):
    """Tekst po zakończeniu (np. widok z miejsca legendy)."""

    act: str | None = None
    paragraphs: Paragraphs


class Reveal(_Model):
    """Odsłonięcie prawdziwych bohaterów legendy."""

    title: str
    paragraphs: Paragraphs


class Rank(_Model):
    """Ranga za wynik (liczbę wyborów zgodnych z legendą): najwyższa z `min` <= wynik."""

    min: int
    title: str
    text: str


class Story(_Model):
    """Pełna historia: frontend pobiera ją raz i wykonuje wszystkie przejścia lokalnie."""

    id: str = Field(description="Stałe id historii; jego zmiana tworzy w bazie nową historię.")
    title: str
    location: Location
    stops: dict[str, Stop] = Field(description="Przystanki spaceru; klucz to id przystanku.")
    route: Route | None = None
    streetview: StreetView | None = None
    test_points: list[SimPoint] | None = Field(None, description="Tylko do symulacji GPS.")
    demo_start: LatLon | None = Field(None, description="Tylko do symulacji GPS.")
    state: dict[str, list[str]] = Field(
        description="Pola stanu gry i ich dozwolone wartości. Pole `widok` ustawia frontend z GPS."
    )
    intro: Intro
    start: str = Field(description="Id pierwszej sceny.")
    scenes: dict[str, Scene] = Field(
        description="Graf scen; klucz to id sceny. Każda ścieżka od `start` ma 6 decyzji."
    )
    ending_by: list[str] = Field(description="Pola stanu wybierające zakończenie.")
    endings: dict[str, Ending] = Field(
        description="Klucz to wartości pól z `ending_by` połączone znakiem |."
    )
    finale: Finale
    reveal: Reveal
    ranks: list[Rank]
    heritage: Text
    look_up: Text


class LocationSummary(_Model):
    """Miejsce legendy na liście historii (bez punktów widokowych)."""

    name: str
    center: LatLon


class StorySummary(_Model):
    """Pozycja listy historii (bez grafu)."""

    id: str
    title: str
    location: LocationSummary
    intro: Intro
