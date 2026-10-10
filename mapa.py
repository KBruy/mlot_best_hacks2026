"""Podgląd spaceru na żywo: mała strona z mapą Google, która śledzi pozycję z gry.

Gra (w terminalu) zapisuje każdy odczyt GPS w LiveMap, a strona pod
http://127.0.0.1:PORT co chwilę pyta o /pos i przesuwa pinezkę na mapie.
Tylko biblioteka standardowa; serwer działa w osobnym wątku i słucha
wyłącznie na localhost.
"""

import json
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
               font: 16px/1.4 system-ui, sans-serif; }
  #bar { position: absolute; z-index: 2; top: 12px; left: 12px; right: 12px;
         padding: 10px 14px; border-radius: 10px; background: rgba(0,0,0,.75); }
  #bar b { color: #f5c542; }
  iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0;
           transition: opacity .4s; }
  .hidden { opacity: 0; }
</style>
</head>
<body>
<div id="bar"><b>Mostek Czarownic</b> · <span id="note">czekam na pozycję z gry…</span></div>
<iframe id="a" title="Mapa"></iframe>
<iframe id="b" title="Mapa" class="hidden"></iframe>
<script>
  // Dwie ramki na zmianę: nowa mapa ładuje się w ukrytej, a potem się ją pokazuje,
  // żeby pinezka nie migała przy każdym kroku.
  const frames = [document.getElementById("a"), document.getElementById("b")];
  let front = 0, shown = "";
  function url(lat, lon) {
    return "https://maps.google.com/maps?q=" + lat + "," + lon + "&z=19&t=k&output=embed";
  }
  async function tick() {
    try {
      const r = await fetch("/pos", {cache: "no-store"});
      const p = await r.json();
      document.getElementById("note").textContent = p.note || "";
      const key = p.lat + "," + p.lon;
      if (p.lat !== null && key !== shown) {
        shown = key;
        const back = frames[1 - front];
        back.onload = () => {
          back.classList.remove("hidden");
          frames[front].classList.add("hidden");
          front = 1 - front;
        };
        back.src = url(p.lat, p.lon);
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


class LiveMap:
    """Przechowuje ostatnią pozycję i serwuje stronę z mapą."""

    def __init__(self, port=8765):
        self._lock = threading.Lock()
        self._state = {"lat": None, "lon": None, "note": ""}
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

    def update(self, position, note=""):
        with self._lock:
            self._state = {"lat": position[0], "lon": position[1], "note": note}

    def snapshot(self):
        with self._lock:
            return dict(self._state)

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class MappedGps:
    """Przezroczysta nakładka na dostawcę GPS: każdy odczyt trafia też na mapę."""

    def __init__(self, gps, live_map, story, distance):
        self.gps, self.map, self.story, self.distance = gps, live_map, story, distance
        self.live = getattr(gps, "live", False)

    def __call__(self, target):
        position = self.gps(target)
        if position is not None:
            self.map.update(position, self.describe(position, target))
        return position

    def describe(self, position, target):
        if target is None:
            return "📍 start: " + self.story["location"]["name"]
        left = self.distance(*position, target["lat"], target["lon"])
        if left <= target["radius_m"]:
            return "📍 jesteś: " + target["label"]
        return f"🚶 idziesz: {target['label']} (jeszcze ok. {round(left)} m)"
