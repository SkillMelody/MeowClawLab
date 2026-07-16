from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_ROOT = Path(__file__).resolve().parent
QA_GENERATOR = ROOT / "tests" / "fixtures" / "qa" / "generate_fixtures.py"


def load_qa_generator() -> Any:
    spec = importlib.util.spec_from_file_location("qa_fixture_generator", str(QA_GENERATOR))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules["qa_fixture_generator"] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def write_reference_rubric(path: Path, case_id: str, scores: list[int]) -> None:
    dimensions = [
        "title_role_and_message_quality",
        "content_fidelity",
        "expression_architecture",
        "page_composition",
        "component_craft",
        "editability_hygiene",
    ]
    write_json(
        path,
        {
            "schema_version": "1.0",
            "case_id": case_id,
            "scorer": {"type": "human_reference", "name": "benchmark-fixture", "version": "1.0"},
            "dimensions": [
                {
                    "dimension": dimension,
                    "score": score,
                    "evidence": [f"Fixture baseline evidence for {dimension}."],
                    "confidence": 0.85,
                }
                for dimension, score in zip(dimensions, scores)
            ],
            "notes": ["Reference rubric is fixture-authored for deterministic benchmark tests."],
        },
    )


def build_manifest(case_id: str, profile: str, status: str = "verified") -> dict[str, Any]:
    return {
        "schema_version": "2.0",
        "build_id": f"{case_id}-baseline-001",
        "deck_id": case_id,
        "benchmark_case_id": case_id,
        "profile": profile,
        "builder": "fixture",
        "builder_profile": "deterministic-fixture",
        "status": status,
        "contract_refs": {
            "ppt_ir": "../expected-ppt-ir.json",
            "style_contract": "../expected-style-contract.json",
            "asset_manifest": "asset-manifest.json",
            "delivery_plan": None,
            "qa_report": "qa-report.json",
        },
        "stages": {"fixture": {"status": "complete"}},
        "outputs": {"deck": "deck.pptx", "qa_report": "qa-report.json"},
        "metrics": {},
        "warnings": [],
        "errors": [],
    }


def make_case(
    qa: Any,
    *,
    case_id: str,
    title: str,
    category: str,
    source: str,
    requirements: dict[str, Any],
    primary_expression: str,
    profile: str = "premium",
    scores: list[int] | None = None,
    baseline_builder: Callable[[Path], None] | None = None,
    expected_metrics: dict[str, Any] | None = None,
) -> None:
    case_dir = BENCHMARK_ROOT / case_id
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)
    (case_dir / "source.md").write_text(source.strip() + "\n", encoding="utf-8")
    write_json(case_dir / "requirements.json", requirements)
    (case_dir / "expected-content-lock.md").write_text(
        f"# Content Lock\n\n- Case: {case_id}\n- Required expression: {primary_expression}\n- Claims must stay sourced and editable.\n",
        encoding="utf-8",
    )
    ppt_ir = qa.base_ppt_ir(slide_count=1, primary_expression=primary_expression)
    ppt_ir["deck"]["id"] = case_id
    ppt_ir["deck"]["title"] = title
    ppt_ir["deck"]["production_profile"] = profile
    ppt_ir["slides"][0]["primary_anchor"] = requirements.get("primary_anchor", "body")
    write_json(case_dir / "expected-ppt-ir.json", ppt_ir)
    style = dict(qa.STYLE)
    style["style_id"] = requirements.get("style_id", "qa-style")
    style["display_name"] = requirements.get("style_name", "Benchmark Fixture Style")
    write_json(case_dir / "expected-style-contract.json", style)
    write_reference_rubric(case_dir / "reference-rubric.json", case_id, scores or [3, 3, 3, 2, 2, 3])
    write_json(case_dir / "expected-metrics.json", expected_metrics or {"source_coverage_ratio": 0.9, "primary_expression_missing_count": 0})
    write_json(case_dir / "anti-patterns.json", {"forbidden": requirements.get("anti_patterns", ["generic_topic_title", "whole_slide_raster"])})
    case = {
        "schema_version": "1.0",
        "case_id": case_id,
        "title": title,
        "category": category,
        "source_files": ["source.md"],
        "requirements_file": "requirements.json",
        "expected_content_lock": "expected-content-lock.md",
        "expected_ppt_ir": "expected-ppt-ir.json",
        "expected_style_contract": "expected-style-contract.json",
        "reference_rubric": "reference-rubric.json",
        "anti_patterns": "anti-patterns.json",
        "expected_metrics": expected_metrics or {"source_coverage_ratio": 0.9, "primary_expression_missing_count": 0},
        "allowed_variations": {"slide_count_delta": 1},
        "profile": profile,
        "builder": "auto",
        "renderer": "auto",
    }
    if baseline_builder is not None:
        baseline = case_dir / "baseline"
        baseline.mkdir()
        baseline_builder(baseline)
        for extra in ["ppt-ir.json", "style-contract.json", "delivery-plan.json", "expected-issues.json"]:
            extra_path = baseline / extra
            if extra_path.exists():
                extra_path.unlink()
        write_json(baseline / "build-manifest.json", build_manifest(case_id, profile))
        case["baseline"] = {
            "deck": "baseline/deck.pptx",
            "qa_report": "baseline/qa-report.json",
            "build_manifest": "baseline/build-manifest.json",
        }
    write_json(case_dir / "case.json", case)


def main() -> None:
    qa = load_qa_generator()
    for item in BENCHMARK_ROOT.iterdir():
        if item.name == "generate_fixtures.py":
            continue
        if item.is_dir():
            shutil.rmtree(item)
    make_case(
        qa,
        case_id="editorial-skill-article",
        title="Skill Article Editorial Deck",
        category="editorial_article",
        source="A skill article explains why reusable agent skills need contracts, examples, and verification.",
        requirements={"expected_judgment_title": "Reusable skills need contracts, examples, and verification", "expected_message": "The deck must transform the article into an editorial argument.", "style_id": "editorial-knowledge"},
        primary_expression="textual_argument",
        baseline_builder=qa.save_valid,
    )
    make_case(
        qa,
        case_id="editorial-longform-opinion",
        title="Longform Opinion Synthesis",
        category="editorial_article",
        source="A long opinion argues that automation succeeds when judgment remains visible.",
        requirements={"expected_judgment_title": "Automation lands when judgment remains visible", "expected_message": "Preserve the argument and cite caveats.", "style_id": "editorial-knowledge"},
        primary_expression="textual_argument",
        baseline_builder=qa.save_valid,
    )
    make_case(
        qa,
        case_id="product-quarterly-review",
        title="Product Quarterly Review",
        category="product_report",
        source="Quarterly product metrics show adoption, retention risk, and a need to sequence roadmap bets.",
        requirements={"expected_judgment_title": "Adoption improved, but retention risk should set the roadmap", "expected_message": "KPI and decision evidence must remain editable.", "style_id": "product-report"},
        primary_expression="data_visual",
        baseline_builder=qa.save_valid,
    )
    make_case(
        qa,
        case_id="product-roadmap-decision",
        title="Roadmap Decision Memo",
        category="product_report",
        source="A roadmap memo compares three bets by effort, confidence, and customer impact.",
        requirements={"expected_judgment_title": "The low-risk retention bet should ship before expansion", "expected_message": "Comparison and next action must be explicit.", "style_id": "product-report"},
        primary_expression="table_matrix",
        baseline_builder=qa.save_valid,
    )
    make_case(
        qa,
        case_id="technical-agent-architecture",
        title="Agent System Architecture",
        category="technical_agent",
        source="The agent system separates planner, tool router, memory, and execution sandbox with permission gates.",
        requirements={"expected_judgment_title": "Permission boundaries define the agent architecture", "expected_message": "The architecture must show layers and trust boundaries.", "style_id": "technical-blueprint"},
        primary_expression="relationship_visual",
        baseline_builder=qa.save_complex_diagram,
    )
    make_case(
        qa,
        case_id="technical-harness-failure-recovery",
        title="Harness Failure Recovery",
        category="technical_agent",
        source="The verification harness distinguishes renderer unavailability, structural QA errors, and repair loops.",
        requirements={"expected_judgment_title": "Recovery depends on separating unavailable renderers from QA failures", "expected_message": "Failure modes must not be collapsed into one status.", "style_id": "technical-blueprint"},
        primary_expression="relationship_visual",
        baseline_builder=qa.save_complex_diagram,
    )
    make_case(
        qa,
        case_id="design-spec-product-template",
        title="Product Template Design Spec",
        category="design_spec",
        source="A detailed design spec defines priorities, not just coordinates.",
        requirements={"expected_judgment_title": "Design specs should preserve priority, not literal coordinates", "expected_message": "Visual priority and editable overlays must be explicit.", "style_id": "consulting-light"},
        primary_expression="structured_cards",
        baseline_builder=qa.save_valid,
    )
    make_case(
        qa,
        case_id="design-spec-technical-blueprint",
        title="Technical Blueprint Spec",
        category="design_spec",
        source="A blueprint spec describes zones, annotations, and asset boundaries.",
        requirements={"expected_judgment_title": "Blueprint fidelity comes from zones and boundaries", "expected_message": "Do not mechanically copy every placeholder.", "style_id": "technical-blueprint"},
        primary_expression="relationship_visual",
        baseline_builder=qa.save_complex_diagram,
    )
    make_case(
        qa,
        case_id="anti-regression-card-overuse",
        title="Card Overuse Regression",
        category="anti_regression",
        source="A system dependency story is often flattened into equal cards.",
        requirements={"expected_judgment_title": "Dependencies should not be flattened into equal cards", "expected_message": "The benchmark should catch relationship-to-card regression.", "anti_patterns": ["relationship_to_cards_regression"]},
        primary_expression="relationship_visual",
        scores=[3, 3, 2, 2, 2, 3],
        expected_metrics={"relationship_to_cards_regression_count": 0, "source_coverage_ratio": 0.9},
    )
    make_case(
        qa,
        case_id="anti-regression-whole-slide-raster",
        title="Whole Slide Raster Regression",
        category="anti_regression",
        source="A polished visual must not hide title, labels, and core data in one uneditable image.",
        requirements={"expected_judgment_title": "Whole-slide raster hides the editable message", "expected_message": "The benchmark should require bounded raster disclosure.", "anti_patterns": ["whole_slide_raster", "rasterized_core_text"]},
        primary_expression="conceptual_scene",
        scores=[3, 3, 2, 2, 2, 2],
        expected_metrics={"whole_slide_raster_count": 0, "source_coverage_ratio": 0.9},
    )


if __name__ == "__main__":
    main()
