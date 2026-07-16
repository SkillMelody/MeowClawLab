from __future__ import annotations

import importlib.metadata
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
                "native_chart": False,
                "native_connector": "partial",
                "svg_embed": False,
                "speaker_notes": False,
                "theme": "partial",
                "slide_master": "partial",
                "readback": True,
            },
            warnings=[] if available else ["python-pptx package is not importable."],
        )

    def supports(self, component_type: str, delivery_route: str) -> SupportLevel:
        if delivery_route in {"native_ppt", "native_table"}:
            return "full"
        if delivery_route in {"native_chart", "native_diagram"}:
            return "partial"
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
            slides.append(slide_plan)
        return BuildPlan(builder=self.name, slides=slides)

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
        presentation = Presentation()
        presentation.slide_width = Inches(13.333)
        presentation.slide_height = Inches(7.5)
        blank_layout = presentation.slide_layouts[6]

        object_results: list[dict[str, Any]] = []
        fallbacks: list[dict[str, Any]] = []
        warnings: list[str] = []

        for slide_plan in build_plan.slides:
            slide = presentation.slides.add_slide(blank_layout)
            _add_textbox(
                slide,
                slide_plan.get("title") or "Untitled",
                x=0.55,
                y=0.35,
                w=12.2,
                h=0.45,
                font_size=22,
                bold=True,
                color="2D3340",
            )
            body_parts = [part for part in [slide_plan.get("judgment"), slide_plan.get("message")] if isinstance(part, str) and part.strip()]
            body = "\n".join(body_parts)
            if body:
                _add_textbox(slide, body, x=0.7, y=1.05, w=11.7, h=0.5, font_size=13, color="6E6A60")
            objects = slide_plan.get("objects", []) or []
            if not objects:
                continue
            card_width = max(2.6, min(3.6, 10.8 / max(len(objects), 1)))
            for index, obj in enumerate(objects):
                route = ((obj.get("delivery_plan") or {}).get("selected_route") or obj.get("delivery_preferences", {}).get("preferred_route") or "native_ppt")
                actual_route = route
                if route in {"native_chart", "native_diagram", "hybrid_overlay", "svg_component", "generated_image", "background_image"}:
                    actual_route = "native_ppt"
                    fallbacks.append(
                        {
                            "slide_id": slide_plan.get("id"),
                            "object_id": obj.get("id"),
                            "component_type": obj.get("component_type") or obj.get("type"),
                            "planned_route": route,
                            "actual_route": actual_route,
                            "reason_codes": ["PYTHON_PPTX_MINIMAL_NATIVE_FALLBACK"],
                            "editable_core_preserved": obj.get("editability") != "native_required",
                        }
                    )
                x = 0.8 + index * (card_width + 0.22)
                y = 1.85
                if route == "native_table" or obj.get("type") == "table":
                    _add_table(slide, obj, x=x, y=y, w=min(10.8, card_width * 2), h=2.3)
                else:
                    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(card_width), Inches(1.35))
                    shape.fill.solid()
                    shape.fill.fore_color.rgb = RGBColor(244, 241, 234)
                    shape.line.color.rgb = RGBColor(228, 224, 215)
                    text_frame = shape.text_frame
                    text_frame.clear()
                    paragraph = text_frame.paragraphs[0]
                    run = paragraph.add_run()
                    run.text = _object_text(obj)
                    run.font.size = Pt(12)
                    run.font.color.rgb = RGBColor(45, 51, 64)
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


def _add_textbox(slide: Any, text: str, *, x: float, y: float, w: float, h: float, font_size: int, color: str, bold: bool = False) -> None:
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
    run.font.color.rgb = RGBColor.from_string(color)


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


def _add_table(slide: Any, obj: dict[str, Any], *, x: float, y: float, w: float, h: float) -> None:
    from pptx.util import Inches, Pt

    data = _table_data(obj)
    rows = max(len(data), 1)
    cols = max(len(row) for row in data) if data else 1
    table_shape = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    table = table_shape.table
    for row_index, row in enumerate(data):
        for col_index in range(cols):
            cell = table.cell(row_index, col_index)
            cell.text = row[col_index] if col_index < len(row) else ""
            for paragraph in cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)
