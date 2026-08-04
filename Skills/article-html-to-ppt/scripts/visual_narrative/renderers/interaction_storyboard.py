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
    steps = content.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("INTERACTION_STORYBOARD_STEPS_REQUIRED")

    colors = resolve_style(style)
    x, y, w, h = content_box(intent)
    names: list[str] = []
    derived_name = "Label:interaction_storyboard:derived"
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
        name = f"Source:interaction_storyboard:{index}"
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

    node_w = max(1.45, min(2.3, (w - 0.25 * (len(steps) - 1)) / len(steps)))
    total_w = node_w * len(steps) + 0.25 * (len(steps) - 1)
    start_x = x + max(0, (w - total_w) / 2)
    node_y = y + max(0.3, (h - 1.25) / 2)
    shapes: dict[str, Any] = {}
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("id") or f"step-{index}")
        label = str(step.get("label") or step_id)
        kind = str(step.get("kind") or "state")
        fill = colors["mist_blue"] if kind in {"async_state", "result"} else colors["paper_white"]
        name = f"Component:interaction_storyboard:step:{step_id}"
        shapes[step_id] = add_box(
            slide,
            name=name,
            x=start_x + index * (node_w + 0.25),
            y=node_y,
            w=node_w,
            h=1.25,
            fill=fill,
            line=colors["signal_blue"] if kind == "async_state" else colors["hairline_grey"],
            text=f"{kind}\n{label}",
            text_color=colors["ink_navy"],
            font_size=10,
            bold=True,
        )
        names.append(name)

    for index, transition in enumerate(content.get("transitions") or []):
        if not isinstance(transition, dict):
            continue
        start = shapes.get(str(transition.get("from") or ""))
        end = shapes.get(str(transition.get("to") or ""))
        if start is None or end is None:
            continue
        name = f"Connector:interaction_storyboard:transition:{index}"
        add_bound_connector(slide, start, end, name=name, color=colors["signal_blue"])
        names.append(name)
    return RenderResult(actual_route="native_diagram", object_names=names).to_dict()


def _strings(value: Any) -> list[str]:
    return [item.strip() for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []
