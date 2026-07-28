from __future__ import annotations

import importlib.metadata
import math
from pathlib import Path
from typing import Any

from .base import BuildInspection, BuildPlan, BuildResult, BuilderCapability, SupportLevel


class PythonPptxAdapter:
    name = "python_pptx"

    def probe(self) -> BuilderCapability:
        version = _package_version()
        available = version is not None
        return BuilderCapability(
            name=self.name,
            available=available,
            version=version,
            command="python" if available else None,
            features={
                "native_text": True,
                "native_table": True,
                "native_chart": True,
                "native_connector": True,
                "svg_embed": False,
                "speaker_notes": False,
                "theme": "partial",
                "slide_master": "partial",
                "readback": True,
            },
            components={
                "heat_matrix": "full",
                "layered_architecture": "full",
                "drill_down_stair": "full",
                "phase_roadmap": "full",
            } if available else {},
            warnings=[] if available else ["python-pptx package is not importable."],
        )

    def supports(self, component_type: str, delivery_route: str) -> SupportLevel:
        if (
            component_type
            in {
                "heat_matrix",
                "layered_architecture",
                "drill_down_stair",
                "phase_roadmap",
            }
            and delivery_route == "native_diagram"
        ):
            return "full"
        if delivery_route in {"native_ppt", "native_table", "native_chart"}:
            return "full"
        if delivery_route in {"generated_image", "background_image", "hybrid_overlay"}:
            return "visual_only"
        return "unsupported"

    def plan(self, ppt_ir: dict[str, Any], style_contract: dict[str, Any], delivery_plan: dict[str, Any]) -> BuildPlan:
        object_plans = {
            (obj.get("slide_id"), obj.get("object_id")): obj
            for slide in delivery_plan.get("slides", []) or []
            for obj in slide.get("objects", []) or []
            if isinstance(obj, dict)
        }
        slides = []
        for slide in ppt_ir.get("slides", []) or []:
            planned_objects = []
            for obj in slide.get("objects", []) or []:
                planned = dict(obj)
                planned["delivery_plan"] = object_plans.get((slide.get("id"), obj.get("id")), {})
                planned_objects.append(planned)
            slide_plan = dict(slide)
            slide_plan["objects"] = planned_objects
            slide_plan["style_contract"] = style_contract
            slides.append(slide_plan)
        warnings = _unsupported_style_warnings(style_contract)
        return BuildPlan(builder=self.name, slides=slides, style_contract=dict(style_contract), warnings=warnings)

    def build(self, build_plan: BuildPlan, output_dir: Path) -> BuildResult:
        try:
            from pptx import Presentation
            from pptx.dml.color import RGBColor
            from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
            from pptx.util import Inches, Pt
        except Exception as exc:
            return BuildResult(builder=self.name, status="failed", errors=[{"code": "BUILDER_RUNTIME_IMPORT_FAILED", "message": str(exc)}])

        output_dir.mkdir(parents=True, exist_ok=True)
        deck_path = output_dir / "deck.pptx"
        style = _resolve_style(build_plan.style_contract)
        presentation = Presentation()
        presentation.slide_width = Inches(13.333)
        presentation.slide_height = Inches(7.5)
        blank_layout = presentation.slide_layouts[6]

        object_results: list[dict[str, Any]] = []
        fallbacks: list[dict[str, Any]] = []
        warnings: list[str] = list(build_plan.warnings)

        for slide_number, slide_plan in enumerate(build_plan.slides, start=1):
            slide = presentation.slides.add_slide(blank_layout)
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor.from_string(style["background"])
            if slide_plan.get("slide_role") == "cover":
                _add_cover(slide, slide_plan, style)
                if not (slide_plan.get("objects") or []):
                    continue
            else:
                _add_textbox(
                    slide,
                    slide_plan.get("title") or "Untitled",
                    x=style["margin_left"],
                    y=style["margin_top"],
                    w=12.2,
                    h=0.45,
                    font_size=style["title_size"],
                    bold=True,
                    color=style["primary"],
                    font_name=style["font_name"],
                )
            body_parts: list[str] = []
            seen_text = {
                str(slide_plan.get("title") or "").strip()
            }
            for part in (slide_plan.get("judgment"), slide_plan.get("message")):
                if not isinstance(part, str):
                    continue
                normalized = part.strip()
                if not normalized or normalized in seen_text:
                    continue
                body_parts.append(normalized)
                seen_text.add(normalized)
            body = "\n".join(body_parts)
            if body and slide_plan.get("slide_role") != "cover":
                _add_textbox(slide, body, x=style["margin_left"], y=1.05, w=11.7, h=0.5, font_size=style["body_size"], color=style["text_secondary"], font_name=style["font_name"])
            if slide_plan.get("slide_role") != "cover":
                _add_footer(slide, slide_plan, style, slide_number)
            objects = slide_plan.get("objects", []) or []
            if not objects:
                continue
            card_width = max(2.6, min(3.6, 10.8 / max(len(objects), 1)))
            for index, obj in enumerate(objects):
                route = ((obj.get("delivery_plan") or {}).get("selected_route") or obj.get("delivery_preferences", {}).get("preferred_route") or "native_ppt")
                component_type = str(obj.get("component_type") or obj.get("type") or "")
                renderer = _semantic_renderer(component_type)
                if renderer is not None and route == "native_diagram":
                    rendered = renderer(
                        slide,
                        obj,
                        slide_plan.get("page_design_intent")
                        if isinstance(slide_plan.get("page_design_intent"), dict)
                        else {},
                        slide_plan.get("style_contract")
                        if isinstance(slide_plan.get("style_contract"), dict)
                        else {},
                    )
                    warnings.extend(rendered.get("warnings", []))
                    object_results.append(
                        {
                            "slide_id": slide_plan.get("id"),
                            "object_id": obj.get("id"),
                            "component_type": component_type,
                            "planned_route": route,
                            "actual_route": rendered["actual_route"],
                            "status": "created",
                            "object_names": rendered.get("object_names", []),
                        }
                    )
                    continue
                actual_route = route
                component_type = obj.get("component_type") or obj.get("type")
                is_chart = route == "native_chart" and obj.get("type") == "chart"
                is_process = route == "native_diagram" and component_type == "process"
                if route in {"hybrid_overlay", "svg_component", "generated_image", "background_image"}:
                    actual_route = "native_ppt"
                    fallbacks.append(
                        {
                            "slide_id": slide_plan.get("id"),
                            "object_id": obj.get("id"),
                            "component_type": component_type,
                            "planned_route": route,
                            "actual_route": actual_route,
                            "reason_codes": ["PYTHON_PPTX_MINIMAL_NATIVE_FALLBACK"],
                            "editable_core_preserved": obj.get("editability") != "native_required",
                        }
                    )
                single_object = len(objects) == 1
                x = (
                    style["margin_left"]
                    if single_object
                    else style["margin_left"] + index * (card_width + style["card_gap"])
                )
                y = 1.85
                object_width = 11.7 if single_object else card_width
                content_height = 4.65
                if route == "native_table" or obj.get("type") == "table":
                    _add_table(
                        slide,
                        obj,
                        x=x,
                        y=y,
                        w=object_width,
                        h=content_height if single_object else 2.3,
                        style=style,
                    )
                elif is_chart:
                    _add_chart(
                        slide,
                        obj,
                        x=x,
                        y=y,
                        w=object_width,
                        h=content_height if single_object else 3.4,
                        style=style,
                    )
                elif is_process:
                    process_height = 2.2 if single_object else 1.35
                    process_y = (
                        y + (content_height - process_height) / 2
                        if single_object
                        else y
                    )
                    _add_process(
                        slide,
                        obj,
                        x=x,
                        y=process_y,
                        w=object_width,
                        h=process_height,
                        style=style,
                    )
                elif component_type == "metric_card":
                    _add_metric_wall(
                        slide,
                        obj,
                        x=x,
                        y=y,
                        w=object_width,
                        h=content_height if single_object else 1.35,
                        style=style,
                    )
                else:
                    _add_card(
                        slide,
                        obj,
                        x=x,
                        y=y,
                        w=object_width,
                        h=content_height if single_object else 1.35,
                        style=style,
                    )
                object_results.append(
                    {
                        "slide_id": slide_plan.get("id"),
                        "object_id": obj.get("id"),
                        "component_type": obj.get("component_type") or obj.get("type"),
                        "planned_route": route,
                        "actual_route": actual_route,
                        "status": "created",
                    }
                )

        presentation.save(deck_path)
        return BuildResult(builder=self.name, status="created", pptx=str(deck_path), object_results=object_results, fallbacks=fallbacks, warnings=warnings)

    def inspect_output(self, pptx_path: Path) -> BuildInspection:
        try:
            from ppt_qa.package_inspector import inspect_package
        except Exception as exc:
            return BuildInspection(builder=self.name, status="failed", errors=[{"code": "BUILDER_INSPECT_IMPORT_FAILED", "message": str(exc)}])
        inspection = inspect_package(pptx_path)
        return BuildInspection(
            builder=self.name,
            status="passed" if inspection.status == "passed" else "failed",
            issues=[issue.__dict__ for issue in inspection.issues],
        )


def _package_version() -> str | None:
    try:
        return importlib.metadata.version("python-pptx")
    except importlib.metadata.PackageNotFoundError:
        return None


def _semantic_renderer(component_type: str) -> Any:
    try:
        from scripts.visual_narrative.renderers import get_renderer
    except ImportError:
        return None
    return get_renderer(component_type)


def _add_textbox(slide: Any, text: str, *, x: float, y: float, w: float, h: float, font_size: float, color: str, bold: bool = False, font_name: str | None = None) -> None:
    from pptx.dml.color import RGBColor
    from pptx.util import Inches, Pt

    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    paragraph = frame.paragraphs[0]
    run = paragraph.add_run()
    run.text = str(text)
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.name = font_name
    run.font.color.rgb = RGBColor.from_string(color)
    return box


def _add_cover(slide: Any, slide_plan: dict[str, Any], style: dict[str, Any]) -> None:
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
    from pptx.util import Inches

    accent = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(style["margin_left"]),
        Inches(1.45),
        Inches(0.12),
        Inches(3.75),
    )
    accent.name = "Decoration:cover:accent"
    accent.fill.solid()
    accent.fill.fore_color.rgb = RGBColor.from_string(style["primary"])
    accent.line.fill.background()
    _add_textbox(
        slide,
        str(slide_plan.get("title") or "Untitled"),
        x=style["margin_left"] + 0.42,
        y=2.0,
        w=10.8,
        h=1.65,
        font_size=max(32.0, style["title_size"] * 1.55),
        bold=True,
        color=style["primary"],
        font_name=style["font_name"],
    )
    subtitle = str(slide_plan.get("message") or "").strip()
    if subtitle and subtitle != str(slide_plan.get("title") or "").strip():
        _add_textbox(
            slide,
            subtitle,
            x=style["margin_left"] + 0.42,
            y=4.0,
            w=9.8,
            h=0.75,
            font_size=max(14.0, style["body_size"]),
            color=style["text_secondary"],
            font_name=style["font_name"],
        )
    rule = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(style["margin_left"] + 0.42),
        Inches(5.25),
        Inches(4.0),
        Inches(0.04),
    )
    rule.name = "Decoration:cover:rule"
    rule.fill.solid()
    rule.fill.fore_color.rgb = RGBColor.from_string(style["border"])
    rule.line.fill.background()


def _add_footer(
    slide: Any,
    slide_plan: dict[str, Any],
    style: dict[str, Any],
    slide_number: int,
) -> None:
    if not style["footer_enabled"]:
        return
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Inches

    y = 7.5 - style["margin_bottom"] - style["footer_height"]
    divider = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(style["margin_left"]),
        Inches(y),
        Inches(12.2),
        Inches(0.012),
    )
    divider.name = "Decoration:footer:divider"
    divider.fill.solid()
    divider.fill.fore_color.rgb = RGBColor.from_string(style["border"])
    divider.line.fill.background()

    refs = [
        item
        for item in slide_plan.get("source_refs", []) or []
        if isinstance(item, dict)
    ]
    source_parts = []
    for item in refs:
        source_id = str(item.get("source_id") or "").strip()
        locator = str(item.get("locator") or "").strip()
        combined = " · ".join(part for part in (source_id, locator) if part)
        if combined and combined not in source_parts:
            source_parts.append(combined)
    source_text = "来源：" + "；".join(source_parts) if source_parts else "来源：内部综合"
    source = _add_textbox(
        slide,
        source_text,
        x=style["margin_left"],
        y=y + 0.055,
        w=10.8,
        h=style["footer_height"],
        font_size=style["footnote_size"],
        color=style["text_secondary"],
        font_name=style["font_name"],
    )
    source.name = "source_note"
    page = _add_textbox(
        slide,
        f"{slide_number:02d}",
        x=11.9,
        y=y + 0.055,
        w=0.85,
        h=style["footer_height"],
        font_size=style["footnote_size"],
        color=style["text_secondary"],
        font_name=style["font_name"],
    )
    page.name = "footer_page"
    page.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT


def _metric_entries(obj: dict[str, Any]) -> list[dict[str, str]]:
    content = obj.get("content")
    if not isinstance(content, dict):
        return []
    metrics = content.get("metrics")
    if isinstance(metrics, list):
        entries: list[dict[str, str]] = []
        for index, item in enumerate(metrics, start=1):
            if not isinstance(item, dict):
                continue
            value = item.get("value")
            if value is None:
                continue
            entries.append(
                {
                    "label": str(item.get("label") or f"指标 {index:02d}"),
                    "value": (
                        f"{item.get('prefix') or ''}"
                        f"{value}"
                        f"{item.get('suffix') or ''}"
                    ),
                }
            )
        if entries:
            return entries
    raw_values = content.get("values")
    labels = content.get("labels")
    if isinstance(raw_values, list):
        return [
            {
                "label": (
                    str(labels[index])
                    if isinstance(labels, list) and index < len(labels)
                    else f"指标 {index + 1:02d}"
                ),
                "value": str(value),
            }
            for index, value in enumerate(raw_values)
        ]
    quartiles = content.get("quartiles")
    if isinstance(quartiles, list):
        quartile_labels = ["25 分位", "中位数", "75 分位"]
        return [
            {
                "label": quartile_labels[index] if index < len(quartile_labels) else f"分位 {index + 1}",
                "value": f"{value}%",
            }
            for index, value in enumerate(quartiles)
        ]
    return []


def _add_metric_wall(
    slide: Any,
    obj: dict[str, Any],
    *,
    x: float,
    y: float,
    w: float,
    h: float,
    style: dict[str, Any],
) -> None:
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.util import Inches

    entries = _metric_entries(obj)
    if not entries:
        _add_card(slide, obj, x=x, y=y, w=w, h=h, style=style)
        return
    columns = 3 if len(entries) <= 6 else 4
    rows = math.ceil(len(entries) / columns)
    gap = style["card_gap"]
    wall_h = min(h, rows * 2.3 + gap * (rows - 1))
    wall_y = y + max(0.0, (h - wall_h) / 2)
    card_w = (w - gap * (columns - 1)) / columns
    card_h = (wall_h - gap * (rows - 1)) / rows
    for index, entry in enumerate(entries):
        row, column = divmod(index, columns)
        left = x + column * (card_w + gap)
        top = wall_y + row * (card_h + gap)
        card = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            Inches(left),
            Inches(top),
            Inches(card_w),
            Inches(card_h),
        )
        card.name = f"Material:metric_wall:card:{index + 1:02d}"
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor.from_string(style["surface"])
        card.line.color.rgb = RGBColor.from_string(style["border"])
        value_box = _add_textbox(
            slide,
            entry["value"],
            x=left + 0.22,
            y=top + 0.38,
            w=card_w - 0.44,
            h=max(0.58, card_h * 0.42),
            font_size=30,
            bold=True,
            color=style["primary"],
            font_name=style["font_name"],
        )
        value_box.name = f"Component:metric_wall:value:{index + 1:02d}"
        value_box.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        value_box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        label_box = _add_textbox(
            slide,
            entry["label"],
            x=left + 0.22,
            y=top + card_h * 0.64,
            w=card_w - 0.44,
            h=max(0.35, card_h * 0.2),
            font_size=max(11, style["table_size"]),
            color=style["text_secondary"],
            font_name=style["font_name"],
        )
        label_box.name = f"Component:metric_wall:label:{index + 1:02d}"
        label_box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER


def _object_text(obj: dict[str, Any]) -> str:
    content = obj.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, dict):
        for key in ("title", "label", "claim", "text", "value"):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    component = obj.get("component_type") or obj.get("semantic_role") or obj.get("type")
    return str(component or "PPT object").replace("_", " ").title()


def _add_card(
    slide: Any,
    obj: dict[str, Any],
    *,
    x: float,
    y: float,
    w: float,
    h: float,
    style: dict[str, Any],
) -> None:
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.util import Inches, Pt

    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(x),
        Inches(y),
        Inches(w),
        Inches(h),
    )
    shape.name = f"Component:card:{obj.get('id') or 'primary'}"
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(style["surface"])
    shape.line.color.rgb = RGBColor.from_string(style["border"])
    text_frame = shape.text_frame
    text_frame.clear()
    text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    text_frame.margin_left = Inches(0.42)
    text_frame.margin_right = Inches(0.42)
    paragraph = text_frame.paragraphs[0]
    paragraph.alignment = PP_ALIGN.CENTER
    run = paragraph.add_run()
    run.text = _object_text(obj)
    run.font.size = Pt(
        max(20.0, style["body_size"] * 1.6)
        if h >= 3.0
        else style["body_size"]
    )
    run.font.name = style["font_name"]
    run.font.color.rgb = RGBColor.from_string(style["text_primary"])


def _table_data(obj: dict[str, Any]) -> list[list[str]]:
    content = obj.get("content")
    if isinstance(content, dict):
        rows = content.get("rows")
        if isinstance(rows, list) and rows:
            return [[str(cell) for cell in row] for row in rows if isinstance(row, list)]
        headers = content.get("headers")
        body = content.get("body")
        if isinstance(headers, list) and isinstance(body, list):
            return [[str(cell) for cell in headers], *[[str(cell) for cell in row] for row in body if isinstance(row, list)]]
    return [["Item", "Status"], [_object_text(obj), "Editable"]]


def _chart_data(obj: dict[str, Any]) -> tuple[list[str], list[tuple[str, list[float]]]]:
    content = obj.get("content")
    if not isinstance(content, dict):
        raise ValueError(f"Chart {obj.get('id')} requires mapping content")
    categories = content.get("categories")
    raw_series = content.get("series")
    if not isinstance(categories, list) or not categories or not isinstance(raw_series, list) or not raw_series:
        raise ValueError(f"Chart {obj.get('id')} requires non-empty categories and series")
    parsed_series: list[tuple[str, list[float]]] = []
    for series in raw_series:
        if not isinstance(series, dict) or not isinstance(series.get("values"), list):
            raise ValueError(f"Chart {obj.get('id')} has invalid series")
        values = series["values"]
        if len(values) != len(categories) or not all(isinstance(value, (int, float)) for value in values):
            raise ValueError(f"Chart {obj.get('id')} series values must align with categories")
        parsed_series.append((str(series.get("name") or "Series"), [float(value) for value in values]))
    return [str(category) for category in categories], parsed_series


def _add_chart(slide: Any, obj: dict[str, Any], *, x: float, y: float, w: float, h: float, style: dict[str, Any]) -> None:
    from pptx.chart.data import ChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
    from pptx.util import Inches, Pt

    categories, series = _chart_data(obj)
    data = ChartData()
    data.categories = categories
    for name, values in series:
        data.add_series(name, values)
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(max(w, 5.8)), Inches(h), data
    ).chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.font.name = style["font_name"]
    chart.legend.font.size = Pt(style["table_size"])
    chart.value_axis.has_major_gridlines = True
    chart.category_axis.tick_labels.font.name = style["font_name"]
    chart.category_axis.tick_labels.font.size = Pt(style["table_size"])


def _process_labels(obj: dict[str, Any]) -> list[str]:
    content = obj.get("content")
    nodes = content.get("nodes") if isinstance(content, dict) else None
    if not isinstance(nodes, list) or not nodes:
        raise ValueError(f"Process {obj.get('id')} requires non-empty nodes")
    labels = [str(node.get("label")) for node in nodes if isinstance(node, dict) and node.get("label") is not None]
    if len(labels) != len(nodes):
        raise ValueError(f"Process {obj.get('id')} requires a label for every node")
    return labels


def _add_routed_connector(
    slide: Any,
    start: Any,
    end: Any,
    *,
    route: str = "straight",
    feedback: bool = False,
    color: str = "2D3340",
    width_pt: float = 1.5,
) -> Any:
    """Add one native, endpoint-bound arrow using the requested route."""
    from lxml import etree
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_CONNECTOR
    from pptx.oxml.ns import qn
    from pptx.util import Pt

    connector_type = {
        "straight": MSO_CONNECTOR.STRAIGHT,
        "orthogonal": MSO_CONNECTOR.ELBOW,
        "curved": MSO_CONNECTOR.CURVE,
    }.get(route)
    if connector_type is None:
        raise ValueError(f"Unsupported connector route: {route}")

    start_x = start.left + start.width
    start_y = start.top + start.height // 2
    end_x = end.left
    end_y = end.top + end.height // 2
    if feedback:
        start_x = start.left + start.width // 2
        start_y = start.top + start.height
        end_x = end.left + end.width // 2
        end_y = end.top

    connector = slide.shapes.add_connector(
        connector_type,
        start_x,
        start_y,
        end_x,
        end_y,
    )
    connector.name = f"Connector:{route}"
    connector.line.color.rgb = RGBColor.from_string(color)
    connector.line.width = Pt(width_pt)
    connector.begin_connect(start, 3 if not feedback else 2)
    connector.end_connect(end, 1 if not feedback else 0)
    line_xml = connector.line._get_or_add_ln()
    tail_end = etree.Element(qn("a:tailEnd"))
    tail_end.set("type", "triangle")
    line_xml.append(tail_end)
    return connector


def _add_process(slide: Any, obj: dict[str, Any], *, x: float, y: float, w: float, h: float, style: dict[str, Any]) -> None:
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.util import Inches, Pt

    labels = _process_labels(obj)
    total_width = max(w, 5.8)
    gap = 0.28
    node_width = (total_width - gap * (len(labels) - 1)) / len(labels)
    shapes = []
    for index, label in enumerate(labels):
        left = x + index * (node_width + gap)
        shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(left), Inches(y), Inches(node_width), Inches(h))
        shape.name = f"Component:process:{obj.get('id') or 'primary'}:node:{index + 1:02d}"
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(style["surface"])
        shape.line.color.rgb = RGBColor.from_string(style["border"])
        shape.text = label
        shape.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        paragraph = shape.text_frame.paragraphs[0]
        paragraph.alignment = PP_ALIGN.CENTER
        for run in paragraph.runs:
            run.font.name = style["font_name"]
            run.font.size = Pt(
                max(18.0, style["body_size"] * 1.4)
                if h >= 2.0
                else style["body_size"]
            )
            run.font.color.rgb = RGBColor.from_string(style["text_primary"])
        shapes.append(shape)
    route = str(obj.get("connector_route") or "straight")
    for before, after in zip(shapes, shapes[1:]):
        _add_routed_connector(
            slide,
            before,
            after,
            route=route,
            color=style["primary"],
        )


def _add_table(slide: Any, obj: dict[str, Any], *, x: float, y: float, w: float, h: float, style: dict[str, Any]) -> None:
    from pptx.dml.color import RGBColor
    from pptx.util import Inches, Pt

    data = _table_data(obj)
    rows = max(len(data), 1)
    cols = max(len(row) for row in data) if data else 1
    compact = rows <= 3
    table_height = min(h, max(1.8, rows * 0.8)) if compact else h
    table_y = y + max(0.0, (h - table_height) / 2)
    table_shape = slide.shapes.add_table(
        rows,
        cols,
        Inches(x),
        Inches(table_y),
        Inches(w),
        Inches(table_height),
    )
    table_shape.name = f"Component:table:{obj.get('id') or 'primary'}"
    table = table_shape.table
    for row_index, row in enumerate(data):
        for col_index in range(cols):
            cell = table.cell(row_index, col_index)
            cell.text = row[col_index] if col_index < len(row) else ""
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor.from_string(style["primary"] if row_index == 0 else style["background"])
            for paragraph in cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(
                        max(13.0, style["table_size"])
                        if compact
                        else style["table_size"]
                    )
                    run.font.name = style["font_name"]
                    run.font.color.rgb = RGBColor.from_string(style["background"] if row_index == 0 else style["text_primary"])


def _hex(value: Any, default: str) -> str:
    if isinstance(value, str) and len(value.lstrip("#")) == 6:
        return value.lstrip("#").upper()
    return default


def _resolve_style(contract: dict[str, Any]) -> dict[str, Any]:
    colors = contract.get("colors") if isinstance(contract.get("colors"), dict) else {}
    typography = contract.get("typography") if isinstance(contract.get("typography"), dict) else {}
    grid = contract.get("grid") if isinstance(contract.get("grid"), dict) else {}
    title_sizes = typography.get("title_sizes_pt") if isinstance(typography.get("title_sizes_pt"), dict) else {}
    body_sizes = typography.get("body_sizes_pt") if isinstance(typography.get("body_sizes_pt"), dict) else {}
    footer_tokens = contract.get("footer_tokens") if isinstance(contract.get("footer_tokens"), dict) else {}
    fonts = typography.get("font_primary") if isinstance(typography.get("font_primary"), list) else []
    return {
        "background": _hex(colors.get("background"), "FFFFFF"), "primary": _hex(colors.get("primary"), "2D3340"),
        "surface": _hex(colors.get("surface_1"), "F4F1EA"), "border": _hex(colors.get("border"), "E4E0D7"),
        "text_primary": _hex(colors.get("text_primary"), "2D3340"), "text_secondary": _hex(colors.get("text_secondary"), "6E6A60"),
        "font_name": next((font for font in fonts if isinstance(font, str) and font not in {"sans-serif", "serif", "monospace"}), "Aptos"),
        "title_size": float(title_sizes.get("slide", 22)), "body_size": float(body_sizes.get("normal", 13)),
        "table_size": float(body_sizes.get("small", 10)), "footnote_size": float(body_sizes.get("footnote", 8.5)),
        "margin_left": float(grid.get("margin_left_in", 0.55)),
        "margin_top": float(grid.get("margin_top_in", 0.35)),
        "margin_bottom": float(grid.get("margin_bottom_in", 0.35)),
        "footer_enabled": bool(footer_tokens.get("enabled", False)),
        "footer_height": float(footer_tokens.get("height_in", 0.24)),
        "card_gap": _spacing_value(contract, "card_gap", 0.16),
    }


def _spacing_value(contract: dict[str, Any], rule: str, default: float) -> float:
    spacing = contract.get("spacing") if isinstance(contract.get("spacing"), dict) else {}
    rules = spacing.get("rules") if isinstance(spacing.get("rules"), dict) else {}
    scale = spacing.get("scale") if isinstance(spacing.get("scale"), dict) else {}
    token = rules.get(rule)
    value = scale.get(token) if isinstance(token, str) else None
    return float(value) if isinstance(value, (int, float)) else default


def _unsupported_style_warnings(contract: dict[str, Any]) -> list[str]:
    spacing = contract.get("spacing") if isinstance(contract.get("spacing"), dict) else {}
    rules = spacing.get("rules") if isinstance(spacing.get("rules"), dict) else {}
    card_gap_token = rules.get("card_gap")
    consumed_scale = {card_gap_token: True} if isinstance(card_gap_token, str) else {}
    consumed_paths: dict[str, Any] = {
        "colors": {
            "background": True,
            "primary": True,
            "surface_1": True,
            "border": True,
            "text_primary": True,
            "text_secondary": True,
        },
        "typography": {
            "font_primary": True,
            "title_sizes_pt": {"slide": True},
            "body_sizes_pt": {"normal": True, "small": True, "footnote": True},
        },
        "grid": {"margin_left_in": True, "margin_top_in": True, "margin_bottom_in": True},
        "footer_tokens": True,
        "spacing": {
            "scale": consumed_scale,
            "rules": {"card_gap": True},
        },
    }
    warning_paths: list[str] = []
    _collect_unconsumed_style_paths(contract, consumed_paths, "", warning_paths)
    return [f"Unsupported style field ignored by PythonPptxAdapter: {path}" for path in sorted(set(warning_paths))]


def _collect_unconsumed_style_paths(value: Any, consumed_paths: Any, prefix: str, warnings: list[str]) -> None:
    if consumed_paths is True:
        return
    if isinstance(value, dict):
        if not value and prefix:
            warnings.append(prefix)
            return
        support = consumed_paths if isinstance(consumed_paths, dict) else {}
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            _collect_unconsumed_style_paths(child, support.get(key), path, warnings)
        return
    if prefix:
        warnings.append(prefix)
