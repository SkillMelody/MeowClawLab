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


ZERO = Decimal("0")
ONE = Decimal("1")


def _decimal(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _data(case: DecisionCase) -> Mapping[str, Any]:
    value = case.extensions.get("risk_treatment", {})
    return value if isinstance(value, Mapping) else {}


def _range(value: Any) -> Tuple[Decimal, Decimal, Decimal]:
    if isinstance(value, Mapping):
        return tuple(_decimal(value[key]) for key in ("low", "central", "high"))  # type: ignore[return-value]
    number = _decimal(value)
    return number, number, number


def _calculation(identifier: str, expression: str, value: Decimal) -> CalculationTrace:
    return CalculationTrace(identifier, expression, value)


class RiskTreatmentFramework:
    framework_id = "risk_treatment"
    version = "1.0.0"
    decision_types = frozenset({DecisionType.RISK})

    def assess_sufficiency(self, case: DecisionCase) -> SufficiencyReport:
        data = _data(case)
        if "ordinal_likelihood" in data or "ordinal_impact" in data:
            return SufficiencyReport(
                False,
                ("calibrated_probability_range", "monetary_or_calibrated_consequences"),
                ("ordinal_risk_not_monetizable",),
            )
        missing = []
        probability = data.get("probability")
        if not isinstance(probability, Mapping) or any(key not in probability for key in ("low", "central", "high", "horizon")):
            missing.append("calibrated_probability_range")
        if not data.get("consequences"):
            missing.append("monetary_or_calibrated_consequences")
        if "risk_tolerance" not in data:
            missing.append("risk_tolerance")
        return SufficiencyReport(not missing, tuple(missing), ("required_risk_evidence_missing",) if missing else ())

    def validate_evidence(self, case: DecisionCase) -> ValidationReport:
        data = _data(case)
        issues = []
        probability = data.get("probability")
        if isinstance(probability, Mapping) and all(key in probability for key in ("low", "central", "high")):
            low, central, high = _range(probability)
            if not ZERO <= low <= central <= high <= ONE:
                issues.append(ValidationIssue("invalid_probability_range", "Probability must satisfy 0 <= low <= central <= high <= 1"))
            if probability.get("horizon") != case.question.horizon:
                issues.append(ValidationIssue("probability_horizon_mismatch", "Probability horizon must match the decision horizon"))
        if data.get("tail_risk"):
            issues.append(ValidationIssue("tail_risk_requires_escalation", "Tail risk requires scenario or specialist analysis"))
        if data.get("correlated_risk"):
            issues.append(ValidationIssue("correlated_risk_requires_model", "Correlated exposure cannot be treated as independent EMV"))
        return ValidationReport(not any(issue.blocking for issue in issues), tuple(issues))

    def analyze(self, case: DecisionCase) -> AnalysisResult:
        data = _data(case)
        sufficiency = self.assess_sufficiency(case)
        validation = self.validate_evidence(case)
        ordinal_only = "ordinal_risk_not_monetizable" in sufficiency.reason_codes
        limitations = []
        diagnostics = []

        if ordinal_only:
            return AnalysisResult(
                id=f"{case.id}-risk-analysis",
                framework_id=self.framework_id,
                framework_version=self.version,
                input_snapshot_hash=input_snapshot_sha256(case),
                analysis_mode=AnalysisMode.DESCRIPTIVE,
                limitations=("Ordinal 1-5 risk scores support screening only and are not monetary exposure.",),
                diagnostics=("describe_only", "ordinal_risk_not_monetizable"),
            )
        if not sufficiency.sufficient:
            return AnalysisResult(
                id=f"{case.id}-risk-analysis",
                framework_id=self.framework_id,
                framework_version=self.version,
                input_snapshot_hash=input_snapshot_sha256(case),
                analysis_mode=AnalysisMode.DESCRIPTIVE,
                limitations=("Calibrated probability, consequences, and tolerance are required for treatment economics.",),
                diagnostics=sufficiency.reason_codes,
            )

        probability = _range(data["probability"])
        consequence_ranges = [_range(item["amount"]) for item in data["consequences"]]
        consequences = tuple(sum((item[index] for item in consequence_ranges), ZERO) for index in range(3))
        baseline = tuple(probability[index] * consequences[index] for index in range(3))
        calculations = []
        labels = ("low", "central", "high")
        for index, label in enumerate(labels):
            calculations.extend(
                (
                    _calculation(f"probability_{label}", f"calibrated event probability ({label})", probability[index]),
                    _calculation(f"consequence_{label}", f"sum of consequence amounts ({label})", consequences[index]),
                    _calculation(f"baseline_exposure_{label}", f"probability_{label} * consequence_{label}", baseline[index]),
                )
            )
        diagnostics.append(f"probability horizon: {data['probability']['horizon']}")

        guarded = bool(data.get("tail_risk") or data.get("correlated_risk"))
        if guarded:
            limitations.append("Simple additive EMV and ROI are blocked for tail or correlated risk.")
            diagnostics.extend(validation.reason_codes)
        else:
            mitigation = data.get("mitigation")
            if isinstance(mitigation, Mapping):
                success_residual = _decimal(mitigation["success_residual_probability"])
                failure = _decimal(mitigation.get("failure_probability", ZERO))
                impact_fraction = _decimal(mitigation.get("residual_impact_fraction", ONE))
                adjusted_probability = tuple(success_residual * (ONE - failure) + item * failure for item in probability)
                residual = tuple(adjusted_probability[index] * consequences[index] * impact_fraction for index in range(3))
                reduction = tuple(baseline[index] - residual[index] for index in range(3))
                full_life_cost = _decimal(mitigation.get("one_time_cost", ZERO)) + _decimal(
                    mitigation.get("recurring_cost", ZERO)
                ) * _decimal(mitigation.get("recurring_periods", ZERO))
                for index, label in enumerate(labels):
                    calculations.extend(
                        (
                            _calculation(
                                f"adjusted_residual_probability_{label}",
                                "success residual probability * success chance + baseline probability * failure chance",
                                adjusted_probability[index],
                            ),
                            _calculation(
                                f"adjusted_residual_exposure_{label}",
                                f"adjusted_residual_probability_{label} * consequence_{label} * residual impact fraction",
                                residual[index],
                            ),
                            _calculation(
                                f"exposure_reduction_{label}",
                                f"baseline_exposure_{label} - adjusted_residual_exposure_{label}",
                                reduction[index],
                            ),
                        )
                    )
                net_benefit = reduction[1] - full_life_cost
                calculations.extend(
                    (
                        _calculation("full_life_mitigation_cost", "one-time cost + recurring cost * recurring periods", full_life_cost),
                        _calculation("net_benefit", "exposure_reduction_central - full_life_mitigation_cost", net_benefit),
                    )
                )
                if full_life_cost > ZERO:
                    calculations.extend(
                        (
                            _calculation("roi", "net_benefit / full_life_mitigation_cost", net_benefit / full_life_cost),
                            _calculation("benefit_cost_ratio", "exposure_reduction_central / full_life_mitigation_cost", reduction[1] / full_life_cost),
                        )
                    )
                tolerance = _decimal(data["risk_tolerance"])
                calculations.extend(
                    (
                        _calculation("risk_tolerance", "declared risk tolerance", tolerance),
                        _calculation("tolerance_gap", "adjusted_residual_exposure_central - risk_tolerance", residual[1] - tolerance),
                    )
                )
            else:
                tolerance = _decimal(data["risk_tolerance"])
                calculations.extend(
                    (
                        _calculation("risk_tolerance", "declared risk tolerance", tolerance),
                        _calculation("tolerance_gap", "baseline_exposure_central - risk_tolerance", baseline[1] - tolerance),
                    )
                )

        constraint_types = tuple(str(item).lower() for item in data.get("constraint_types", ()))
        if data.get("mandatory_escalation") or {"legal", "safety", "compliance"}.intersection(constraint_types):
            diagnostics.append("mandatory_escalation")
            diagnostics.extend(f"binding_constraint:{item}" for item in constraint_types)
        findings = (Finding(f"{case.id}-baseline", f"Central baseline exposure is {baseline[1]}"),)
        return AnalysisResult(
            id=f"{case.id}-risk-analysis",
            framework_id=self.framework_id,
            framework_version=self.version,
            input_snapshot_hash=input_snapshot_sha256(case),
            analysis_mode=AnalysisMode.DIAGNOSTIC if guarded else case.question.requested_analysis_mode,
            calculations=tuple(calculations),
            findings=findings,
            limitations=tuple(limitations),
            diagnostics=tuple(diagnostics),
        )

    def run_sensitivity(self, case: DecisionCase, result: AnalysisResult) -> Tuple[SensitivityResult, ...]:
        data = _data(case)
        if result.analysis_mode == AnalysisMode.DESCRIPTIVE or data.get("tail_risk") or data.get("correlated_risk"):
            return ()
        mitigation = data.get("mitigation")
        if not isinstance(mitigation, Mapping):
            return ()
        values = {item.id: item.value for item in result.calculations}
        probability = _range(data["probability"])
        consequences = [_range(item["amount"]) for item in data["consequences"]]
        impact = sum((item[1] for item in consequences), ZERO)
        failure = _decimal(mitigation.get("failure_probability", ZERO))
        residual_success = _decimal(mitigation["success_residual_probability"])
        impact_fraction = _decimal(mitigation.get("residual_impact_fraction", ONE))
        cost = values["full_life_mitigation_cost"] or ZERO
        denominator = impact * (ONE - failure * impact_fraction)
        probability_switch = (
            cost + impact * residual_success * (ONE - failure) * impact_fraction
        ) / denominator if denominator > ZERO else ZERO
        probability_central = probability[1]
        failure_denominator = impact * impact_fraction * (probability_central - residual_success)
        failure_switch = (
            (probability_central * impact - cost - impact * residual_success * impact_fraction) / failure_denominator
            if failure_denominator != ZERO
            else ZERO
        )
        residual = values.get("adjusted_residual_exposure_central", values["baseline_exposure_central"]) or ZERO
        tolerance = values["risk_tolerance"] or ZERO
        reduction = values.get("exposure_reduction_central", ZERO) or ZERO
        return (
            SensitivityResult(
                "risk-switch-event-probability", "event_probability", str(probability[0]), str(probability[2]),
                f"Net benefit switches at event probability {probability_switch}", ("net_benefit",),
            ),
            SensitivityResult(
                "risk-switch-mitigation-failure", "mitigation_failure_probability", "0", "1",
                f"Net benefit switches at mitigation failure probability {failure_switch}", ("net_benefit",),
            ),
            SensitivityResult(
                "risk-switch-mitigation-cost", "mitigation_cost", "0", str(cost * Decimal("1.5")),
                f"Net benefit switches at full-life mitigation cost {reduction}", ("full_life_mitigation_cost", "net_benefit"),
            ),
            SensitivityResult(
                "risk-switch-tolerance", "risk_tolerance", str(tolerance / Decimal("2")), str(tolerance * Decimal("2")),
                f"Tolerance status switches at residual exposure {residual}", ("tolerance_gap",),
            ),
        )

    def build_recommendation(
        self, case: DecisionCase, result: AnalysisResult, sensitivity: Tuple[SensitivityResult, ...]
    ) -> Recommendation:
        data = _data(case)
        values = {item.id: item.value for item in result.calculations}
        constraints = tuple(str(item) for item in data.get("constraint_types", ()))
        mandatory = data.get("mandatory_escalation") or {"legal", "safety", "compliance"}.intersection(
            item.lower() for item in constraints
        )
        guarded = data.get("tail_risk") or data.get("correlated_risk")
        ordinal = "ordinal_risk_not_monetizable" in result.diagnostics
        selected = ()
        status = RecommendationStatus.NO_RECOMMENDATION
        statement = "No treatment recommendation is supported by the available evidence."
        conditions = ()

        if mandatory or guarded:
            selected = ("escalate",)
            status = RecommendationStatus.CONDITIONAL
            statement = "Escalate to the authorized risk owner; simple treatment economics cannot govern this risk."
            conditions = ("Authorized legal, safety, compliance, or specialist review is required.",)
        elif not ordinal and "baseline_exposure_central" in values:
            baseline = values["baseline_exposure_central"] or ZERO
            tolerance = values.get("risk_tolerance", ZERO) or ZERO
            if baseline <= tolerance:
                selected = ("accept",)
                status = RecommendationStatus.RECOMMEND
                statement = "Accept and monitor because calibrated baseline exposure is within tolerance."
            elif "net_benefit" in values and (values["net_benefit"] or ZERO) > ZERO:
                option_id = str(data["mitigation"].get("option_id", "mitigate"))
                selected = (option_id,)
                residual = values.get("adjusted_residual_exposure_central", baseline) or baseline
                if residual <= tolerance:
                    status = RecommendationStatus.RECOMMEND
                    statement = f"{option_id.capitalize()} because expected exposure reduction exceeds full-life treatment cost."
                else:
                    status = RecommendationStatus.CONDITIONAL
                    statement = f"{option_id.capitalize()}, then escalate the remaining exposure above tolerance."
                    conditions = ("Residual exposure must be accepted or reduced to the declared risk tolerance.",)
            else:
                selected = ("avoid",)
                status = RecommendationStatus.CONDITIONAL
                statement = "Avoid the exposure because it exceeds tolerance and the evaluated treatment has no positive net benefit."
                conditions = ("Confirm the feasibility and cost of avoidance before approval.",)

        owner = case.question.owner
        review_date = case.question.decision_date + timedelta(days=90) if case.question.decision_date else None
        return Recommendation(
            id=f"{result.id}-recommendation",
            status=status,
            statement=statement,
            selected_option_ids=selected,
            calculation_ids=tuple(item.id for item in result.calculations),
            binding_constraints=constraints,
            counterarguments=(
                Counterargument(
                    f"{result.id}-counterargument",
                    "Expected monetary value can understate distribution shape, dependence, and non-monetary harm.",
                    "Escalation guardrails and named sensitivity prevent economics from overriding those limits.",
                ),
            ),
            sensitivity_summary=tuple(item.conclusion for item in sensitivity),
            confidence=ConfidenceLevel.LOW,
            confidence_basis="Confidence reflects evidence quality, not event probability.",
            owner=owner,
            conditions=conditions,
            review_date=review_date,
            triggers=(ReviewTrigger(f"{result.id}-trigger", "Probability, consequence, cost, or tolerance crosses a named switching point", "Re-run treatment decision"),),
            model_version=self.version,
            analysis_run_id=result.id,
        )

    def explain(self, result: AnalysisResult) -> ExplanationTrace:
        return ExplanationTrace(
            "Risk treatment separates calibrated exposure screening from bounded treatment economics.",
            (
                "Validate probability range and horizon.",
                "Aggregate separately calibrated consequences and calculate baseline EMV.",
                "Adjust residual exposure for treatment failure and full-life cost.",
                "Apply tolerance and mandatory escalation before recommending treatment.",
                "Report named switching points and model limitations.",
            ),
        )
