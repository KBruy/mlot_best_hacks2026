"""Obrobka audio po generacji."""
import torch

FRAME_S = 0.02


def _frame_db(x: torch.Tensor, sr: int) -> torch.Tensor:
    hop = int(FRAME_S * sr)
    n = x.shape[-1] // hop
    rms = x[: n * hop].reshape(n, hop).pow(2).mean(1).sqrt()
    return 20 * torch.log10(rms + 1e-6)


def _speech_end(valley: torch.Tensor, max_blip_s: float = 0.12, min_gap_s: float = 0.3) -> int:
    """Ramka konca mowy z pominieciem koncowych trzaskow.

    Po wypowiedzi model potrafi wygenerowac cichy szum z krotkimi trzaskami (pojedyncze
    glosne ramki). Ostatni trzask nie moze byc uznany za koniec mowy, bo wtedy caly szum
    przed nim zostaje. Mowa konczy sie na ostatnim glosnym odcinku dluzszym niz max_blip_s,
    jesli po nim jest przerwa >= min_gap_s, a dalej juz tylko krotkie odcinki.
    """
    end = valley.numel()
    runs, start = [], None
    for i, quiet_frame in enumerate(valley.tolist() + [True]):
        if not quiet_frame and start is None:
            start = i
        elif quiet_frame and start is not None:
            runs.append((start, i))
            start = None
    blip = int(max_blip_s / FRAME_S)
    speech = [r for r in runs if r[1] - r[0] > blip]
    if not speech or speech[-1] == runs[-1]:
        return end
    last_end = speech[-1][1]
    next_start = runs[runs.index(speech[-1]) + 1][0]
    return last_end if (next_start - last_end) * FRAME_S >= min_gap_s else end


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
    frames = db.numel()
    end = _speech_end(valley)  # dalej analizujemy tylko mowe, bez koncowych trzaskow
    db, valley = db[:end], valley[:end]

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
    cut = min(frames, cut + int(pad_s / FRAME_S)) * int(FRAME_S * sr)
    out = wav[..., :cut].clone()
    fade = min(int(fade_s * sr), out.shape[-1])
    out[..., -fade:] *= torch.linspace(1.0, 0.0, fade, device=out.device)
    return out
