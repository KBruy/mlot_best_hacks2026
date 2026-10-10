import json

import pytest

from app.validate import CONTENT_DIR


@pytest.fixture
def story_dict() -> dict:
    """Świeża kopia neutralnego fixture (8 scen, 6 decyzji na ścieżce, 2 zakończenia)."""
    return json.loads((CONTENT_DIR / "legend.json").read_text(encoding="utf-8"))

