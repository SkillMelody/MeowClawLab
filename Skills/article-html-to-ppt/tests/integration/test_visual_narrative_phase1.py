from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "scripts" / "run_pipeline.py"
FIXTURES = ROOT / "tests" / "fixtures" / "v2-acceptance"


def write_json(path: Path, document: dict) -> None:
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_source_context_brief(tmp_path: Path, route: str) -> Path:
    if route == "product_prd":
        document = {
            "schema_version": "1.0",
            "source_id": "prd-fixture",
            "primary_audience": ["product_manager", "engineer", "designer", "tester"],
            "delivery_objective": "review_and_align",
            "source_material_type": "prd",
            "evidence_profile": ["scope_boundary", "user_flow", "acceptance_criteria"],
            "industry_compliance_context": ["consumer_software"],
            "delivery_scenario": "prd_review",
        }
    else:
        document = {
            "schema_version": "1.0",
            "source_id": "research-fixture",
            "primary_audience": ["analyst"],
            "delivery_objective": "communicate_findings",
            "source_material_type": "research_report",
            "evidence_profile": ["statistics", "comparison", "trend"],
            "industry_compliance_context": [],
            "delivery_scenario": "insight_briefing",
        }
    path = tmp_path / "source-context-brief.json"
    write_json(path, document)
    return path


def storyline(*, request_revision: bool = False, professional_route: str = "research_insight") -> dict:
    slides = [
        ("S01", "cover", [], "supporting"),
        ("S02", "relationship", ["hierarchy", "drill_down"], "supporting"),
        ("S03", "data", [], "key"),
        ("S04", "architecture", ["layer", "system_boundary"], "supporting"),
        ("S05", "data", [], "supporting"),
        ("S06", "diagram", ["phase", "milestone"], "key"),
        ("S07", "comparison", [], "supporting"),
        ("S08", "roadmap", ["phase", "roadmap"], "supporting"),
        ("S09", "closing", [], "supporting"),
    ]
    sequences = {
        "research_insight": ["research_question", "evidence_and_findings", "implications_and_actions"],
        "product_prd": ["problem_and_scope", "user_flow_and_rules", "acceptance_and_open_questions"],
    }
    sequence = sequences[professional_route]
    document = {
        "title": "PPTSmith 视觉叙事验收",
        "slides": [
            {
                "id": slide_id,
                "role": role,
                "message": f"{slide_id} 的判断信息保持不变。",
                "evidence_refs": [{"source_id": "src-001", "locator": slide_id}],
                "relationships": relationships,
                "priority": priority,
                "narrative_stage": sequence[min(index * len(sequence) // len(slides), len(sequence) - 1)],
            }
            for index, (slide_id, role, relationships, priority) in enumerate(slides)
        ],
    }
    if request_revision:
        document["revision_observations"] = [
            {"slide_id": "S03", "codes": ["VISUAL_WEAK_PRIMARY_ANCHOR"]}
        ]
    return document


def run_phase1_pipeline(tmp_path: Path, *, request_revision: bool = False) -> subprocess.CompletedProcess[str]:
    content_analysis = tmp_path / "content-analysis.json"
    storyline_path = tmp_path / "storyline.json"
    write_json(
        content_analysis,
        {
            "evidence_types": ["statistics", "comparison", "trend"],
            "relationship_types": ["hierarchy"],
        },
    )
    write_json(storyline_path, storyline(request_revision=request_revision))
    brief_path = write_source_context_brief(tmp_path, "research_insight")
    return subprocess.run(
        [
            sys.executable,
            str(PIPELINE),
            "--requirements",
            str(FIXTURES / "requirements-fast.json"),
            "--ppt-ir",
            str(FIXTURES / "ppt-ir.json"),
            "--style",
            str(FIXTURES / "style-contract-editorial.json"),
            "--content-analysis",
            str(content_analysis),
            "--storyline",
            str(storyline_path),
            "--source-context-brief",
            str(brief_path),
            "--builder",
            "auto",
            "--profile",
            "fast",
            "--work-dir",
            str(tmp_path / ".ppt-work"),
            "--output-dir",
            str(tmp_path / "delivery"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_visual_narrative_stages_run_before_delivery_resolution(tmp_path: Path) -> None:
    completed = run_phase1_pipeline(tmp_path)

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    state = load_json(work / "state.json")
    assert state["stage_order"].index("route_task") < state["stage_order"].index(
        "resolve_delivery"
    )
    assert state["stage_order"].index("plan_visual_narrative") < state[
        "stage_order"
    ].index("build")
    assert state["stage_order"].index("deck_rhythm") < state["stage_order"].index(
        "build"
    )
    assert state["visual_revision_count"] == 0
    for name in (
        "task-route.json",
        "visual-plan.json",
        "deck-rhythm-report.json",
        "visual-revision-request.json",
    ):
        assert (work / "contracts" / name).is_file()
    task_route = load_json(work / "contracts" / "task-route.json")
    assert task_route["selected_route"] == "research_report"
    assert "product_prd" in task_route["rejected_routes"]


def test_visual_plan_is_compiled_into_ppt_ir_before_delivery_resolution(
    tmp_path: Path,
) -> None:
    completed = run_phase1_pipeline(tmp_path)

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    state = load_json(work / "state.json")
    ppt_ir = load_json(work / "contracts" / "ppt-ir.json")
    delivery = load_json(work / "contracts" / "delivery-plan.json")

    assert state["stage_order"].index("compile_visual_plan") < state["stage_order"].index(
        "resolve_delivery"
    )
    slide = next(item for item in ppt_ir["slides"] if item["id"] == "S06")
    assert slide["primary_expression"] == "relationship_visual"
    assert slide["objects"][0]["component_type"] == "phase_roadmap"
    assert slide["objects"][0]["delivery_preferences"] == {
        "preferred_route": "native_diagram",
        "allowed_fallbacks": [],
    }
    planned = next(item for item in delivery["slides"] if item["slide_id"] == "S06")
    assert planned["objects"][0]["component_type"] == "phase_roadmap"
    assert planned["objects"][0]["selected_route"] == "native_diagram"


def test_supported_relationship_components_are_compiled_to_verified_native_renderers(
    tmp_path: Path,
) -> None:
    document = storyline()
    document["slides"][1]["relationships"] = ["hierarchy", "drill_down"]
    content_analysis = tmp_path / "content-analysis.json"
    storyline_path = tmp_path / "storyline.json"
    write_json(content_analysis, {"evidence_types": ["statistics"], "relationship_types": ["hierarchy"]})
    write_json(storyline_path, document)
    brief_path = write_source_context_brief(tmp_path, "research_insight")

    completed = subprocess.run(
        [
            sys.executable, str(PIPELINE), "--requirements", str(FIXTURES / "requirements-fast.json"),
            "--ppt-ir", str(FIXTURES / "ppt-ir.json"), "--style", str(FIXTURES / "style-contract-editorial.json"),
            "--content-analysis", str(content_analysis), "--storyline", str(storyline_path),
            "--source-context-brief", str(brief_path), "--builder", "python_pptx", "--profile", "fast",
            "--work-dir", str(tmp_path / ".ppt-work"), "--output-dir", str(tmp_path / "delivery"),
        ],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    ppt_ir = load_json(work / "contracts" / "ppt-ir.json")
    delivery = load_json(work / "contracts" / "delivery-plan.json")
    for slide_id, component in (("S02", "drill_down_stair"),):
        slide = next(item for item in ppt_ir["slides"] if item["id"] == slide_id)
        assert slide["objects"][0]["component_type"] == component
        assert slide["objects"][0]["delivery_preferences"]["preferred_route"] == "native_diagram"
        planned = next(item for item in delivery["slides"] if item["slide_id"] == slide_id)
        assert planned["objects"][0]["component_type"] == component
        assert planned["objects"][0]["selected_route"] == "native_diagram"


def test_unsupported_relationship_visual_becomes_a_disclosed_native_placeholder(
    tmp_path: Path,
) -> None:
    document = storyline()
    document["slides"][1]["relationships"] = ["feedback_loop"]
    content_analysis = tmp_path / "content-analysis.json"
    storyline_path = tmp_path / "storyline.json"
    write_json(content_analysis, {"evidence_types": ["statistics"], "relationship_types": []})
    write_json(storyline_path, document)
    brief_path = write_source_context_brief(tmp_path, "research_insight")

    completed = subprocess.run(
        [
            sys.executable, str(PIPELINE), "--requirements", str(FIXTURES / "requirements-fast.json"),
            "--ppt-ir", str(FIXTURES / "ppt-ir.json"), "--style", str(FIXTURES / "style-contract-editorial.json"),
            "--content-analysis", str(content_analysis), "--storyline", str(storyline_path),
            "--source-context-brief", str(brief_path), "--builder", "python_pptx", "--profile", "fast",
            "--work-dir", str(tmp_path / ".ppt-work"), "--output-dir", str(tmp_path / "delivery"),
        ],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    ppt_ir = load_json(work / "contracts" / "ppt-ir.json")
    build = load_json(work / "contracts" / "build-manifest.json")
    slide = next(item for item in ppt_ir["slides"] if item["id"] == "S02")
    placeholder = slide["objects"][0]
    assert placeholder["component_type"] == "comparison_card"
    assert placeholder["component_status"] == "unsupported_placeholder"
    assert placeholder["content"]["title"] == "待补齐：关系图组件"
    assert "原生可编辑关系图" in placeholder["content"]["claim"]
    assert build["metrics"]["unsupported_placeholder_count"] == 1
    assert build["status"] == "verified"


def test_product_prd_evidence_is_consumed_before_delivery(tmp_path: Path) -> None:
    content_analysis = tmp_path / "content-analysis.json"
    storyline_path = tmp_path / "storyline.json"
    write_json(
        content_analysis,
        {
            "requested_route": "product_prd",
            "source_id": "prd-fixture",
            "ui_spaces": [{"name": "Canvas", "locator": "5"}],
            "interactions": [{"trigger": "select", "locator": "8.2"}],
        },
    )
    write_json(storyline_path, storyline(professional_route="product_prd"))
    brief_path = write_source_context_brief(tmp_path, "product_prd")
    completed = subprocess.run(
        [
            sys.executable, str(PIPELINE), "--requirements", str(FIXTURES / "requirements-fast.json"),
            "--ppt-ir", str(FIXTURES / "ppt-ir.json"), "--style", str(FIXTURES / "style-contract-editorial.json"),
            "--content-analysis", str(content_analysis), "--storyline", str(storyline_path),
            "--source-context-brief", str(brief_path),
            "--builder", "auto", "--profile", "fast", "--work-dir", str(tmp_path / ".ppt-work"),
            "--output-dir", str(tmp_path / "delivery"),
        ],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    evidence = load_json(tmp_path / ".ppt-work" / "contracts" / "design-evidence.json")
    assert evidence["status"] == "ready"
    assert evidence["blocking_codes"] == []
    assert evidence["coverage_matrix"]["product_ui_overview"]["consumed"] is True
    assert evidence["coverage_matrix"]["interaction_storyboard"]["consumed"] is True


def test_product_prd_evidence_is_injected_and_consumed_by_native_prototypes(
    tmp_path: Path,
) -> None:
    content_analysis = tmp_path / "content-analysis.json"
    storyline_path = tmp_path / "storyline.json"
    write_json(
        content_analysis,
        {
            "requested_route": "product_prd",
            "source_id": "prd-fixture",
            "ui_spaces": [{"name": "Canvas", "locator": "5"}],
            "interactions": [{"trigger": "select", "locator": "8.2"}],
        },
    )
    write_json(storyline_path, storyline(professional_route="product_prd"))
    brief_path = write_source_context_brief(tmp_path, "product_prd")
    completed = subprocess.run(
        [
            sys.executable, str(PIPELINE), "--requirements", str(FIXTURES / "requirements-fast.json"),
            "--ppt-ir", str(FIXTURES / "ppt-ir.json"), "--style", str(FIXTURES / "style-contract-editorial.json"),
            "--content-analysis", str(content_analysis), "--storyline", str(storyline_path),
            "--source-context-brief", str(brief_path),
            "--builder", "auto", "--profile", "fast", "--work-dir", str(tmp_path / ".ppt-work"),
            "--output-dir", str(tmp_path / "delivery"),
        ],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    evidence = load_json(work / "contracts" / "design-evidence.json")
    ppt_ir = load_json(work / "contracts" / "ppt-ir.json")
    delivery = load_json(work / "contracts" / "delivery-plan.json")
    assert delivery["builder"]["requested"] == "auto"
    assert delivery["builder"]["selected"] == "python_pptx"
    coverage = evidence["coverage_matrix"]
    assert coverage["product_ui_overview"] == {
        "required": True,
        "evidence_ids": ["ui_space-01"],
        "consumed": True,
        "consumer_object_ids": ["prd-product-ui-overview"],
    }
    assert coverage["interaction_storyboard"] == {
        "required": True,
        "evidence_ids": ["interaction-01"],
        "consumed": True,
        "consumer_object_ids": ["prd-interaction-storyboard"],
    }
    assert coverage["application_screenshot"] == {
        "required": True,
        "asset_status": "missing",
        "consumed": True,
        "consumer_object_ids": ["prd-product-ui-overview"],
        "placeholder": {
            "aspect_ratio": "16:10",
            "page_id": "S02",
            "region": "product_ui_overview.primary_visual",
        },
    }
    objects = [obj for slide in ppt_ir["slides"] for obj in slide.get("objects", [])]
    assert {obj["component_type"] for obj in objects} >= {
        "product_ui_overview",
        "interaction_storyboard",
    }
    product_slides = {slide["id"]: slide for slide in ppt_ir["slides"]}
    assert product_slides["S02"]["title"] == "产品工作台 UI 总览"
    assert product_slides["S02"]["message"] == "Canvas 是核心工作区；真实应用截图待补。"
    assert [obj["id"] for obj in product_slides["S02"]["objects"]] == ["prd-product-ui-overview"]
    # S02 spaces from content-analysis (only Canvas is provided as ui_space)
    s02_spaces = product_slides["S02"]["objects"][0]["content"]["spaces"]
    s02_labels = {s["label"] for s in s02_spaces}
    assert "Canvas" in s02_labels
    assert len(s02_spaces) == 1
    assert product_slides["S03"]["title"] == "工作台交互路径"
    assert product_slides["S03"]["message"] == "从节点选区到 AI 反馈、结果采纳及异常处理的完整路径。"
    assert [obj["id"] for obj in product_slides["S03"]["objects"]] == ["prd-interaction-storyboard"]
    s03_steps = product_slides["S03"]["objects"][0]["content"]["steps"]
    assert len(s03_steps) == 1
    assert s03_steps[0]["kind"] == "action"


def test_product_prd_forced_pptxgenjs_is_honestly_blocked(tmp_path: Path) -> None:
    content_analysis = tmp_path / "content-analysis.json"
    storyline_path = tmp_path / "storyline.json"
    write_json(
        content_analysis,
        {
            "requested_route": "product_prd",
            "source_id": "prd-fixture",
            "ui_spaces": [{"name": "Canvas", "locator": "5"}],
            "interactions": [{"trigger": "select", "locator": "8.2"}],
        },
    )
    write_json(storyline_path, storyline(professional_route="product_prd"))
    brief_path = write_source_context_brief(tmp_path, "product_prd")
    completed = subprocess.run(
        [
            sys.executable, str(PIPELINE), "--requirements", str(FIXTURES / "requirements-fast.json"),
            "--ppt-ir", str(FIXTURES / "ppt-ir.json"), "--style", str(FIXTURES / "style-contract-editorial.json"),
            "--content-analysis", str(content_analysis), "--storyline", str(storyline_path),
            "--source-context-brief", str(brief_path),
            "--builder", "pptxgenjs", "--profile", "fast", "--work-dir", str(tmp_path / ".ppt-work"),
            "--output-dir", str(tmp_path / "delivery"),
        ],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )

    assert completed.returncode != 0
    assert "BUILDER_COMPONENT_UNSUPPORTED" in completed.stderr
    state = load_json(tmp_path / ".ppt-work" / "state.json")
    assert state["failed_stage"] == "resolve_delivery"


def test_product_prd_without_design_evidence_does_not_inject_prototypes(tmp_path: Path) -> None:
    content_analysis = tmp_path / "content-analysis.json"
    storyline_path = tmp_path / "storyline.json"
    write_json(content_analysis, {"requested_route": "product_prd", "source_id": "minimal-prd"})
    write_json(storyline_path, storyline(professional_route="product_prd"))
    brief_path = write_source_context_brief(tmp_path, "product_prd")
    completed = subprocess.run(
        [
            sys.executable, str(PIPELINE), "--requirements", str(FIXTURES / "requirements-fast.json"),
            "--ppt-ir", str(FIXTURES / "ppt-ir.json"), "--style", str(FIXTURES / "style-contract-editorial.json"),
            "--content-analysis", str(content_analysis), "--storyline", str(storyline_path),
            "--source-context-brief", str(brief_path),
            "--builder", "python_pptx", "--profile", "fast", "--work-dir", str(tmp_path / ".ppt-work"),
            "--output-dir", str(tmp_path / "delivery"),
        ],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    evidence = load_json(work / "contracts" / "design-evidence.json")
    ppt_ir = load_json(work / "contracts" / "ppt-ir.json")
    # product_ui_overview is always required and injected even without ui_space evidence
    assert evidence["coverage_matrix"]["product_ui_overview"]["consumer_object_ids"] == ["prd-product-ui-overview"]
    assert evidence["coverage_matrix"]["interaction_storyboard"]["consumer_object_ids"] == []
    assert any(
        obj.get("component_type") == "product_ui_overview"
        for slide in ppt_ir["slides"]
        for obj in slide.get("objects", [])
    )
    assert all(
        obj.get("component_type") != "interaction_storyboard"
        for slide in ppt_ir["slides"]
        for obj in slide.get("objects", [])
    )


def test_visual_revision_is_applied_at_most_once_and_keeps_first_pass_evidence(
    tmp_path: Path,
) -> None:
    completed = run_phase1_pipeline(tmp_path, request_revision=True)

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    state = load_json(work / "state.json")
    request = load_json(work / "contracts" / "visual-revision-request.json")
    plan = load_json(work / "contracts" / "visual-plan.json")
    assert request["status"] == "revision_required"
    assert state["visual_revision_count"] == 1
    assert state["stage_order"].count("visual_revision") == 1
    assert (work / "revisions" / "initial" / "deck.pptx").is_file()
    revised_slide = next(slide for slide in plan["slides"] if slide["slide_id"] == "S03")
    assert revised_slide["revision"]["iteration"] == 1
    assert revised_slide["message"] == "S03 的判断信息保持不变。"
    assert revised_slide["evidence_refs"] == [
        {"source_id": "src-001", "locator": "S03"}
    ]
