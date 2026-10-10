import json

import pytest

from app.validate import CONTENT_DIR


@pytest.fixture
def story_dict() -> dict:
    """Świeża kopia neutralnego fixture (9 węzłów, 6 decyzji na trasie)."""
    return json.loads((CONTENT_DIR / "legend.json").read_text(encoding="utf-8"))

