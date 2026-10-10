"""Strojenie parametrow generacji: to samo zdanie, to samo ziarno, rozne ustawienia.

Uzycie: uv run python tune.py
Wyniki: outputs/tune_<wariant>.wav
"""
import quiet  # noqa: F401  (musi byc pierwszy)
import time
from pathlib import Path

import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ROOT = Path(__file__).parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
SAMPLE = ROOT / "voices" / "adrian_neutral.wav"

device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"device: {device}")

TEXTS = [
    "Dawno temu, w mglistym Wrocławiu, żył człowiek, który słyszał rzekę.",
    "Nie wierzcie wszystkiemu, co szepczą mury starej kamienicy.",
    "Trzymajcie się mocno, bo lecimy nad dachami miasta!",
]
VARIANTS = {
    "t06_rp20_cfg03": dict(temperature=0.6, repetition_penalty=2.0, cfg_weight=0.3),
    "t06_rp20_cfg05": dict(temperature=0.6, repetition_penalty=2.0, cfg_weight=0.5),
    "t06_rp25_cfg03": dict(temperature=0.6, repetition_penalty=2.5, cfg_weight=0.3),
}

model = ChatterboxMultilingualTTS.from_pretrained(device=device)
for name, params in VARIANTS.items():
    for i, text in enumerate(TEXTS):
        torch.manual_seed(0)
        t = time.time()
        wav = model.generate(text, language_id="pl", audio_prompt_path=str(SAMPLE), **params)
        dt = time.time() - t
        path = OUT / f"tune_{name}_{i}.wav"
        ta.save(str(path), wav.cpu(), model.sr)
        print(f"{path.name}: {wav.shape[-1] / model.sr:.1f}s audio w {dt:.0f}s")
