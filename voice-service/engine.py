"""Silnik TTS: Chatterbox Multilingual + profile postaci + cache na dysku."""
import quiet  # noqa: F401  (musi byc pierwszy)

import hashlib
import json
import os
import threading
from pathlib import Path

import torch
import torchaudio as ta
import yaml
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

from audio import trim_tail
from script import normalize, split_sentences

ROOT = Path(__file__).parent
VOICES_DIR = ROOT / "voices"
CACHE_DIR = ROOT / "cache"
ALLOWED_PARAMS = {"exaggeration", "cfg_weight", "temperature", "repetition_penalty"}
# Dobrane na sluch (spike/tune). repetition_penalty < ~2 powoduje ucinanie audio.
DEFAULTS = dict(temperature=0.6, repetition_penalty=2.5, cfg_weight=0.3)
SENTENCE_PAUSE_S = 0.25


class NotFound(Exception):
    """Nieznany głos lub postać."""


def pick_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class Engine:
    def __init__(self) -> None:
        self.device = pick_device()
        self.characters = self._load_characters()
        self.model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
        self.sr = self.model.sr
        self._lock = threading.Lock()  # model nie jest wielowatkowy
        CACHE_DIR.mkdir(exist_ok=True)

    @staticmethod
    def _load_characters() -> dict[str, dict]:
        chars = yaml.safe_load((ROOT / "characters.yaml").read_text(encoding="utf-8")) or {}
        for name, params in chars.items():
            params = params or {}
            unknown = set(params) - ALLOWED_PARAMS
            if unknown:
                raise ValueError(f"characters.yaml: postac '{name}' ma nieznane parametry {sorted(unknown)}")
            chars[name] = params
        return chars

    def voices(self) -> list[str]:
        return sorted(p.name.removesuffix("_neutral.wav") for p in VOICES_DIR.glob("*_neutral.wav"))

    def _sample(self, voice: str, character: str) -> Path:
        voice, character = normalize(voice), normalize(character)
        if voice not in self.voices():
            raise NotFound(f"Nieznany głos '{voice}'. Dostępne: {', '.join(self.voices()) or '(brak)'}.")
        if character not in self.characters:
            raise NotFound(f"Nieznana postać '{character}'. Dostępne: {', '.join(self.characters)}.")
        styled = VOICES_DIR / f"{voice}_{character}.wav"
        return styled if styled.exists() else VOICES_DIR / f"{voice}_neutral.wav"

    def _cache_path(self, sample: Path, character: str, text: str) -> Path:
        params = {**DEFAULTS, **self.characters[character]}
        stat = sample.stat()  # nowa probka glosu uniewaznia cache
        raw = json.dumps([sample.name, stat.st_mtime_ns, stat.st_size, params, text], sort_keys=True)
        return CACHE_DIR / (hashlib.sha256(raw.encode("utf-8")).hexdigest() + ".wav")

    def synthesize(self, voice: str, character: str, text: str) -> torch.Tensor:
        """Zwraca audio [1, probki] (CPU, self.sr). Wyniki sa cache'owane na dysku."""
        sample = self._sample(voice, character)
        character = normalize(character)
        cached = self._cache_path(sample, character, text)
        if cached.exists():
            return ta.load(str(cached))[0]
        with self._lock:
            if cached.exists():  # ktos inny wygenerowal, gdy czekalismy
                return ta.load(str(cached))[0]
            params = {**DEFAULTS, **self.characters[character]}
            pause = torch.zeros(1, int(SENTENCE_PAUSE_S * self.sr))
            pieces: list[torch.Tensor] = []
            for chunk in split_sentences(text):
                wav = self.model.generate(chunk, language_id="pl", audio_prompt_path=str(sample), **params)
                pieces += [trim_tail(wav.cpu(), self.sr), pause]
            audio = torch.cat(pieces[:-1], dim=-1)
            tmp = cached.with_suffix(".tmp.wav")
            ta.save(str(tmp), audio, self.sr)
            os.replace(tmp, cached)
            return audio
