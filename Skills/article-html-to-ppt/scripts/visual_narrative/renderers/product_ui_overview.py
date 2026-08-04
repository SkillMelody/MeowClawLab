from __future__ import annotations

from typing import Any

from .common import RenderResult, add_bound_connector, add_box, add_text, content_box, resolve_style


def render(
    slide: Any,
    obj: dict[str, Any],
    intent: dict[str, Any],
    style: dict[str, Any],
) -> dict[str, Any]:
    content = obj.get("content") if isinstance(obj.get("content"), dict) else {}
    spaces = content.get("spaces")
    if not isinstance(spaces, list) or not spaces:
        raise ValueError("PRODUCT_UI_OVERVIEW_SPACES_REQUIRED")

    colors = resolve_style(style)
    x, y, w, h = content_box(intent)
    names: list[str] = []
    derived_name = "Label:product_ui_overview:derived"
    add_text(
        slide,
        name=derived_name,
        text="PRD 派生示意",
        x=x,
        y=y - 0.3,
        w=1.45,
        h=0.22,
        color=colors["slate_text"],
        font_size=10,
        bold=True,
    )
    names.append(derived_name)
    source_refs = _strings(content.get("source_refs"))
    source_width = max(2.15, (w - 1.55) / max(1, len(source_refs)))
    for index, source in enumerate(source_refs):
        name = f"Source:product_ui_overview:{index}"
        add_text(
            slide,
            name=name,
            text=f"来源：{source}",
            x=x + 1.55 + index * source_width,
            y=y - 0.3,
            w=source_width,
            h=0.28,
            color=colors["slate_text"],
            font_size=10,
        )
        names.append(name)

    shapes: dict[str, Any] = {}
    space_h = (h - 0.18) / len(spaces)
    for index, space in enumerate(spaces):
        if not isinstance(space, dict):
            continue
        space_id = str(space.get("id") or f"space-{index}")
        label = str(space.get("label") or space_id)
        is_topbar = space_id.lower() == "topbar" or index == 0 and len(spaces) > 2
        if is_topbar:
            box_x, box_y, box_w, box_h = x, y, w, min(0.58, space_h)
        elif len(spaces) <= 2:
            box_x, box_y, box_w, box_h = x, y + 0.78, w, h - 0.78
        else:
            body_index = index - 1
            body_count = max(1, len(spaces) - 1)
            box_x = x + body_index * (w / body_count)
            box_y = y + 0.78
            box_w = w / body_count - 0.12
            box_h = h - 0.78
        name = f"Component:product_ui_overview:space:{space_id}"
        shapes[space_id] = add_box(
            slide,
            name=name,
            x=box_x,
            y=box_y,
            w=box_w,
            h=box_h,
            fill=colors["mist_blue"] if index % 2 == 0 else colors["paper_white"],
            line=colors["insight_blue"] if index == 0 else colors["hairline_grey"],
            text=label,
            text_color=colors["ink_navy"],
            font_size=11,
            bold=True,
        )
        names.append(name)

    for index, relationship in enumerate(content.get("relationships") or []):
        if not isinstance(relationship, dict):
            continue
        start = shapes.get(str(relationship.get("from") or ""))
        end = shapes.get(str(relationship.get("to") or ""))
        if start is None or end is None:
            continue
        name = f"Connector:product_ui_overview:relationship:{index}"
        add_bound_connector(
            slide,
            start,
            end,
            name=name,
            color=colors["signal_blue"],
            vertical=start.top < end.top,
        )
        names.append(name)
    return RenderResult(actual_route="native_diagram", object_names=names).to_dict()


def _strings(value: Any) -> list[str]:
    return [item.strip() for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []
