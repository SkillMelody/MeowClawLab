from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Any, Mapping, Tuple

from ..model import (
    AnalysisMode,
    AnalysisResult,
    CalculationTrace,
    ConfidenceLevel,
    Counterargument,
    DecisionCase,
    DecisionType,
    ExplanationTrace,
    Finding,
    Recommendation,
    RecommendationStatus,
    ReviewTrigger,
    SensitivityResult,
    SufficiencyReport,
    ValidationIssue,
    ValidationReport,
)
from ..serialization import input_snapshot_sha256


_CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


def _decimal(value: Any, default: str = "0") -> Decimal:
    return Decimal(str(default if value is None else value))


class ValueGateFramework:
    framework_id = "value_gate"
    version = "1.0.0"
    decision_types = frozenset({DecisionType.VALUE})

    def _input(self, case: DecisionCase) -> Mapping[str, Any]:
        value = case.extensions.get("value_gate", {})
        return value if isinstance(value, Mapping) else {}

    def assess_sufficiency(self, case: DecisionCase) -> SufficiencyReport:
        data = self._input(case)
        missing = []
        benefit = data.get("benefit", {})
        for field in ("direction", "baseline", "target", "actual_to_date", "planned_to_date", "forecast"):
            if field not in benefit:
                missing.append(f"value_gate.benefit.{field}")
        options = data.get("options", {})
        if "stop" not in options:
            missing.append("value_gate.options.stop")
        for option_id, option in options.items():
            if "cash_flows" not in option:
                missing.append(f"value_gate.options.{option_id}.cash_flows")
            if "hard_constraints_met" not in option:
                missing.append(f"value_gate.options.{option_id}.hard_constraints_met")
        reasons = []
        if "value_gate.options.stop" in missing:
            reasons.append("stop_option_missing")
        if any(item != "value_gate.options.stop" for item in missing):
            reasons.append("critical_value_input_missing")
        return SufficiencyReport(not missing, tuple(missing), tuple(reasons))

    def validate_evidence(self, case: DecisionCase) -> ValidationReport:
        data = self._input(case)
        issues = []
        benefit = data.get("benefit", {})
        if all(field in benefit for field in ("direction", "baseline", "target")):
            direction = benefit["direction"]
            baseline, target = _decimal(benefit["baseline"]), _decimal(benefit["target"])
            valid = direction in ("increase", "decrease") and (
                (direction == "increase" and target > baseline)
                or (direction == "decrease" and target < baseline)
            )
            if not valid:
                issues.append(ValidationIssue("invalid_target_uplift", "target must improve from baseline in the declared direction", "value_gate.benefit.target"))
        for option_id, option in data.get("options", {}).items():
            for index, flow in enumerate(option.get("cash_flows", ())):
                if flow.get("cost_includes_delay") and _decimal(flow.get("cost_of_delay")) != 0:
                    issues.append(ValidationIssue("cost_of_delay_double_count", "cost of delay is already included in option cost", f"value_gate.options.{option_id}.cash_flows.{index}"))
        return ValidationReport(not issues, tuple(issues))

    def _policy(self, data: Mapping[str, Any]) -> tuple[Decimal, Decimal, str]:
        policy = data.get("policy", {})
        return (
            _decimal(policy.get("completeness_threshold"), "0.8"),
            _decimal(policy.get("materiality_threshold"), "0"),
            str(policy.get("confidence_threshold", "medium")),
        )

    def _option_npv(self, option: Mapping[str, Any], rate: Decimal, benefit_scale: Decimal = Decimal("1")) -> Decimal:
        total = Decimal("0")
        for flow in option.get("cash_flows", ()):
            period = int(flow.get("period", 0))
            if period <= 0:
                continue
            benefit = _decimal(flow.get("benefit")) * benefit_scale
            cost = _decimal(flow.get("cost"))
            delay = Decimal("0") if flow.get("cost_includes_delay") else _decimal(flow.get("cost_of_delay"))
            total += (benefit - cost - delay) / ((Decimal("1") + rate) ** period)
        return total

    def _winner(self, data: Mapping[str, Any], scale_option: str | None = None, scale: Decimal = Decimal("1")) -> str | None:
        options = data.get("options", {})
        if "stop" not in options:
            return None
        rate = _decimal(data.get("discount_rate"))
        feasible = {
            option_id: self._option_npv(option, rate, scale if option_id == scale_option else Decimal("1"))
            for option_id, option in options.items() if option.get("hard_constraints_met", True)
        }
        return max(feasible, key=feasible.get) if feasible else None

    def analyze(self, case: DecisionCase) -> AnalysisResult:
        data = self._input(case)
        validation = self.validate_evidence(case)
        sufficiency = self.assess_sufficiency(case)
        calculations = []
        diagnostics = ["gate_valid_question:pass" if validation.valid else "gate_valid_question:fail"]
        limitations = ["Completeness, materiality, and confidence thresholds are configurable PPTSmith policy."]
        benefit = data.get("benefit", {})
        if validation.valid and sufficiency.sufficient:
            direction = Decimal("1") if benefit["direction"] == "increase" else Decimal("-1")
            baseline = _decimal(benefit["baseline"])
            denominator = direction * (_decimal(benefit["planned_to_date"]) - baseline)
            realized = direction * (_decimal(benefit["actual_to_date"]) - baseline)
            realization = realized / denominator if denominator > 0 else None
            forecast_gap = direction * (_decimal(benefit["forecast"]) - _decimal(benefit["target"]))
            calculations.extend((
                CalculationTrace("benefit_realization", "direction * (actual_to_date - baseline) / current_should_realize", realization),
                CalculationTrace("forecast_gap", "direction * (forecast - target)", forecast_gap),
            ))
        elif not sufficiency.sufficient:
            diagnostics.append("gate_evidence_sufficiency:fail")

        options = data.get("options", {})
        failed_constraints = []
        for option_id, option in options.items():
            met = bool(option.get("hard_constraints_met", True))
            diagnostics.append(f"gate_hard_constraints:{option_id}:{'pass' if met else 'fail'}")
            if not met:
                failed_constraints.extend(option.get("constraint_ids", ()))
        rate = _decimal(data.get("discount_rate"))
        npvs = {option_id: self._option_npv(option, rate) for option_id, option in options.items()}
        stop_npv = npvs.get("stop")
        for option_id, option in options.items():
            calculations.append(CalculationTrace(f"npv-{option_id}", "sum future (benefit - cost - non-duplicated cost_of_delay) / (1 + discount_rate)^period", npvs[option_id]))
            sunk = sum((_decimal(flow.get("cost")) for flow in option.get("cash_flows", ()) if int(flow.get("period", 0)) <= 0), Decimal("0"))
            if sunk:
                diagnostics.append(f"sunk_cost_excluded:{option_id}:{sunk}")
            if option_id != "stop" and stop_npv is not None:
                calculations.append(CalculationTrace(f"npv-incremental-{option_id}", f"npv-{option_id} - npv-stop", npvs[option_id] - stop_npv))
                future_benefit = sum((_decimal(flow.get("benefit")) for flow in option.get("cash_flows", ()) if int(flow.get("period", 0)) > 0), Decimal("0"))
                option_cost = sum((_decimal(flow.get("cost")) for flow in option.get("cash_flows", ()) if int(flow.get("period", 0)) > 0), Decimal("0"))
                stop_cost = sum((_decimal(flow.get("cost")) for flow in options["stop"].get("cash_flows", ()) if int(flow.get("period", 0)) > 0), Decimal("0"))
                incremental_cost = option_cost - stop_cost
                if incremental_cost > 0:
                    calculations.append(CalculationTrace(f"incremental_roi-{option_id}", "(incremental future benefit - incremental future cost) / incremental future cost", (future_benefit - incremental_cost) / incremental_cost))

        if sufficiency.sufficient:
            diagnostics.append("gate_evidence_sufficiency:pass")
        completeness_threshold, materiality, confidence_threshold = self._policy(data)
        completeness_ok = _decimal(data.get("completeness")) >= completeness_threshold
        confidence = str(data.get("confidence", "low"))
        confidence_ok = _CONFIDENCE_ORDER.get(confidence, -1) >= _CONFIDENCE_ORDER.get(confidence_threshold, 1)
        diagnostics.append(f"gate_policy_completeness:{'pass' if completeness_ok else 'fail'}")
        diagnostics.append(f"gate_policy_confidence:{'pass' if confidence_ok else 'fail'}")
        winner = self._winner(data)
        if winner and stop_npv is not None:
            winner_npv = npvs[winner]
            stop_delta = winner_npv - stop_npv
            diagnostics.append(f"gate_future_economics:{'pass' if winner == 'stop' or stop_delta >= materiality else 'conditional'}")
        diagnostics.append(f"gate_sensitivity:{'pass' if data.get('sensitivity') else 'fail'}")
        findings = (Finding("sequential-gates", "Value decision evaluated in order: validity, hard constraints, sufficiency, future economics/executability, sensitivity.", calculation_ids=tuple(item.id for item in calculations)),)
        return AnalysisResult(
            id=f"value-gate-{case.id}", framework_id=self.framework_id, framework_version=self.version,
            input_snapshot_hash=input_snapshot_sha256(case), analysis_mode=case.question.requested_analysis_mode,
            calculations=tuple(calculations), findings=findings, limitations=tuple(limitations),
            evidence_ids=tuple(item.id for item in case.evidence), assumption_ids=tuple(item.id for item in case.assumptions),
            diagnostics=tuple(diagnostics + ([f"binding_constraint:{item}" for item in failed_constraints])),
            extensions={
                "benefit_series": {
                    key: str(benefit[key])
                    for key in ("baseline", "planned_to_date", "actual_to_date", "target", "forecast")
                    if key in benefit
                },
                "discount_rate": str(data.get("discount_rate", "not supplied")),
            },
        )

    def run_sensitivity(self, case: DecisionCase, result: AnalysisResult) -> Tuple[SensitivityResult, ...]:
        data = self._input(case)
        outputs = []
        options = data.get("options", {})
        rate = _decimal(data.get("discount_rate"))
        for index, spec in enumerate(data.get("sensitivity", ())):
            option_id = str(spec["option"])
            low, high = _decimal(spec["low"]), _decimal(spec["high"])
            low_winner = self._winner(data, option_id, low)
            high_winner = self._winner(data, option_id, high)
            competitors = {key: self._option_npv(value, rate) for key, value in options.items() if key != option_id and value.get("hard_constraints_met", True)}
            base_without_benefit = self._option_npv(options[option_id], rate, Decimal("0"))
            benefit_pv = self._option_npv(options[option_id], rate, Decimal("1")) - base_without_benefit
            threshold = None
            if competitors and benefit_pv != 0:
                threshold = (max(competitors.values()) - base_without_benefit) / benefit_pv
            conclusion = f"one-way named sensitivity; flip threshold={threshold}" if threshold is not None else "one-way named sensitivity; no finite flip threshold"
            outputs.append(SensitivityResult(
                id=f"value-sensitivity-{index}", variable=str(spec["name"]),
                low_case=f"{low}: {low_winner}", high_case=f"{high}: {high_winner}", conclusion=conclusion,
                calculation_ids=(f"npv-{option_id}",),
            ))
        return tuple(outputs)

    def build_recommendation(self, case: DecisionCase, result: AnalysisResult, sensitivity: Tuple[SensitivityResult, ...]) -> Recommendation:
        data = self._input(case)
        sufficiency = self.assess_sufficiency(case)
        validation = self.validate_evidence(case)
        completeness_threshold, materiality, confidence_threshold = self._policy(data)
        completeness_ok = _decimal(data.get("completeness")) >= completeness_threshold
        confidence = str(data.get("confidence", "low"))
        confidence_rank = _CONFIDENCE_ORDER.get(confidence, 0)
        threshold_rank = _CONFIDENCE_ORDER.get(confidence_threshold, 1)
        winner = self._winner(data)
        feasible_npvs = sorted(
            (self._option_npv(option, _decimal(data.get("discount_rate"))) for option in data.get("options", {}).values() if option.get("hard_constraints_met", True)),
            reverse=True,
        )
        material_winner = len(feasible_npvs) == 1 or (feasible_npvs[0] - feasible_npvs[1] >= materiality)
        if not validation.valid or not sufficiency.sufficient or not completeness_ok:
            status, selected = RecommendationStatus.NO_RECOMMENDATION, ()
            statement = "No recommendation: critical value evidence or required Stop comparator is missing or invalid."
        elif winner is None:
            status, selected, statement = RecommendationStatus.DEFER, (), "Defer pending an executable option."
        elif confidence_rank < threshold_rank:
            status, selected, statement = RecommendationStatus.DEFER, (), "Defer until evidence confidence meets PPTSmith policy."
        elif not material_winner:
            status, selected, statement = RecommendationStatus.NO_RECOMMENDATION, (), "No clear winner: option economics are within the PPTSmith policy materiality threshold."
        elif confidence_rank == threshold_rank or not sensitivity:
            status, selected, statement = RecommendationStatus.CONDITIONAL, (winner,), f"Conditionally select {winner}; validate sensitivity and evidence confidence."
        else:
            status, selected, statement = RecommendationStatus.RECOMMEND, (winner,), f"Select {winner} based on sequential gates and future incremental economics."
        constraints = tuple(item.split(":", 1)[1] for item in result.diagnostics if item.startswith("binding_constraint:"))
        owner = case.question.owner or "unassigned"
        review_date = (case.question.decision_date + timedelta(days=30)) if case.question.decision_date else None
        level = ConfidenceLevel(confidence) if confidence in _CONFIDENCE_ORDER else ConfidenceLevel.LOW
        return Recommendation(
            id=f"recommendation-{result.id}", status=status, statement=statement,
            selected_option_ids=selected,
            rejected_option_ids=tuple(item for item in data.get("options", {}) if selected and item not in selected),
            deferred_option_ids=tuple(data.get("options", {})) if status in (RecommendationStatus.DEFER, RecommendationStatus.NO_RECOMMENDATION) else (),
            evidence_ids=result.evidence_ids, assumption_ids=result.assumption_ids,
            calculation_ids=tuple(item.id for item in result.calculations),
            binding_constraints=constraints,
            counterarguments=(Counterargument("counterargument-value", "Forecast benefits may not materialize.", "Use named sensitivity and review triggers."),),
            sensitivity_summary=tuple(item.conclusion for item in sensitivity), confidence=level,
            confidence_basis="Evidence quality only; not probability of outcome.", owner=owner,
            conditions=("PPTSmith policy thresholds remain satisfied.", "No hard constraint becomes binding."),
            review_date=review_date,
            triggers=(ReviewTrigger("value-review", "Forecast or constraint status changes materially", "Re-run sequential gates"),),
            model_version=self.version, analysis_run_id=result.id,
        )

    def explain(self, result: AnalysisResult) -> ExplanationTrace:
        return ExplanationTrace(
            "Value realization and Continue/Pivot/Stop analysis",
            tuple(item for item in result.diagnostics if item.startswith("gate_")),
        )
