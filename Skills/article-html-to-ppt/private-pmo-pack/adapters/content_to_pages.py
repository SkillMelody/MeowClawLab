from __future__ import annotations

from typing import Any

from quality.layout_budget import validate_layout_budget
from routing.page_router import route_page


def select_pages(evidence_units: list[dict[str, Any]]) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    for index, evidence in enumerate(evidence_units, start=1):
        route = route_page(evidence)
        supporting = evidence.get("supporting_visuals_override", route["supporting_visuals"])
        layout_input = {
            "page_family": route["page_family"],
            "primary_visual": route["primary_visual"],
            "supporting_visuals": supporting,
            "body_character_count": int(evidence.get("body_character_count") or 0),
        }
        layout_qa = validate_layout_budget(layout_input)
        pages.append(
            {
                "page_id": f"P{index:02d}",
                "evidence_id": str(evidence.get("id") or f"E{index}"),
                "intent": str(evidence.get("intent") or ""),
                "page_family": route["page_family"],
                "primary_visual": route["primary_visual"],
                "supporting_visuals": list(supporting),
                "selection_reason_codes": route["reason_codes"],
                "layout_qa": layout_qa,
            }
        )

    return {
        "schema_version": "1.0",
        "passed": all(page["layout_qa"]["passed"] for page in pages),
        "pages": pages,
    }
