import json
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def story_dict() -> dict:
    """Świeża kopia neutralnego fixture (8 scen, 6 decyzji na ścieżce, 2 zakończenia)."""
    return json.loads((FIXTURE_DIR / "legend.json").read_text(encoding="utf-8"))

