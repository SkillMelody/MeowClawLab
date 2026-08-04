from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "1.0"


def build_design_evidence(product_prd: dict[str, Any]) -> dict[str, Any]:
    """Normalize direct PRD design evidence and expose its required consumers."""
    source_id = _string(product_prd.get("source_id")) or "product_prd"
    items: list[dict[str, Any]] = []
    items.extend(_items(product_prd.get("design_tokens"), "token", source_id))
    items.extend(_items(product_prd.get("ui_spaces"), "ui_space", source_id))
    items.extend(_items(product_prd.get("interactions"), "interaction", source_id))

    has_spaces = any(item["category"] == "ui_space" for item in items)
    has_interactions = any(item["category"] == "interaction" for item in items)
    coverage = {
        "product_ui_overview": {
            "required": has_spaces,
            "evidence_ids": [item["id"] for item in items if item["category"] == "ui_space"],
            "consumed": False,
        },
        "interaction_storyboard": {
            "required": has_interactions,
            "evidence_ids": [item["id"] for item in items if item["category"] == "interaction"],
            "consumed": False,
        },
    }
    required = [name for name, entry in coverage.items() if entry["required"] and not entry["consumed"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "source_id": source_id,
        "items": items,
        "coverage_matrix": coverage,
        "status": "blocked" if required else "ready",
        "blocking_codes": ["PRODUCT_PRD_REQUIRED_PROTOTYPES_UNCONSUMED"] if required else [],
    }


def _items(value: Any, category: str, source_id: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    normalized: list[dict[str, Any]] = []
    for ordinal, raw in enumerate(value, 1):
        if not isinstance(raw, dict):
            continue
        text = _string(raw.get("value")) or _string(raw.get("name")) or _string(raw.get("trigger"))
        if not text:
            continue
        locator = _string(raw.get("locator")) or "unspecified"
        normalized.append({
            "id": f"{category}-{ordinal:02d}",
            "category": category,
            "value": text,
            "source": {
                "source_id": source_id,
                "locator": locator,
                "directness": "direct",
                "confidence": "high",
            },
            "consumption": {"status": "unconsumed", "consumers": []},
        })
    return normalized


def _string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
