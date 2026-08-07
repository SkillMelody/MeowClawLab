from __future__ import annotations

from typing import Any


PAGE_LIMITS = {
    "single_project_health_dashboard": {"supporting": 3, "characters": 160},
    "portfolio_dashboard": {"supporting": 3, "characters": 150},
    "time_resource_dashboard": {"supporting": 3, "characters": 140},
    "pmo_control_tower": {"supporting": 4, "characters": 170},
    "executive_status_one_pager": {"supporting": 4, "characters": 190},
    "claim_evidence": {"supporting": 2, "characters": 160},
}


def validate_layout_budget(page: dict[str, Any]) -> dict[str, Any]:
    page_family = str(page.get("page_family") or "claim_evidence")
    limits = PAGE_LIMITS.get(page_family, PAGE_LIMITS["claim_evidence"])
    supporting = list(page.get("supporting_visuals") or [])
    character_count = int(page.get("body_character_count") or 0)
    reasons: list[str] = []

    if not page.get("primary_visual"):
        reasons.append("primary_visual_missing")
    if len(supporting) > limits["supporting"]:
        reasons.append("primary_visual_budget_exceeded")
    if character_count > limits["characters"]:
        reasons.append("text_density_exceeded")

    return {
        "passed": not reasons,
        "page_family": page_family,
        "reason_codes": reasons,
        "limits": limits,
        "observed": {
            "supporting_visual_count": len(supporting),
            "body_character_count": character_count,
        },
    }
