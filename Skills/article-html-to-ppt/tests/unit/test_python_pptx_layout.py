from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from builders.python_pptx_adapter import _object_frame


def test_data_primary_gets_dominant_canvas_and_supporting_object_gets_side_panel() -> None:
    objects = [
        {"id": "chart", "type": "chart", "component_type": "bar_chart", "priority": "primary"},
        {
            "id": "interpretation",
            "type": "shape",
            "component_type": "evidence_block",
            "priority": "supporting",
            "semantic_role": "interpretation",
            "provenance": {"derivation": "same_slide_evidence_augmenter"},
        },
    ]

    primary = _object_frame(objects, 0, y=1.8, content_height=4.5, style={"margin_left": 0.55, "card_gap": 0.2})
    support = _object_frame(objects, 1, y=1.8, content_height=4.5, style={"margin_left": 0.55, "card_gap": 0.2})

    assert primary == (0.55, 1.8, 8.35, 4.5)
    assert support == (9.14, 1.8, 3.83, 4.5)


def test_two_primary_objects_stack_in_main_zone_when_generated_support_is_present() -> None:
    objects = [
        {"id": "chart", "type": "chart", "component_type": "bar_chart", "priority": "primary"},
        {"id": "table", "type": "table", "component_type": "native_table", "priority": "primary"},
        {
            "id": "interpretation",
            "type": "shape",
            "component_type": "evidence_block",
            "priority": "supporting",
            "semantic_role": "interpretation",
            "provenance": {"derivation": "same_slide_evidence_augmenter"},
        },
    ]

    chart = _object_frame(objects, 0, y=1.8, content_height=4.5, style={"margin_left": 0.55, "card_gap": 0.2})
    table = _object_frame(objects, 1, y=1.8, content_height=4.5, style={"margin_left": 0.55, "card_gap": 0.2})
    support = _object_frame(objects, 2, y=1.8, content_height=4.5, style={"margin_left": 0.55, "card_gap": 0.2})

    assert chart == pytest.approx((0.55, 1.8, 8.35, 2.49))
    assert table == pytest.approx((0.55, 4.53, 8.35, 1.77))
    assert support == (9.14, 1.8, 3.83, 4.5)
