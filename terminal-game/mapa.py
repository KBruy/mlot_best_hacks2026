"""Podgląd spaceru na żywo: Street View i mała mapa Google, które śledzą pozycję z gry.

Gra (w terminalu) zapisuje każdy odczyt GPS w LiveMap, a strona pod
http://127.0.0.1:PORT co chwilę pyta o /pos i przestawia widok.
Street View jest osadzony bez klucza API, więc sam bierze najbliższą panoramę;
dlatego gra pokazuje tylko sprawdzone panoramy z listy story.json["streetview"].
Tylko biblioteka standardowa; serwer działa w osobnym wątku i słucha
wyłącznie na localhost.
"""

import json
import math
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mostek Czarownic: spacer na żywo</title>
<style>
  html, body { margin: 0; height: 100%; background: #111; color: #eee;
               font: 16px/1.4 system-ui, sans-serif; overflow: hidden; }
  #bar { position: absolute; z-index: 3; top: 12px; left: 12px; right: 12px;
         padding: 10px 14px; border-radius: 10px; background: rgba(0,0,0,.75); }
  #bar b { color: #f5c542; }
  #title { color: #9fd3ff; }
  .view { position: absolute; inset: 0; width: 100%; height: 100%; border: 0;
          transition: opacity .5s; }
  .hidden { opacity: 0; pointer-events: none; }
  #mini { position: absolute; z-index: 2; right: 12px; bottom: 12px;
          width: 260px; height: 190px; border: 2px solid #f5c542; border-radius: 10px;
          overflow: hidden; background: #222; }
  #mini iframe { width: 100%; height: 100%; border: 0; }
  @media (max-width: 600px) { #mini { width: 150px; height: 120px; } }
</style>
</head>
<body>
<div id="bar"><b>Mostek Czarownic</b> · <span id="title"></span> <span id="note">czekam na pozycję z gry…</span></div>
<iframe id="a" class="view" title="Street View" allowfullscreen></iframe>
<iframe id="b" class="view hidden" title="Street View" allowfullscreen></iframe>
<div id="mini"><iframe id="map" title="Mapa"></iframe></div>
<script>
  // Dwie ramki Street View na zmianę: nowa panorama ładuje się w ukrytej,
  // a potem się ją pokazuje, żeby obraz nie migał przy każdym kroku.
  const frames = [document.getElementById("a"), document.getElementById("b")];
  let front = 0, shownView = "", shownMap = "";
  function svUrl(v) {
    return "https://maps.google.com/maps?layer=c&cbll=" + v.lat + "," + v.lon +
           "&cbp=12," + v.heading + ",0,0," + v.pitch + "&output=svembed";
  }
  function mapUrl(lat, lon) {
    return "https://maps.google.com/maps?q=" + lat + "," + lon + "&z=18&t=k&output=embed";
  }
  function show(url) {
    const back = frames[1 - front];
    back.onload = () => {
      back.classList.remove("hidden");
      frames[front].classList.add("hidden");
      front = 1 - front;
    };
    back.src = url;
  }
  async function tick() {
    try {
      const r = await fetch("/pos", {cache: "no-store"});
      const p = await r.json();
      document.getElementById("note").textContent = p.note || "";
      document.getElementById("title").textContent = p.title ? p.title + " ·" : "";
      if (p.lat !== null) {
        const mapKey = p.lat + "," + p.lon;
        if (mapKey !== shownMap) {
          shownMap = mapKey;
          document.getElementById("map").src = mapUrl(p.lat, p.lon);
        }
        const view = p.view || {lat: p.lat, lon: p.lon, heading: 0, pitch: 0};
        const viewKey = [view.lat, view.lon, view.heading, view.pitch].join(",");
        if (viewKey !== shownView) {
          shownView = viewKey;
          show(svUrl(view));
        }
      }
    } catch (e) {
      document.getElementById("note").textContent = "gra nie odpowiada (zakończona?)";
    }
    setTimeout(tick, 400);
  }
  tick();
</script>
</body>
</html>
"""


def bearing_deg(lat1, lon1, lat2, lon2):
    """Kierunek z punktu 1 do punktu 2 w stopniach (0 = północ, 90 = wschód)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return round(math.degrees(math.atan2(x, y))) % 360


class LiveMap:
    """Przechowuje ostatnią pozycję i widok, i serwuje stronę ze Street View."""

    def __init__(self, port=8765):
        self._lock = threading.Lock()
        self._state = {"lat": None, "lon": None, "note": "", "title": "", "view": None}
        live = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith("/pos"):
                    body, kind = json.dumps(live.snapshot()).encode(), "application/json"
                elif self.path in ("/", "/index.html"):
                    body, kind = PAGE.encode(), "text/html; charset=utf-8"
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", kind)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):  # nie zaśmiecaj terminala z grą
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def update(self, position=None, note=None, view=None, title=None):
        """Zmienia tylko podane pola; reszta zostaje jak była."""
        with self._lock:
            if position is not None:
                self._state["lat"], self._state["lon"] = position
            if note is not None:
                self._state["note"] = note
            if view is not None:
                self._state["view"] = view
            if title is not None:
                self._state["title"] = title

    def snapshot(self):
        with self._lock:
            return json.loads(json.dumps(self._state))

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class MappedGps:
    """Przezroczysta nakładka na dostawcę GPS: każdy odczyt trafia też do Street View.

    Na przystanku pokazuje ustalone ujęcie z story.json, w drodze najbliższą
    sprawdzoną panoramę zwróconą w kierunku marszu. notify() odbiera zdarzenia gry
    (nowa scena, finał) i np. przełącza widok na panoramę z mostka.
    """

    ANCHOR_RANGE_M = 35  # dalej od sprawdzonej panoramy zostaje poprzedni widok

    def __init__(self, gps, live_map, story, distance):
        self.gps, self.map, self.story, self.distance = gps, live_map, story, distance
        self.live = getattr(gps, "live", False)
        self.sv = story.get("streetview", {})
        self.last = None
        self.view = None

    def __call__(self, target):
        position = self.gps(target)
        if position is not None:
            self.view = self.pick_view(position, target) or self.view
            self.map.update(position, self.describe(position, target), self.view)
            self.last = position
        return position

    def notify(self, event, data):
        if event == "scene":
            self.map.update(title=data.get("act") or data["title"])
        elif event == "finale" and "finale" in self.sv:
            finale = self.sv["finale"]
            self.view = {k: finale[k] for k in ("lat", "lon", "heading", "pitch")}
            self.map.update(note=finale["note"], view=self.view, title=data.get("act", ""))

    def stop_name(self, target):
        return next((n for n, s in self.story["stops"].items() if s is target), None)

    def pick_view(self, position, target):
        if target is not None:
            left = self.distance(*position, target["lat"], target["lon"])
            fixed = self.sv.get("stops", {}).get(self.stop_name(target))
            if left <= target["radius_m"] and fixed:
                return dict(fixed)
        anchors = self.sv.get("anchors", [])
        if not anchors:
            return None
        anchor = min(anchors, key=lambda a: self.distance(*position, *a))
        if self.distance(*position, *anchor) > self.ANCHOR_RANGE_M:
            return None
        if target is None:  # start: patrz na kościół
            heading = bearing_deg(*anchor, *self.story["location"]["center"])
        elif self.last and self.distance(*self.last, *position) > 2:  # patrz tam, dokąd idziesz
            heading = bearing_deg(*self.last, *position)
        else:
            heading = bearing_deg(*anchor, target["lat"], target["lon"])
        return {"lat": anchor[0], "lon": anchor[1], "heading": heading, "pitch": 0}

    def describe(self, position, target):
        if target is None:
            return "📍 start: " + self.story["location"]["name"]
        left = self.distance(*position, target["lat"], target["lon"])
        if left <= target["radius_m"]:
            return "📍 jesteś: " + target["label"]
        return f"🚶 idziesz: {target['label']} (jeszcze ok. {round(left)} m)"
