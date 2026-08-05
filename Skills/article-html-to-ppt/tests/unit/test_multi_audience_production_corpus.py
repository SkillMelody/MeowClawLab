from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from visual_narrative.audience_router import route_audience


CORPUS = ROOT / "tests" / "fixtures" / "multi-audience-production" / "source-context-briefs.json"


def test_production_corpus_has_one_complete_brief_per_professional_route() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))

    assert corpus["schema_version"] == "1.0"
    cases = corpus["cases"]
    assert len(cases) == 8
    assert {case["expected_route"] for case in cases} == {
        "strategic_decision",
        "investor_commercial",
        "product_prd",
        "technical_architecture",
        "project_governance",
        "research_insight",
        "education_explanation",
        "brand_content_communication",
    }
    for case in cases:
        assert case["sources"]
        assert case["evidence_policy"]["data_status"] in {"quantitative", "qualitative_only", "internal_nonquantitative"}
        decision = route_audience(case["brief"])
        assert decision["status"] == "ready"
        assert decision["selected_route"] == case["expected_route"]
