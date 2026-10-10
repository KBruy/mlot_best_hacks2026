"""Obrobka audio po generacji."""
import torch

FRAME_S = 0.02


def _frame_db(x: torch.Tensor, sr: int) -> torch.Tensor:
    hop = int(FRAME_S * sr)
    n = x.shape[-1] // hop
    rms = x[: n * hop].reshape(n, hop).pow(2).mean(1).sqrt()
    return 20 * torch.log10(rms + 1e-6)


def trim_tail(
    wav: torch.Tensor,
    sr: int,
    min_noise_s: float = 0.8,
    flat_db: float = 6.0,
    fade_s: float = 0.06,
    pad_s: float = 0.08,
) -> torch.Tensor:
    """Usuwa z konca nagrania szum po wypowiedzi i cisze, wygasza koniec.

    Chatterbox po wymuszonym EOS potrafi dolozyc >1 s rownego szumu o glosnosci mowy.
    Mowa ma gleboke doliny energii co kilkaset ms, szum - plaski poziom. Jesli po
    ostatniej dolinie jest ogon dluzszy niz min_noise_s i prawie bez modulacji
    (odchylenie std < flat_db), jest odcinany. wav: [kanaly, probki].
    """
    x = wav[0]
    db = _frame_db(x, sr)
    if db.numel() < 10:
        return wav
    valley = db < db.max() - 30
    end = db.numel()

    # poczatek ogona = pierwsza ramka po ostatniej dolinie (jesli doliny sa)
    non_valley = (~valley).nonzero().flatten()
    voiced_end = int(non_valley[-1]) + 1 if non_valley.numel() else end  # po ostatniej glosnej ramce
    last_valley_end = None
    v = valley.nonzero().flatten()
    if v.numel():
        # koniec ostatniego ciaglego ciagu ramek-dolin, ktory nie siega konca nagrania
        runs_end = [int(i) + 1 for i in v if i + 1 < end and not valley[i + 1]]
        last_valley_end = runs_end[-1] if runs_end else None
    if last_valley_end is not None:
        tail = db[last_valley_end:]
        if tail.numel() * FRAME_S >= min_noise_s and tail.std() < flat_db:
            voiced_end = last_valley_end  # szum - odetnij; ciche ramki wyzej obetnie voiced_end nizej

    # zrzuc ciche ramki tuz przed punktem ciecia (koniec ostatniej glosnej ramki)
    cut = voiced_end
    while cut > 0 and valley[cut - 1]:
        cut -= 1
    cut = min(end, cut + int(pad_s / FRAME_S)) * int(FRAME_S * sr)
    out = wav[..., :cut].clone()
    fade = min(int(fade_s * sr), out.shape[-1])
    out[..., -fade:] *= torch.linspace(1.0, 0.0, fade, device=out.device)
    return out
