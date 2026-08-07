from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from itertools import combinations
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

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


def _decimal(value: Any, default: Decimal = ZERO) -> Decimal:
    return default if value is None else Decimal(str(value))


def _input(case: DecisionCase) -> Mapping[str, Any]:
    value = case.extensions.get("resource_allocation", {})
    return value if isinstance(value, Mapping) else {}


def _reason_codes(data: Mapping[str, Any]) -> Tuple[str, ...]:
    reasons = []
    criteria = data.get("criteria", ())
    options = data.get("options", ())
    if not criteria:
        reasons.append("criteria_missing")
    if not options:
        reasons.append("options_missing")
    criterion_ids = []
    for criterion in criteria:
        criterion_id = criterion.get("id")
        criterion_ids.append(criterion_id)
        if not criterion.get("weight_source"):
            reasons.append("weight_source_missing")
        if criterion.get("normalization") == "sample_minmax":
            reasons.append("sample_relative_normalization_forbidden")
        anchors = criterion.get("anchors", {})
        if "worst" not in anchors or "best" not in anchors or anchors.get("worst") == anchors.get("best"):
            reasons.append("fixed_anchors_missing")
    for option in options:
        scores = option.get("scores", {})
        if any(criterion_id not in scores for criterion_id in criterion_ids):
            reasons.append("option_score_missing")
    option_ids = {item.get("id") for item in options}
    for option in options:
        if any(item not in option_ids for item in option.get("dependencies", ())):
            reasons.append("dependency_endpoint_missing")
        if any(item not in option_ids for item in option.get("exclusions", ())):
            reasons.append("exclusion_endpoint_missing")
    return tuple(dict.fromkeys(reasons))


def _normalized(raw: Decimal, criterion: Mapping[str, Any]) -> Decimal:
    anchors = criterion["anchors"]
    worst, best = _decimal(anchors["worst"]), _decimal(anchors["best"])
    if criterion.get("direction", "higher") == "lower":
        value = (worst - raw) / (worst - best)
    else:
        value = (raw - worst) / (best - worst)
    return min(ONE, max(ZERO, value))


def _score_options(data: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    criteria = data["criteria"]
    weights = {item["id"]: _decimal(item["weight"]) for item in criteria}
    total_weight = sum(weights.values(), ZERO)
    if total_weight <= ZERO:
        total_weight = ONE
    result: Dict[str, Dict[str, Any]] = {}
    multipliers = data.get("score_multipliers", {})
    for option in data["options"]:
        contributions = {}
        normalized = {}
        for criterion in criteria:
            criterion_id = criterion["id"]
            raw = _decimal(option["scores"][criterion_id]) * _decimal(multipliers.get(criterion_id, ONE), ONE)
            normalized[criterion_id] = _normalized(raw, criterion)
            contributions[criterion_id] = normalized[criterion_id] * weights[criterion_id] / total_weight
        result[option["id"]] = {
            "normalized": {key: float(value) for key, value in normalized.items()},
            "contributions": {key: float(value) for key, value in contributions.items()},
            "weighted_score": float(sum(contributions.values(), ZERO)),
            "_score": sum(contributions.values(), ZERO),
        }
    return result


def _dependency_closure(selected: Iterable[str], options: Mapping[str, Mapping[str, Any]]) -> frozenset[str]:
    closure = set(selected)
    pending = list(selected)
    while pending:
        option_id = pending.pop()
        for dependency in options[option_id].get("dependencies", ()):
            if dependency not in closure:
                closure.add(dependency)
                pending.append(dependency)
    return frozenset(closure)


def _feasible(selected: frozenset[str], data: Mapping[str, Any], options: Mapping[str, Mapping[str, Any]]) -> Tuple[bool, Tuple[str, ...]]:
    violations = []
    must_do = {key for key, value in options.items() if value.get("must_do")}
    required = _dependency_closure(must_do, options)
    if not required.issubset(selected):
        violations.append("must_do_or_dependency")
    if any(not set(options[item].get("dependencies", ())).issubset(selected) for item in selected):
        violations.append("dependency")
    for item in selected:
        if set(options[item].get("exclusions", ())) & selected:
            violations.append("mutual_exclusion")
            break
    required_by = data.get("required_by")
    if required_by and any(options[item].get("available_by", required_by) > required_by for item in selected):
        violations.append("required_date")
    thresholds = data.get("policy_thresholds", {})
    for item in selected:
        for criterion_id, threshold in thresholds.items():
            score = _decimal(options[item].get("scores", {}).get(criterion_id))
            if threshold.get("minimum") is not None and score < _decimal(threshold["minimum"]):
                violations.append("policy_threshold:" + criterion_id)
            if threshold.get("maximum") is not None and score > _decimal(threshold["maximum"]):
                violations.append("policy_threshold:" + criterion_id)
    cost = sum((_decimal(options[item].get("cost")) for item in selected), ZERO)
    if data.get("budget") is not None and cost > _decimal(data["budget"]):
        violations.append("budget")
    for resource, limit in data.get("capacity", {}).items():
        demand = sum((_decimal(options[item].get("capacity", {}).get(resource)) for item in selected), ZERO)
        if demand > _decimal(limit):
            violations.append("capacity:" + resource)
    return not violations, tuple(dict.fromkeys(violations))


def _select(data: Mapping[str, Any], scores: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    options = {item["id"]: item for item in data["options"]}
    option_ids = tuple(options)
    complex_model = bool(data.get("periods")) or len(option_ids) > 20
    if complex_model:
        selected = _dependency_closure((key for key, value in options.items() if value.get("must_do")), options)
        candidates = sorted((key for key in option_ids if key not in selected), key=lambda key: scores[key]["_score"], reverse=True)
        for candidate in candidates:
            trial = _dependency_closure(set(selected) | {candidate}, options)
            if _feasible(trial, data, options)[0]:
                selected = trial
        feasible, violations = _feasible(selected, data, options)
        return {"selected": selected, "feasible": feasible, "violations": violations, "method": "heuristic", "objective": sum((scores[key]["_score"] for key in selected), ZERO)}

    best = None
    for size in range(len(option_ids) + 1):
        for subset in combinations(option_ids, size):
            selected = frozenset(subset)
            feasible, _ = _feasible(selected, data, options)
            if not feasible:
                continue
            objective = sum((scores[key]["_score"] for key in selected), ZERO)
            candidate = (objective, tuple(sorted(selected)), selected)
            if best is None or candidate[:2] > best[:2]:
                best = candidate
    if best is None:
        must_do = _dependency_closure((key for key, value in options.items() if value.get("must_do")), options)
        return {"selected": frozenset(), "feasible": False, "violations": _feasible(must_do, data, options)[1], "method": "complete_enumeration", "objective": ZERO}
    return {"selected": best[2], "feasible": True, "violations": (), "method": "complete_enumeration", "objective": best[0]}


def _binding(selected: frozenset[str], data: Mapping[str, Any]) -> Tuple[str, ...]:
    options = {item["id"]: item for item in data["options"]}
    result = []
    if data.get("budget") is not None and sum((_decimal(options[item].get("cost")) for item in selected), ZERO) == _decimal(data["budget"]):
        result.append("budget")
    for resource, limit in data.get("capacity", {}).items():
        demand = sum((_decimal(options[item].get("capacity", {}).get(resource)) for item in selected), ZERO)
        if demand == _decimal(limit):
            result.append("capacity:" + resource)
    return tuple(result)


class ResourceAllocationFramework:
    framework_id = "resource_allocation"
    version = "1.0.0"
    decision_types = frozenset({DecisionType.RESOURCE})

    def assess_sufficiency(self, case: DecisionCase) -> SufficiencyReport:
        reasons = _reason_codes(_input(case))
        return SufficiencyReport(not reasons, reason_codes=reasons)

    def validate_evidence(self, case: DecisionCase) -> ValidationReport:
        reasons = _reason_codes(_input(case))
        issues = tuple(ValidationIssue(reason, reason.replace("_", " ")) for reason in reasons)
        return ValidationReport(not issues, issues)

    def analyze(self, case: DecisionCase) -> AnalysisResult:
        data = _input(case)
        reasons = _reason_codes(data)
        if reasons:
            return AnalysisResult(
                id="resource-allocation:" + case.id, framework_id=self.framework_id,
                framework_version=self.version, input_snapshot_hash=input_snapshot_sha256(case),
                analysis_mode=AnalysisMode.DESCRIPTIVE,
                limitations=("Prescriptive analysis blocked by insufficient resource-allocation inputs.",),
                diagnostics=reasons, extensions={"feasible": False, "reason_codes": reasons},
            )
        scores = _score_options(data)
        selection = _select(data, scores)
        selected = selection["selected"]
        ranking = sorted(scores, key=lambda key: (-scores[key]["_score"], key))
        dominance = {key: [] for key in scores}
        criteria = data["criteria"]
        for left in scores:
            for right in scores:
                if left == right:
                    continue
                left_values = scores[left]["normalized"]
                right_values = scores[right]["normalized"]
                if all(left_values[item["id"]] >= right_values[item["id"]] for item in criteria) and any(left_values[item["id"]] > right_values[item["id"]] for item in criteria):
                    dominance[left].append(right)
        opportunity_costs = {}
        for option_id in scores:
            if option_id in selected or not selection["feasible"]:
                continue
            forced = dict(data)
            forced["options"] = [dict(item, must_do=True) if item["id"] == option_id else item for item in data["options"]]
            alternative = _select(forced, scores)
            opportunity_costs[option_id] = float(max(ZERO, selection["objective"] - alternative["objective"])) if alternative["feasible"] else None
        scenarios = {}
        for name in ("base", "downside", "relief"):
            override = data.get("scenarios", {}).get(name, {})
            scenario_data = dict(data)
            scenario_data.update(override)
            scenario_scores = _score_options(scenario_data)
            scenario = _select(scenario_data, scenario_scores)
            scenarios[name] = {"feasible": scenario["feasible"], "selected_option_ids": sorted(scenario["selected"]), "objective": float(scenario["objective"]), "method": scenario["method"]}
        limitations = () if selection["method"] == "complete_enumeration" else ("Cross-period or large portfolio uses an explainable heuristic; global optimality is not claimed.",)
        public_scores = {key: {item: value for item, value in detail.items() if item != "_score"} for key, detail in scores.items()}
        calculations = tuple(CalculationTrace("weighted-score:" + key, "sum(normalized criterion * approved weight)", value=detail["_score"]) for key, detail in scores.items())
        findings = (Finding("portfolio-selection", "Selected feasible portfolio: " + ", ".join(sorted(selected)), calculation_ids=tuple(item.id for item in calculations)),)
        return AnalysisResult(
            id="resource-allocation:" + case.id, framework_id=self.framework_id,
            framework_version=self.version, input_snapshot_hash=input_snapshot_sha256(case),
            analysis_mode=case.question.requested_analysis_mode, calculations=calculations,
            findings=findings, limitations=limitations,
            extensions={
                "feasible": selection["feasible"], "normalization": "fixed_anchors",
                "weight_sources": {item["id"]: item["weight_source"] for item in criteria},
                "option_scores": public_scores, "ranking": ranking, "dominance": dominance,
                "selected_option_ids": sorted(selected),
                "rejected_option_ids": sorted(set(scores) - selected), "deferred_option_ids": [],
                "binding_constraints": _binding(selected, data) if selection["feasible"] else selection["violations"],
                "opportunity_costs": opportunity_costs, "scenarios": scenarios,
                "method": selection["method"],
                "optimal_within_declared_model": selection["method"] == "complete_enumeration",
                "objective": float(selection["objective"]),
                "option_resource_demand": {
                    item["id"]: {resource: float(_decimal(amount)) for resource, amount in item.get("capacity", {}).items()}
                    for item in data["options"]
                },
                "option_cost": {item["id"]: float(_decimal(item.get("cost"))) for item in data["options"]},
                "resource_limits": {
                    name: {
                        resource: float(_decimal(amount))
                        for resource, amount in {
                            **data.get("capacity", {}),
                            **data.get("scenarios", {}).get(name, {}).get("capacity", {}),
                        }.items()
                    }
                    for name in ("base", "downside", "relief")
                },
                "budget_limits": {
                    name: float(_decimal(data.get("scenarios", {}).get(name, {}).get("budget", data.get("budget"))))
                    for name in ("base", "downside", "relief")
                },
            },
        )

    def run_sensitivity(self, case: DecisionCase, result: AnalysisResult) -> Tuple[SensitivityResult, ...]:
        if not result.extensions.get("feasible"):
            return ()
        data = _input(case)
        baseline = tuple(result.extensions["ranking"])
        sensitivity = []
        for criterion in data["criteria"]:
            criterion_id = criterion["id"]
            conclusions = []
            for weight in (ZERO, ONE):
                varied = dict(data)
                varied["criteria"] = [dict(item, weight=str(weight)) if item["id"] == criterion_id else item for item in data["criteria"]]
                ranking = tuple(sorted(_score_options(varied), key=lambda key: (-_score_options(varied)[key]["_score"], key)))
                conclusions.append(ranking)
            changed = any(item != baseline for item in conclusions)
            sensitivity.append(SensitivityResult(
                id="weight-sensitivity:" + criterion_id, variable="weight:" + criterion_id,
                low_case="0", high_case="1",
                conclusion="ranking changes within tested weight range" if changed else "ranking stable within tested weight range",
                calculation_ids=tuple(item.id for item in result.calculations),
            ))
        for option_id in baseline:
            sensitivity.append(SensitivityResult(
                id="score-sensitivity:" + option_id, variable="score:" + option_id,
                low_case="fixed-anchor worst", high_case="fixed-anchor best",
                conclusion="bounded score range declared; rerun required for changed evidence",
                calculation_ids=("weighted-score:" + option_id,),
            ))
        return tuple(sensitivity)

    def build_recommendation(self, case: DecisionCase, result: AnalysisResult, sensitivity: Tuple[SensitivityResult, ...]) -> Recommendation:
        feasible = bool(result.extensions.get("feasible"))
        selected = tuple(result.extensions.get("selected_option_ids", ()))
        return Recommendation(
            id="resource-recommendation:" + case.id,
            status=RecommendationStatus.RECOMMEND if feasible else RecommendationStatus.INFEASIBLE,
            statement=("Allocate resources to " + ", ".join(selected)) if feasible else "Must-do portfolio is infeasible under declared hard constraints.",
            selected_option_ids=selected,
            rejected_option_ids=tuple(result.extensions.get("rejected_option_ids", ())),
            deferred_option_ids=tuple(result.extensions.get("deferred_option_ids", ())),
            calculation_ids=tuple(item.id for item in result.calculations),
            trade_offs=tuple("Opportunity cost for %s: %s" % item for item in result.extensions.get("opportunity_costs", {}).items()),
            binding_constraints=tuple(result.extensions.get("binding_constraints", ())),
            counterarguments=(Counterargument(
                id="resource-counterargument:" + case.id,
                statement="A rejected option may outperform if approved weights, scores, or constraints change.",
                response="Retain fixed anchors and rerun the declared scenarios and sensitivity before review.",
            ),),
            sensitivity_summary=tuple(item.conclusion for item in sensitivity),
            confidence=ConfidenceLevel.MEDIUM if feasible else ConfidenceLevel.LOW,
            confidence_basis="Fixed anchors and named weight sources; confidence is evidence quality, not probability.",
            owner=case.question.owner,
            conditions=("Weights retain their named approval source.", "Hard constraints and option evidence remain current."),
            review_date=case.question.decision_date,
            triggers=(ReviewTrigger(
                id="resource-review-trigger:" + case.id,
                condition="Budget, capacity, option score, dependency, exclusion, or approved weight changes.",
                action="Rerun feasibility, portfolio selection, scenarios, and sensitivity.",
            ),),
            model_version=self.version, analysis_run_id=result.id,
            extensions={"method": result.extensions.get("method")},
        )

    def explain(self, result: AnalysisResult) -> ExplanationTrace:
        return ExplanationTrace(
            summary="Hard constraints were applied before fixed-anchor weighted scoring and portfolio selection.",
            steps=("Validate weights, anchors, and scores.", "Apply must-do dependency closure and exclusions.", "Enforce budget and capacity.", "Select portfolio and calculate opportunity costs.", "Test scenarios and sensitivity."),
        )
