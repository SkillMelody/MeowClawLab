from __future__ import annotations

from typing import Any


RACI_CODES = {"R", "A", "C", "I"}
STATUSES = {"green", "amber", "yellow", "red", "gray"}


def validate_pmo_semantics(data: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []

    for action in data.get("actions", []) or []:
        if not str(action.get("owner") or "").strip():
            reasons.append("action_missing_owner")
        if not str(action.get("deadline") or "").strip():
            reasons.append("action_missing_deadline")
        if str(action.get("status") or "").lower() not in STATUSES:
            reasons.append("action_missing_status")

    raci = data.get("raci") or {}
    role_count = len(raci.get("roles") or [])
    for task in raci.get("tasks", []) or []:
        assignments = task.get("assignments") or []
        if len(assignments) != role_count or any(code not in RACI_CODES for code in assignments):
            reasons.append("raci_assignments_invalid")
        if assignments.count("A") != 1:
            reasons.append("raci_accountable_count_invalid")

    for risk in data.get("risk_heat_map", []) or []:
        for key in ("impact", "likelihood"):
            value = risk.get(key)
            if not isinstance(value, int) or not 1 <= value <= 5:
                reasons.append(f"risk_{key}_out_of_range")
        if not str(risk.get("owner") or "").strip():
            reasons.append("risk_missing_owner")

    decision = data.get("decision") or {}
    if not str(decision.get("recommendation") or "").strip():
        reasons.append("decision_missing_recommendation")
    if not str(decision.get("next_step") or "").strip():
        reasons.append("decision_missing_next_step")

    return {
        "passed": not reasons,
        "reason_codes": sorted(set(reasons)),
    }
