"""Wycisza znane, nieszkodliwe ostrzezenia zaleznosci Chatterboxa.

Importowac PIERWSZY, przed torch/chatterbox. Nie wycisza ostrzezen
'forcing EOS token' - to sygnal, ze generacja zostala ucieta.
"""
import os
import warnings

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

for message in (
    "pkg_resources is deprecated",
    "`LoRACompatibleLinear` is deprecated",
    "`torch.backends.cuda.sdp_kernel",
):
    warnings.filterwarnings("ignore", message=message)
