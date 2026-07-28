from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from visual_narrative.rhythm import evaluate_deck_rhythm


def slide(
    archetype: str,
    *,
    priority: str = "supporting",
    expression: str = "statement",
) -> dict:
    return {
        "priority": priority,
        "page_archetype": archetype,
        "primary_expression": expression,
    }


def test_formal_deck_fails_repetitive_card_rhythm() -> None:
    plan = {
        "slides": [
            slide("equal_cards", priority="supporting", expression="cards")
            for _ in range(10)
        ]
    }

    report = evaluate_deck_rhythm(plan)

    codes = {issue["code"] for issue in report["issues"]}
    assert report["status"] == "failed"
    assert {
        "RHYTHM_KEY_SLIDE_COUNT",
        "RHYTHM_ARCHETYPE_DIVERSITY",
        "RHYTHM_CONSECUTIVE_ARCHETYPE",
        "RHYTHM_CARD_RATIO",
    } <= codes


def test_balanced_formal_deck_passes() -> None:
    archetypes = [
        "cover",
        "statement",
        "data",
        "relationship",
        "statement",
        "roadmap",
        "data",
        "relationship",
        "decision",
        "closing",
    ]
    slides = [
        slide(
            archetype,
            priority="key" if index in {2, 6} else "supporting",
            expression="cards" if index in {1, 4, 8} else "statement",
        )
        for index, archetype in enumerate(archetypes)
    ]

    report = evaluate_deck_rhythm({"slides": slides})

    assert report["status"] == "passed"
    assert report["issues"] == []
    assert report["metrics"] == {
        "slide_count": 10,
        "key_slide_count": 2,
        "archetype_count": 7,
        "max_consecutive_archetype": 1,
        "card_ratio": pytest.approx(0.30),
    }


def test_card_ratio_above_thirty_percent_fails() -> None:
    archetypes = [
        "cover",
        "statement",
        "data",
        "relationship",
        "statement",
        "roadmap",
        "data",
        "relationship",
        "decision",
        "closing",
    ]
    slides = [
        slide(
            archetype,
            priority="key" if index in {2, 6} else "supporting",
            expression="cards" if index < 4 else "statement",
        )
        for index, archetype in enumerate(archetypes)
    ]

    report = evaluate_deck_rhythm({"slides": slides})

    assert "RHYTHM_CARD_RATIO" in {issue["code"] for issue in report["issues"]}


@pytest.mark.parametrize("malformed_plan", [None, "oops", [], {"slides": "oops"}])
def test_malformed_plan_fails_closed(malformed_plan: object) -> None:
    report = evaluate_deck_rhythm(malformed_plan)

    assert report["status"] == "failed"
    assert report["metrics"]["slide_count"] == 0
    assert "RHYTHM_PLAN_INVALID" in {issue["code"] for issue in report["issues"]}
