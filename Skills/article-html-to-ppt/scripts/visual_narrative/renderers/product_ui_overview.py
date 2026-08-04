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
    if not isinstance(spaces, list):
        spaces = []

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

    placeholder = content.get("screenshot_placeholder") if isinstance(content.get("screenshot_placeholder"), dict) else {}
    ratio = _aspect_ratio(placeholder.get("aspect_ratio"), default=1.6)
    label = str(placeholder.get("label") or "待替换：应用截图")
    asset_status = str(placeholder.get("asset_status") or "missing")
    requirement = str(placeholder.get("source_requirement") or "PRD 要求真实应用截图；当前未提供截图资产。")

    shell = add_box(
        slide, name="Region:product_ui_overview:workspace_shell", x=x, y=y, w=w, h=h,
        fill=None, line=colors["hairline_grey"], radius=True,
    )
    names.append(shell.name)
    header = add_box(
        slide, name="Region:product_ui_overview:workspace_header", x=x + 0.12, y=y + 0.12,
        w=w - 0.24, h=0.45, fill=colors["mist_blue"], line=colors["hairline_grey"],
        text="产品工作台 · 可编辑界面框架（非真实截图）", text_color=colors["ink_navy"], font_size=10, bold=True,
    )
    names.append(header.name)

    side_w = min(2.45, max(2.05, w * 0.21))
    visual_h = h - 1.02
    visual_w = min(w - side_w - 0.72, visual_h * ratio)
    visual_h = visual_w / ratio
    visual_x = x + 0.28
    visual_y = y + 0.72 + max(0, (h - 0.92 - visual_h) / 2)
    placeholder_shape = add_box(
        slide, name="Placeholder:product_ui_overview:application_screenshot", x=visual_x, y=visual_y,
        w=visual_w, h=visual_h, fill=None, line=colors["insight_blue"],
        text=f"{label}\nCanvas 工作区 · 固定比例 {placeholder.get('aspect_ratio') or '16:10'}\n请替换为真实应用 PNG/JPG，并保留来源",
        text_color=colors["ink_navy"], font_size=13, bold=True, line_width=1.5,
    )
    names.append(placeholder_shape.name)
    annotation = add_box(
        slide, name="Annotation:product_ui_overview:screenshot_requirement", x=x + w - side_w - 0.18,
        y=visual_y, w=side_w, h=visual_h, fill=colors["mist_blue"], line=colors["hairline_grey"],
        text=f"截图交付要求\n资产：{'缺失' if asset_status == 'missing' else '已提供'}\n比例：{placeholder.get('aspect_ratio') or '16:10'}\n{requirement}",
        text_color=colors["slate_text"], font_size=10,
    )
    names.append(annotation.name)

    shapes: dict[str, Any] = {}
    for index, space in enumerate(spaces):
        if not isinstance(space, dict):
            continue
        space_id = str(space.get("id") or f"space-{index}")
        space_label = str(space.get("label") or space_id)
        if space_id.lower() == "topbar":
            shape = add_text(
                slide, name=f"Component:product_ui_overview:space:{space_id}", text=space_label,
                x=x + 0.28, y=y + 0.18, w=1.6, h=0.25, color=colors["ink_navy"], font_size=9, bold=True,
            )
        elif space_id.lower() == "canvas" or space_label.lower() == "canvas":
            shape = add_text(
                slide, name=f"Component:product_ui_overview:space:{space_id}", text=space_label,
                x=visual_x + 0.12, y=visual_y + 0.08, w=1.4, h=0.22, color=colors["slate_text"], font_size=10, bold=True,
            )
        else:
            shape = add_box(
                slide, name=f"Component:product_ui_overview:space:{space_id}", x=x + w - side_w - 0.06,
                y=visual_y + 0.18 + index * 0.52, w=side_w - 0.24, h=0.34,
                fill=colors["paper_white"], line=colors["hairline_grey"], text=space_label,
                text_color=colors["ink_navy"], font_size=9,
            )
        shapes[space_id] = placeholder_shape if space_id.lower() == "canvas" or space_label.lower() == "canvas" else shape
        names.append(shape.name)

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


def _aspect_ratio(value: Any, *, default: float) -> float:
    if isinstance(value, str) and ":" in value:
        left, right = value.split(":", 1)
        try:
            ratio = float(left) / float(right)
            if ratio > 0:
                return ratio
        except ValueError:
            pass
    return default
