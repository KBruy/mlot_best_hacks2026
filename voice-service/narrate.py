"""Generuje nagrania narracji legendy: WAV (master), MP3 dla frontu i znaczniki czasu słów (karaoke).

Źródła: skrypty `[Głos, postać] Kwestia` z pliku narracji legendy (NARRATIONS) i teksty
akapitów z legendy (`audio_url`). Wyniki:
    outputs/<id historii>/<plik>.wav                    master, PCM 16-bit 24 kHz mono
    ../frontend/public/audio/<id historii>/<plik>.mp3   MP3 CBR 64 kb/s mono
    ../frontend/public/audio/<id historii>/<plik>.json  {"words": [{text, start, end}]}

Po syntezie każdy odcinek między pauzami jest przycinany tuż za ostatnim słowem wskazanym
przez dopasowanie tekstu do nagrania: model potrafi po zdaniu dogenerować kilka sekund
szumu lub bełkotu, którego nie da się odróżnić od mowy samą głośnością.

Gotowe pliki są pomijane, więc przerwane generowanie można wznowić. Nie wymaga
uruchomionego serwisu ani klucza API (silnik działa w tym procesie) ani ffmpeg.

Użycie (z katalogu voice-service/); bez --story legenda to mostek-czarownic:
    uv run python narrate.py                  # wszystko, czego brakuje
    uv run python narrate.py --story kamienna-glowa   # inna legenda (pozostałe flagi jak niżej)
    uv run python narrate.py dom-1 bal-1      # tylko wybrane pliki
    uv run python narrate.py --force dom-1    # wygeneruj ponownie z pominięciem cache (nowe podejście)
    uv run python narrate.py --align-only     # tylko znaczniki czasu do istniejących WAV
    uv run python narrate.py --retrim dom-1   # przytnij ogony w istniejącym WAV bez generowania
    uv run python narrate.py --check          # tylko spójność skryptów z legendą
"""
import quiet  # noqa: F401  (musi byc pierwszy)

import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio as ta

from script import parse_script

ROOT = Path(__file__).parent
CONTENT = ROOT.parent / "content"
# id historii -> plik ze skryptami nagrań (bloki ### `<plik>.mp3`)
NARRATIONS = {
    "mostek-czarownic": ROOT / "NARRACJA.md",
    "kamienna-glowa": ROOT / "NARRACJA-kamienna-glowa.md",
}
LINE_PAUSE_S = 0.5  # jak w app.py (/tts/script)
MP3_LEVEL = 0.6  # libsndfile: 0.6 = CBR 64 kb/s; stały bitrate trzyma currentTime w przeglądarce
MIN_PAUSE_S = 0.2  # pauzy między zdaniami (0,25 s) i kwestiami (0,5 s) to dokładne zera
TAIL_PAD_S = 0.15  # zapas po ostatnim słowie odcinka (koniec słowa z dopasowania bywa wczesny)
LEAD_PAD_S = 0.15  # zapas przed pierwszym słowem, gdy odcinek zaczyna się od śmieci
MAX_LEAD_S = 0.5   # dłuższy wstęp przed pierwszym słowem jest przycinany
FADE_S = 0.05
MAX_GAP_S = 0.6    # dłuższa cisza między słowami w odcinku (zwykle śmieci po sklejonym zdaniu) jest skracana
GAP_PAD_S = 0.15   # zapas po obu stronach skróconej przerwy

_BLOCK = re.compile(r"^### `([^`]+)\.mp3`\s*\n+```text\n(.*?)\n```", re.M | re.S)


def words(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def story_texts(story: dict) -> dict[str, str]:
    """{nazwa pliku bez .mp3: tekst akapitu} dla wszystkich wariantów z audio_url."""
    found: dict[str, str] = {}

    def walk(value):
        if isinstance(value, dict):
            if "audio_url" in value:
                found[value["audio_url"].rsplit("/", 1)[1].removesuffix(".mp3")] = value["text"]
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)

    walk(story)
    return found


def load_story(story_id: str) -> dict:
    for path in sorted(CONTENT.glob("*.json")):
        story = json.loads(path.read_text(encoding="utf-8"))
        if story.get("id") == story_id:
            return story
    sys.exit(f"Brak historii {story_id!r} w {CONTENT}")


def load_jobs(story_id: str) -> dict[str, tuple[str, str]]:
    """Zwraca {plik: (skrypt, tekst akapitu)}; przerywa przy niespójności."""
    narration = NARRATIONS[story_id]
    texts = story_texts(load_story(story_id))
    scripts = dict(_BLOCK.findall(narration.read_text(encoding="utf-8")))
    problems = [f"brak skryptu w {narration.name}: {n}" for n in sorted(texts.keys() - scripts.keys())]
    problems += [f"skrypt bez audio_url w legendzie: {n}" for n in sorted(scripts.keys() - texts.keys())]
    for name in sorted(texts.keys() & scripts.keys()):
        spoken = " ".join(line.text for line in parse_script(scripts[name]))
        if words(spoken) != words(texts[name]):
            problems.append(f"{name}: słowa skryptu różnią się od tekstu w legendzie")
    if problems:
        sys.exit(f"Niespójność {narration.name} z legendą:\n" + "\n".join(f"- {p}" for p in problems))
    return {n: (scripts[n], texts[n]) for n in texts}


# --- synteza ------------------------------------------------------------------

def synthesize(engine, script: str, fresh: bool = False) -> torch.Tensor:
    """fresh: pomiń cache serwisu, żeby dostać nowe podejście (generacja jest losowa)."""
    pause = torch.zeros(1, int(LINE_PAUSE_S * engine.sr))
    pieces: list[torch.Tensor] = []
    for line in parse_script(script):
        if fresh:
            engine.forget(line.voice, line.character, line.text)
        pieces +=[engine.synthesize(line.voice, line.character, line.text), pause]
    return torch.cat(pieces[:-1], dim=-1)


def segments(audio: np.ndarray, sr: int) -> list[tuple[int, int]]:
    """Odcinki mowy (start, koniec) w próbkach, rozdzielone pauzami z dokładnych zer."""
    zero = np.r_[0, (audio == 0).astype(np.int8), 0]
    edges = np.diff(zero)
    pauses = [(a, b) for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1))
              if b - a >= MIN_PAUSE_S * sr]
    bounds = [0] + [v for a, b in pauses for v in (a, b)] + [len(audio)]
    return [(bounds[i], bounds[i + 1]) for i in range(0, len(bounds), 2) if bounds[i + 1] > bounds[i]]


def _close_gaps(audio: np.ndarray, sr: int, words: list[dict], start: int, end: int) -> np.ndarray:
    """Fragment audio[start:end] ze skróconymi do 2*GAP_PAD_S przerwami między słowami dłuższymi niż MAX_GAP_S."""
    fade, pad = int(FADE_S * sr), int(GAP_PAD_S * sr)
    parts, cursor = [], start
    for prev, nxt in zip(words, words[1:]):
        gap_start, gap_end = int(prev["end"] * sr) + pad, int(nxt["start"] * sr) - pad
        if (nxt["start"] - prev["end"]) <= MAX_GAP_S or gap_end <= gap_start:
            continue
        part = audio[cursor:gap_start].copy()
        part[-fade:] *= np.linspace(1.0, 0.0, min(fade, len(part)), dtype=part.dtype)
        parts.append(part)
        cursor = gap_end
    part = audio[cursor:end].copy()
    if parts:
        part[:fade] *= np.linspace(0.0, 1.0, min(fade, len(part)), dtype=part.dtype)
    parts.append(part)
    return np.concatenate(parts)


def cut_tails(audio: np.ndarray, sr: int, words: list[dict]) -> tuple[np.ndarray, float]:
    """Przycina każdy odcinek do jego słów (z zapasem), skraca długie przerwy między słowami,
    odcinki bez słów usuwa.

    Przed każdym zachowanym odcinkiem zostaje jego pierwotna pauza. Zwraca (audio, usunięte sekundy).
    """
    fade = int(FADE_S * sr)
    pieces: list[np.ndarray] = []
    previous_end = 0
    for start, end in segments(audio, sr):
        pause = start - previous_end
        previous_end = end
        inside = [w for w in words if start <= w["start"] * sr < end and w["end"] > w["start"]]
        if not inside:
            continue
        first, last = int(inside[0]["start"] * sr), int(inside[-1]["end"] * sr)
        new_start = max(start, first - int(LEAD_PAD_S * sr)) if first - start > MAX_LEAD_S * sr else start
        new_end = min(end, last + int(TAIL_PAD_S * sr))
        piece = _close_gaps(audio, sr, inside, new_start, new_end)
        n = min(fade, len(piece))
        if new_end < end:
            piece[-n:] *= np.linspace(1.0, 0.0, n, dtype=piece.dtype)
        if new_start > start:
            piece[:n] *= np.linspace(0.0, 1.0, n, dtype=piece.dtype)
        if pieces:
            pieces.append(np.zeros(pause, dtype=audio.dtype))
        pieces.append(piece)
    if not pieces:
        return audio, 0.0
    result = np.concatenate(pieces)
    return result, (len(audio) - len(result)) / sr


def read_mono(path: Path) -> tuple[np.ndarray, int]:
    audio, sr = sf.read(path, dtype="float32", always_2d=True)
    return audio.mean(axis=1), sr


def save_wav(path: Path, audio: np.ndarray, sr: int) -> None:
    sf.write(path, audio, sr, subtype="PCM_16")


def save_mp3(wav_path: Path, mp3_path: Path) -> None:
    audio, sr = sf.read(wav_path, dtype="float32")
    sf.write(mp3_path, audio, sr, format="MP3", bitrate_mode="CONSTANT", compression_level=MP3_LEVEL)


# --- znaczniki czasu słów (forced alignment) -----------------------------------

class Aligner:
    """Dopasowuje znany tekst do nagrania modelem MMS_FA (wav2vec2, wielojęzyczny, wbudowany w torchaudio).

    Model zna tylko małe litery łacińskie, więc słowa są sprowadzane do ASCII (ą→a, ł→l).
    Tokeny bez liter (np. myślnik dialogowy) dostają czas następnego słowa.
    """

    def __init__(self) -> None:
        bundle = ta.pipelines.MMS_FA
        self.sr = bundle.sample_rate
        self.model = bundle.get_model(with_star=False).eval()
        self.tokenizer = bundle.get_tokenizer()
        self.align = bundle.get_aligner()
        self.alphabet = set(bundle.get_dict()) - {"-", "*"}

    def _romanize(self, token: str) -> str:
        token = token.lower().replace("ł", "l")
        token = unicodedata.normalize("NFKD", token).encode("ascii", "ignore").decode()
        return "".join(c for c in token if c in self.alphabet)

    def __call__(self, audio: np.ndarray, sr: int, text: str) -> list[dict]:
        waveform = ta.functional.resample(torch.from_numpy(audio).unsqueeze(0), sr, self.sr)
        tokens = text.split(" ")  # tak samo jak NarrativeKaraoke we froncie
        romanized = [self._romanize(t) for t in tokens]
        spoken = [r for r in romanized if r]
        with torch.inference_mode():
            emission, _ = self.model(waveform)
        spans = self.align(emission[0], self.tokenizer(spoken))
        seconds_per_frame = waveform.size(1) / emission.size(1) / self.sr
        times = iter([(s[0].start * seconds_per_frame, s[-1].end * seconds_per_frame) for s in spans])
        result: list[dict] = []
        pending: list[str] = []  # tokeny bez liter czekają na następne słowo
        for token, roman in zip(tokens, romanized):
            if not roman:
                pending.append(token)
                continue
            start, end = next(times)
            result += [{"text": t, "start": round(start, 2), "end": round(start, 2)} for t in pending]
            result.append({"text": token, "start": round(start, 2), "end": round(end, 2)})
            pending = []
        last = result[-1]["end"] if result else 0.0
        result += [{"text": t, "start": last, "end": last} for t in pending]
        return result


# --- program ------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Nagrania narracji legendy (WAV, MP3, znaczniki karaoke).")
    parser.add_argument("names", nargs="*", help="nazwy plików bez .mp3 (domyślnie wszystkie)")
    parser.add_argument("--story", default="mostek-czarownic", choices=sorted(NARRATIONS), help="id legendy")
    parser.add_argument("--force", action="store_true",
                        help="generuj ponownie z pominięciem cache, nawet gdy pliki istnieją")
    parser.add_argument("--retrim", action="store_true", help="przytnij ogony w istniejących WAV (bez generowania)")
    parser.add_argument("--align-only", action="store_true", help="tylko znaczniki czasu do istniejących WAV")
    parser.add_argument("--no-align", action="store_true", help="bez plików .json ze znacznikami czasu")
    parser.add_argument("--check", action="store_true", help="tylko sprawdź spójność skryptów z legendą")
    args = parser.parse_args(argv)

    story_id = args.story
    jobs = load_jobs(story_id)
    if args.check:
        print(f"OK {story_id}: {len(jobs)} plików, skrypty zgodne z legendą.")
        return
    unknown = set(args.names) - jobs.keys()
    if unknown:
        sys.exit(f"Nieznane pliki: {', '.join(sorted(unknown))}")
    names = args.names or list(jobs)

    wav_dir = ROOT / "outputs" / story_id
    web_dir = ROOT.parent / "frontend" / "public" / "audio" / story_id
    wav_dir.mkdir(parents=True, exist_ok=True)
    web_dir.mkdir(parents=True, exist_ok=True)

    engine = aligner = None
    started = time.monotonic()
    for i, name in enumerate(names, 1):
        script, text = jobs[name]
        wav, mp3, marks = wav_dir / f"{name}.wav", web_dir / f"{name}.mp3", web_dir / f"{name}.json"
        generate = not (args.align_only or args.retrim) and (args.force or not wav.exists())
        if not generate and not wav.exists():
            print(f"[{i}/{len(names)}] {name}: brak WAV, pomijam", flush=True)
            continue
        changed = generate or args.retrim
        if aligner is None and (changed or not args.no_align):
            print("Ładowanie modelu dopasowania (MMS_FA)...", flush=True)
            aligner = Aligner()
        done = []
        if generate:
            if engine is None:
                print("Ładowanie modelu TTS...", flush=True)
                from engine import Engine
                engine = Engine()
            audio, sr = synthesize(engine, script, fresh=args.force)[0].numpy(), engine.sr
            done.append("wav")
        else:
            audio, sr = read_mono(wav)
        if changed:
            audio, removed = cut_tails(audio, sr, aligner(audio, sr, text))
            save_wav(wav, audio, sr)
            done.append(f"przycięto {removed:.1f} s" if removed else "bez przycinania")
        if changed or not args.align_only and not mp3.exists():
            save_mp3(wav, mp3)
            done.append("mp3")
        if not args.no_align and (changed or args.align_only or not marks.exists()):
            marks.write_text(json.dumps({"words": aligner(audio, sr, text)}, ensure_ascii=False), encoding="utf-8")
            done.append("json")
        elapsed = time.monotonic() - started
        print(f"[{i}/{len(names)}] {name}: {', '.join(done) or 'gotowe'}"
              f" ({len(audio) / sr:.1f} s audio, {elapsed:.0f} s od startu)", flush=True)


if __name__ == "__main__":
    main()
