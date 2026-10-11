import torch

from audio import trim_tail

SR = 24000


def tone(seconds: float, level: float) -> torch.Tensor:
    t = torch.arange(int(seconds * SR)) / SR
    return level * torch.sin(2 * torch.pi * 220 * t)


def speech(seconds: float) -> torch.Tensor:
    """Ton z dolinami energii co 0,3 s, jak sylaby w mowie."""
    parts = []
    for _ in range(int(seconds / 0.3)):
        parts += [tone(0.24, 0.5), torch.zeros(int(0.06 * SR))]
    return torch.cat(parts)


def test_trailing_blips_after_speech_are_cut():
    # mowa, potem 2 s cichego szumu z krótkimi trzaskami (jak ogon generacji Chatterboxa)
    noise = 0.0005 * torch.randn(int(2.0 * SR))
    for at, blip in [(0.5, tone(0.08, 0.05)), (1.9, tone(0.04, 0.2))]:
        start = int(at * SR)
        noise[start:start + blip.numel()] += blip
    wav = torch.cat([speech(3.0), noise]).unsqueeze(0)
    out = trim_tail(wav, SR)
    assert out.shape[-1] / SR < 3.2


def test_clean_speech_keeps_its_end():
    wav = torch.cat([speech(3.0), torch.zeros(int(0.5 * SR))]).unsqueeze(0)
    out = trim_tail(wav, SR)
    assert out.shape[-1] / SR > 2.9
