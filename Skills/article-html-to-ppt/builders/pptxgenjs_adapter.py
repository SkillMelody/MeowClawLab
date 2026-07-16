from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import BuildInspection, BuildPlan, BuildResult, BuilderCapability, SupportLevel


class PptxGenJsAdapter:
    name = "pptxgenjs"

    def probe(self) -> BuilderCapability:
        return BuilderCapability(
            name=self.name,
            available=False,
            features={
                "native_text": True,
                "native_table": True,
                "native_chart": True,
                "native_connector": True,
                "svg_embed": True,
                "speaker_notes": True,
                "theme": "partial",
                "slide_master": "partial",
                "readback": False,
            },
        )

    def supports(self, component_type: str, delivery_route: str) -> SupportLevel:
        if delivery_route in {"native_ppt", "native_chart", "native_table", "native_diagram"}:
            return "partial" if delivery_route == "native_diagram" else "full"
        if delivery_route in {"svg_component", "hybrid_overlay", "generated_image", "background_image"}:
            return "visual_only"
        return "unsupported"

    def plan(self, ppt_ir: dict[str, Any], style_contract: dict[str, Any], delivery_plan: dict[str, Any]) -> BuildPlan:
        slides = []
        for slide in delivery_plan.get("slides", []) or []:
            slides.append(
                {
                    "slide_id": slide.get("slide_id"),
                    "objects": [
                        {
                            "object_id": obj.get("object_id"),
                            "route": obj.get("selected_route"),
                            "adapter_component": "PptxGenJsObject",
                        }
                        for obj in slide.get("objects", []) or []
                    ],
                }
            )
        return BuildPlan(builder=self.name, slides=slides)

    def build(self, build_plan: BuildPlan, output_dir: Path) -> BuildResult:
        return BuildResult(builder=self.name, status="failed", errors=["BUILDER_RUNTIME_NOT_IMPLEMENTED"])

    def inspect_output(self, pptx_path: Path) -> BuildInspection:
        return BuildInspection(builder=self.name, status="not_run")
