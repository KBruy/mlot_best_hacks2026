"""Spike jakosciowy: ten sam glos, rozne postacie, polski tekst.

Uzycie: uv run python spike.py [--quick]
  --quick  generuje tylko jedno krotkie zdanie (test, ze pipeline dziala)
"""
import quiet  # noqa: F401  (musi byc pierwszy)
import sys
import time
from pathlib import Path

import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ROOT = Path(__file__).parent
VOICES = ROOT / "voices"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"
print(f"device: {device}")

# Wariant A: parametry modelu na jednej probce neutralnej.
# Wariant B: osobna probka w danej manierze (jesli plik istnieje).
# Domyslne parametry wybrane na slух w tune.py (pelne zdanie, bez ucinania).
DEFAULTS = dict(temperature=0.6, repetition_penalty=1.3, cfg_weight=0.3)
CHARACTERS = {
    "starzec": dict(exaggeration=0.3),
    "wiedzma": dict(exaggeration=0.8, cfg_weight=0.5),  # nadpisuje domyslne
}
TEXTS = [
    "Dawno temu, w mglistym Wrocławiu, żył człowiek, który słyszał rzekę.",
    "Nie wierzcie wszystkiemu, co szepczą mury starej kamienicy.",
    "Trzymajcie się mocno, bo lecimy nad dachami miasta!",
]
if "--quick" in sys.argv:
    TEXTS = TEXTS[:1]

t0 = time.time()
model = ChatterboxMultilingualTTS.from_pretrained(device=device)
print(f"model zaladowany w {time.time() - t0:.1f}s")


def generate(tag: str, sample: Path, params: dict):
    for i, text in enumerate(TEXTS):
        t = time.time()
        wav = model.generate(text, language_id="pl", audio_prompt_path=str(sample), **{**DEFAULTS, **params})
        dt = time.time() - t
        dur = wav.shape[-1] / model.sr
        path = OUT / f"{tag}_{i}.wav"
        ta.save(str(path), wav.cpu(), model.sr)
        print(f"{path.name}: {dur:.1f}s audio w {dt:.1f}s (x{dt / dur:.1f} czasu rzeczywistego)")


neutral = VOICES / "adrian_neutral.wav"
for name, params in CHARACTERS.items():
    generate(f"A_{name}", neutral, params)  # parametry na probce neutralnej

for name, params in CHARACTERS.items():
    sample = VOICES / f"adrian_{name}.wav"
    if sample.exists():
        generate(f"B_{name}", sample, params)  # probka w manierze
