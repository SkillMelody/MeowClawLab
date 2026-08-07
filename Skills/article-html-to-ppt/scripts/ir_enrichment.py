"""Deterministic, source-bound supporting-object enrichment for Path B IR."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

DATA_COMPONENTS = {"bar_chart", "line_chart", "pie_chart", "native_table", "heat_matrix", "kpi_dashboard", "metric_card"}
SUPPORT_COMPONENTS = {"evidence_block", "metric_card", "comparison_card", "summary_action_card", "source_note"}


def _content_tokens(value: str) -> set[str]:
    """Use CJK characters and word tokens for conservative duplicate detection."""
    return {char for char in value.replace(" ", "") if char.strip()}


def _is_near_duplicate(value: str, existing: str) -> bool:
    candidate, baseline = _content_tokens(value), _content_tokens(existing)
    if not candidate or not baseline:
        return False
    return len(candidate & baseline) / len(candidate | baseline) >= 0.75


def enrich_ppt_ir(ppt_ir: dict[str, Any]) -> dict[str, Any]:
    enriched = deepcopy(ppt_ir)
    for slide in enriched.get("slides", []) or []:
        if not isinstance(slide, dict):
            continue
        objects = [obj for obj in slide.get("objects", []) or [] if isinstance(obj, dict)]
        slide["objects"] = objects
        kinds = {str(obj.get("component_type") or obj.get("type") or "") for obj in objects}
        has_support = any(str(obj.get("component_type") or obj.get("type") or "") in SUPPORT_COMPONENTS and obj.get("priority") != "primary" for obj in objects)
        source_refs = list(slide.get("source_refs") or [])
        message = str(slide.get("judgment") or slide.get("message") or "").strip()
        title = str(slide.get("title") or "").strip()
        role = str(slide.get("slide_role") or "")
        evidence = [item for item in slide.get("supporting_evidence", []) or [] if isinstance(item, dict)]

        # Promote an existing slide-level citation to an existing data object
        # only; this preserves provenance without inventing a source or claim.
        if source_refs:
            for obj in objects:
                component = str(obj.get("component_type") or obj.get("type") or "")
                if component in DATA_COMPONENTS and not obj.get("source_refs"):
                    obj["source_refs"] = list(source_refs)

        # A slide's message/judgment is a conclusion, never independent evidence.
        # Only an explicitly supplied, separately source-bound evidence item may be
        # compiled into a supporting native object; no data or claims are inferred.
        if role in {"data", "judgment"} and not has_support:
            has_primary_data = bool(kinds & DATA_COMPONENTS)
            candidate = next((item for item in evidence if str(item.get("content") or "").strip() and item.get("source_refs")), None)
            if candidate and (role == "judgment" or has_primary_data):
                content = str(candidate["content"]).strip()
                if not _is_near_duplicate(content, f"{title} {message}"):
                    objects.append({
                        "id": f"{slide.get('id', 'slide')}-source-bound-interpretation",
                        "type": "shape",
                        "component_type": "evidence_block",
                        "semantic_role": "interpretation",
                        "content": content,
                        "source_refs": list(candidate["source_refs"]),
                        "editability": "native_required",
                        "priority": "supporting",
                        "delivery_preferences": {"preferred_route": "native_ppt", "allowed_fallbacks": []},
                    })
        if role == "closing":
            actions = [obj for obj in objects if str(obj.get("component_type") or obj.get("type") or "") == "summary_action_card"]
            for index, content in enumerate([title, message], start=1):
                if len(actions) >= 2 or not content:
                    break
                objects.append({
                    "id": f"{slide.get('id', 'slide')}-action-{index}",
                    "type": "shape",
                    "component_type": "summary_action_card",
                    "semantic_role": "next_action",
                    "content": content,
                    "source_refs": source_refs,
                    "editability": "native_required",
                    "priority": "primary" if index == 1 else "supporting",
                    "delivery_preferences": {"preferred_route": "native_ppt", "allowed_fallbacks": []},
                })
                actions.append(objects[-1])
    return enriched
