"""Obrobka audio po generacji."""
import torch


def trim_tail(wav: torch.Tensor, sr: int, trim_s: float = 0.12, fade_s: float = 0.06) -> torch.Tensor:
    """Odcina koncowke (trzask/szum po forced-EOS) i wygasza koniec.

    wav: [kanaly, probki]. Zbyt krotkie nagranie zwraca bez zmian.
    """
    trim, fade = int(trim_s * sr), int(fade_s * sr)
    if wav.shape[-1] <= trim + fade:
        return wav
    wav = wav[..., : wav.shape[-1] - trim].clone()
    wav[..., -fade:] *= torch.linspace(1.0, 0.0, fade, device=wav.device)
    return wav
