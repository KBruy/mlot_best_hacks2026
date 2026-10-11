# Street View: zły początek i anchor pointy

Dla: Krystian. Referencja, która działa: `terminal-game/mapa.py` (`MappedGps.pick_view`, `ordered_anchors`).

## Dlaczego nie pokazujemy Street View w punkcie z GPS

Osadzenie bez klucza API (`cbll=lat,lon&output=svembed`) bierze **najbliższą panoramę do podanego punktu, dowolną**. Może to być zdjęcie sferyczne użytkownika albo wnętrze, a nie zdjęcie z ulicy.

Pod wieżami Marii Magdaleny najbliżej jest zdjęcie sferyczne **z samego mostka** (`streetview.finale`: `51.109652, 17.034396`). `demo_start` i przystanek `wieze` (`51.109666, 17.034503`) leżą od niego ok. 8 m. Kiedy podajemy surowy GPS albo `demo_start`, dostajemy widok z powietrza zamiast z ulicy.

Dlatego `streetview.anchors` to lista **sprawdzonych panoram z ulicy na trasie**. Kamerę stawiamy zawsze na anchorze (albo na ustalonym ujęciu przystanku z `streetview.stops`), nigdy na surowym GPS.

## Co jest teraz źle we froncie

1. **Start na mostku.** `frontend/src/screens/SceneScreen.tsx:48` i `:61`: sceny bez `before` dostają w fallbacku `streetview.finale`, czyli zdjęcie z mostka. Dotyczy to sceny startowej i wszystkich scen przed pierwszym przystankiem.
2. **Spacer demo po całej trasie.** `SceneScreen.tsx:23` i `:50`: `walkFrame` iteruje po **wszystkich** anchorach (14). Droga do pierwszego przystanku (`wieze`) idzie więc aż na Rynek i wraca, a droga na Rynek startuje od początku trasy. Heading jest zawsze na przystanek, a nie wzdłuż drogi.
3. **Sceny między przystankami też na mostku.** Po dojściu do przystanku następne sceny bez `before` znowu wpadają w fallback `finale`.
4. `LocationGate.tsx` (tryb GPS): najbliższy anchor szuka po całej liście, bez ograniczenia do bieżącego odcinka. Przy trasie, która wraca tą samą ulicą (`wieze` → `rynek`), może pokazać widok z poprzedniego odcinka.

## Jak ma działać (jak w terminal-game)

| Moment | Ujęcie |
|---|---|
| Start i sceny przed 1. przystankiem | anchor najbliższy pozycji (GPS albo `demo_start`), `heading` = azymut na `location.center`, `pitch` 0 |
| Droga do przystanku | najbliższy anchor (do 35 m) **z bieżącego odcinka, tylko do przodu**; `heading` na następny anchor, a na ostatnim na przystanek |
| Na przystanku i w scenach po nim (bez nowego `before`) | `streetview.stops[ostatni przystanek]`, czyli ujęcie z JSON-a |
| Finał (`EndingFlow`, krok `finale`) | `streetview.finale`, mostek; **tylko tutaj** |

Kolejność anchorów: `ordered_anchors()` rzutuje je na trasę (`route.start` → `legs[...]` → przystanki). Odcinek do przystanku N zaczyna się od anchora najbliższego przystankowi N-1. Do „ostatniego przystanku” front potrzebuje pola w stanie (np. `lastStop`, ustawianego przy `ADVANCE_SCENE`, gdy scena ma `before`).

## Wartości kontrolne (Mostek Czarownic, z `mapa.py`)

- Start z `demo_start`: `51.109593, 17.034374`, heading **98**, pitch 0, czyli z ulicy na kościół.
- Droga do `wieze`: `51.10934, 17.034651` → h289; `51.109475, 17.034324` → h16.
- Droga na `rynek`: `51.109593, 17.034374` → h242; `51.109475, 17.034024` → h291; `51.109551, 17.033702` → h291; `51.109626, 17.03338` → h287; `51.109626, 17.032965` → h225.

## Przy okazji

- `streetview.stops.wieze.heading`: w referencji `terminal-game/story.json` jest **85** (na kościół), w `content/legenda-czarownica.json` jest **265** (tyłem). W `cbp` ujemny pitch patrzy w górę, więc `-60` jest OK.
- Żeby sprawdzić zmianę stopni, trzeba ponownie zaimportować treść do bazy: `uv run --env-file .env python -m app.import_story` w `backend/`, potem odświeżyć przeglądarkę. Restart API nie jest potrzebny.
