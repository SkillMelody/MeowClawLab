import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from decision_support.frameworks.value_gate import ValueGateFramework
from decision_support.model import (
    AnalysisMode, Assumption, ConfidenceLevel, DecisionCase, DecisionQuestion, DecisionType,
    EvidenceItem, EvidenceKind, FreshnessStatus, RecommendationStatus,
)


FIXTURES = Path(__file__).parent / "fixtures" / "decision"


def make_case(name, mutate=None):
    payload = json.loads((FIXTURES / name).read_text())
    if mutate:
        mutate(payload)
    evidence = tuple(
        EvidenceItem(
            id=f"e-{key}", claim=key, value=Decimal("1"), kind=EvidenceKind.FACT,
            confidence=ConfidenceLevel.HIGH, freshness=FreshnessStatus.CURRENT,
        )
        for key in ("benefit", "cash-flows", "constraints")
    )
    option_ids = tuple(payload.get("options", {}))
    question = DecisionQuestion(
        id="q-value", decision_type=DecisionType.VALUE,
        question="Continue, pivot, or stop?", owner="SteerCo",
        decision_date=date(2026, 7, 25), horizon="2 years",
        requested_analysis_mode=AnalysisMode.PRESCRIPTIVE,
        option_ids=option_ids, baseline_id="stop" if "stop" in option_ids else None,
    )
    return DecisionCase(
        id="case-value", question=question, evidence=evidence,
        assumptions=(Assumption(
            id="a-discount", statement="Discount rate remains appropriate", owner="CFO",
            review_date=date(2026, 8, 25), trigger="Cost of capital changes",
        ),),
        option_ids=option_ids, extensions={"value_gate": payload},
    )


def calculations(result):
    return {item.id: item.value for item in result.calculations}


def test_direction_normalization_uses_current_period_plan_and_forecast_gap():
    framework = ValueGateFramework()
    increase = calculations(framework.analyze(make_case("value-continue.json")))
    decrease = calculations(framework.analyze(make_case("value-pivot.json")))
    assert increase["benefit_realization"] == Decimal("1.2")
    assert increase["forecast_gap"] == Decimal("5")
    assert decrease["benefit_realization"] == Decimal("0.8")
    assert decrease["forecast_gap"] == Decimal("-8")


def test_invalid_target_uplift_is_blocking_validation():
    case = make_case("value-continue.json", lambda p: p["benefit"].update(target="100"))
    report = ValueGateFramework().validate_evidence(case)
    assert not report.valid
    assert "invalid_target_uplift" in report.reason_codes


def test_npv_is_future_only_relative_to_stop_and_reports_roi_and_sunk_cost():
    result = ValueGateFramework().analyze(make_case("value-continue.json"))
    calc = calculations(result)
    assert calc["npv-continue"] == Decimal("100.4132231404958677685950413")
    assert calc["npv-incremental-continue"] == Decimal("111.3223140495867768595041322")
    assert calc["incremental_roi-continue"] == Decimal("3.848484848484848484848484848")
    assert "sunk_cost_excluded:continue:90" in result.diagnostics


def test_missing_stop_and_cost_of_delay_double_count_are_blocking():
    missing = ValueGateFramework().assess_sufficiency(make_case("value-insufficient.json"))
    assert not missing.sufficient and "stop_option_missing" in missing.reason_codes

    def duplicate(payload):
        payload["options"]["continue"]["cash_flows"][1].update(cost_of_delay="4", cost_includes_delay=True)
    duplicate_case = make_case("value-continue.json", duplicate)
    assert "cost_of_delay_double_count" in ValueGateFramework().validate_evidence(duplicate_case).reason_codes


def test_hard_constraints_are_a_gate_and_stop_can_win():
    framework = ValueGateFramework()
    case = make_case("value-stop.json")
    result = framework.analyze(case)
    recommendation = framework.build_recommendation(case, result, framework.run_sensitivity(case, result))
    assert "gate_hard_constraints:pivot:fail" in result.diagnostics
    assert recommendation.status is RecommendationStatus.RECOMMEND
    assert recommendation.selected_option_ids == ("stop",)
    assert recommendation.binding_constraints == ("funding-cap",)


def test_policy_gates_are_sequential_and_can_defer_or_condition():
    framework = ValueGateFramework()
    insufficient_case = make_case("value-insufficient.json")
    insufficient_result = framework.analyze(insufficient_case)
    insufficient_rec = framework.build_recommendation(insufficient_case, insufficient_result, ())
    assert insufficient_rec.status is RecommendationStatus.NO_RECOMMENDATION
    assert "gate_evidence_sufficiency:fail" in insufficient_result.diagnostics
    assert any("PPTSmith policy" in item for item in insufficient_result.limitations)

    conditional_case = make_case("value-continue.json", lambda p: p.update(confidence="medium"))
    conditional_result = framework.analyze(conditional_case)
    conditional_rec = framework.build_recommendation(
        conditional_case, conditional_result, framework.run_sensitivity(conditional_case, conditional_result)
    )
    assert conditional_rec.status is RecommendationStatus.CONDITIONAL
    assert "gate_sensitivity:pass" in conditional_result.diagnostics


def test_low_confidence_defers_and_materially_indistinguishable_options_have_no_clear_winner():
    framework = ValueGateFramework()
    low_case = make_case("value-continue.json", lambda p: p.update(confidence="low"))
    low_result = framework.analyze(low_case)
    assert framework.build_recommendation(low_case, low_result, framework.run_sensitivity(low_case, low_result)).status is RecommendationStatus.DEFER

    def close_options(payload):
        payload["policy"]["materiality_threshold"] = "1000"
    close_case = make_case("value-continue.json", close_options)
    close_result = framework.analyze(close_case)
    recommendation = framework.build_recommendation(close_case, close_result, framework.run_sensitivity(close_case, close_result))
    assert recommendation.status is RecommendationStatus.NO_RECOMMENDATION
    assert "No clear winner" in recommendation.statement


def test_named_one_way_sensitivity_reports_flip_threshold_and_reasonable_flip():
    framework = ValueGateFramework()
    case = make_case("value-pivot.json")
    result = framework.analyze(case)
    sensitivity = framework.run_sensitivity(case, result)
    assert sensitivity[0].variable == "pivot delivery"
    assert "flip threshold" in sensitivity[0].conclusion
    assert "continue" in sensitivity[0].low_case
    assert "pivot" in sensitivity[0].high_case


def test_explain_and_protocol_surface_are_complete():
    framework = ValueGateFramework()
    case = make_case("value-continue.json")
    result = framework.analyze(case)
    assert framework.framework_id == "value_gate"
    assert framework.decision_types == frozenset({DecisionType.VALUE})
    assert framework.explain(result).steps
    assert ValueGateFramework().build_recommendation(case, result, framework.run_sensitivity(case, result)).counterarguments
