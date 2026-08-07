from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from builders.python_pptx_adapter import _object_frame


def test_data_primary_gets_dominant_canvas_and_supporting_object_gets_side_panel() -> None:
    objects = [
        {"id": "chart", "type": "chart", "component_type": "bar_chart", "priority": "primary"},
        {"id": "interpretation", "type": "shape", "component_type": "evidence_block", "priority": "supporting"},
    ]

    primary = _object_frame(objects, 0, y=1.8, content_height=4.5, style={"margin_left": 0.55, "card_gap": 0.2})
    support = _object_frame(objects, 1, y=1.8, content_height=4.5, style={"margin_left": 0.55, "card_gap": 0.2})

    assert primary == (0.55, 1.8, 7.25, 4.5)
    assert support == (8.05, 1.8, 4.7, 1.35)
