"""Deterministic CPM and bounded schedule-constraint analysis.

Inputs use integer working-time units. Calendar dates are presentation labels;
all arithmetic is performed by the declared working calendar contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from ..model import (
    AnalysisResult,
    DecisionCase,
    DecisionType,
    ExplanationTrace,
    Finding,
    Recommendation,
    RecommendationStatus,
    SensitivityResult,
    SufficiencyReport,
    ValidationIssue,
    ValidationReport,
)


@dataclass(frozen=True)
class WorkingCalendar:
    working_weekdays: frozenset[int]
    holidays: frozenset[date]
    unit: str = "working_day"

    @classmethod
    def from_payload(cls, value: Mapping[str, Any]) -> "WorkingCalendar":
        weekdays = frozenset(int(day) for day in value.get("working_weekdays", ()))
        if not weekdays or any(day < 0 or day > 6 for day in weekdays):
            raise ValueError("calendar requires working_weekdays in the range 0..6")
        if value.get("unit") != "working_day":
            raise ValueError("calendar unit must be working_day")
        return cls(weekdays, frozenset(date.fromisoformat(day) for day in value.get("holidays", ())))

    def is_working_day(self, value: date) -> bool:
        return value.weekday() in self.working_weekdays and value not in self.holidays

    def boundary(self, start: date, offset: int) -> date:
        """Return a working-time boundary `offset` units from start."""
        current = start
        step = 1 if offset >= 0 else -1
        remaining = abs(offset)
        while remaining:
            current += timedelta(days=step)
            if self.is_working_day(current):
                remaining -= 1
        return current

    def distance(self, start: date, finish: date) -> int:
        if finish == start:
            return 0
        step = 1 if finish > start else -1
        current, units = start, 0
        while current != finish:
            current += timedelta(days=step)
            if self.is_working_day(current):
                units += step
        return units


def _constraint_weight(kind: str, lag: int, pred_duration: int, succ_duration: int) -> int:
    weights = {
        "FS": pred_duration + lag,
        "SS": lag,
        "FF": pred_duration + lag - succ_duration,
        "SF": lag - succ_duration,
    }
    if kind not in weights:
        raise ValueError("dependency type must be FS, SS, FF, or SF")
    return weights[kind]


def _blocked(reason_codes: Iterable[str], diagnostics: Iterable[str]) -> Dict[str, Any]:
    return {
        "status": "blocked",
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "diagnostics": list(diagnostics),
    }


def _validate(payload: Mapping[str, Any]) -> Tuple[Optional[WorkingCalendar], Tuple[str, ...], Tuple[str, ...]]:
    reasons, diagnostics = [], []
    try:
        calendar = WorkingCalendar.from_payload(payload.get("calendar", {}))
    except (TypeError, ValueError) as error:
        calendar = None
        reasons.append("schedule_calendar_invalid")
        diagnostics.append(str(error))
    tasks = payload.get("tasks", ())
    ids = [task.get("id") for task in tasks]
    if not tasks or any(not task_id for task_id in ids) or len(ids) != len(set(ids)):
        reasons.append("schedule_tasks_invalid")
    for task in tasks:
        if not isinstance(task.get("duration"), int) or task.get("duration", -1) < 0:
            reasons.append("schedule_duration_invalid")
    known = set(ids)
    if not payload.get("data_date"):
        reasons.append("schedule_data_date_missing")
    for dep in payload.get("dependencies", ()):
        if dep.get("predecessor") not in known or dep.get("successor") not in known:
            reasons.append("schedule_dependency_endpoint_missing")
        if dep.get("type") not in {"FS", "SS", "FF", "SF"} or not isinstance(dep.get("lag", 0), int):
            reasons.append("schedule_dependency_invalid")
    try:
        data_date = date.fromisoformat(payload["data_date"]) if payload.get("data_date") else None
        for task in tasks:
            actual_start = date.fromisoformat(task["actual_start"]) if task.get("actual_start") else None
            actual_finish = date.fromisoformat(task["actual_finish"]) if task.get("actual_finish") else None
            if actual_finish and not actual_start:
                reasons.append("schedule_actual_finish_without_start")
            if actual_start and actual_finish and actual_finish < actual_start:
                reasons.append("schedule_actual_dates_invalid")
            if data_date and ((actual_start and actual_start > data_date) or (actual_finish and actual_finish > data_date)):
                reasons.append("schedule_actual_after_data_date")
            if task.get("remaining_duration") is not None and not data_date:
                reasons.append("schedule_data_date_missing")
    except ValueError:
        reasons.append("schedule_actual_dates_invalid")
    return calendar, tuple(dict.fromkeys(reasons)), tuple(diagnostics)


def _topological_order(task_ids: Iterable[str], dependencies: Iterable[Mapping[str, Any]]) -> Optional[Tuple[str, ...]]:
    task_ids = tuple(task_ids)
    indegree = {task_id: 0 for task_id in task_ids}
    successors = {task_id: [] for task_id in task_ids}
    for dep in dependencies:
        pred, succ = dep["predecessor"], dep["successor"]
        successors[pred].append(succ)
        indegree[succ] += 1
    ready = sorted(task_id for task_id, degree in indegree.items() if degree == 0)
    order = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for successor in sorted(successors[current]):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
                ready.sort()
    return tuple(order) if len(order) == len(task_ids) else None


def _resource_overloads(
    tasks: Mapping[str, Mapping[str, Any]], starts: Mapping[str, int], capacities: Mapping[str, int]
) -> list[Dict[str, Any]]:
    overloads = []
    horizon = max((starts[task_id] + task["duration"] for task_id, task in tasks.items()), default=0)
    for resource, capacity in sorted(capacities.items()):
        for unit in range(horizon):
            active = sorted(
                task_id for task_id, task in tasks.items()
                if starts[task_id] <= unit < starts[task_id] + task["duration"]
                and task.get("resources", {}).get(resource, 0)
            )
            demand = sum(tasks[task_id].get("resources", {}).get(resource, 0) for task_id in active)
            if demand > capacity:
                overloads.append({"resource": resource, "start": unit, "finish": unit + 1,
                                  "demand": demand, "capacity": capacity, "task_ids": active})
    return overloads


def _bounded_capacity_scenario(
    scenario: Mapping[str, Any], order: Tuple[str, ...], tasks: Mapping[str, Mapping[str, Any]],
    incoming: Mapping[str, list[Tuple[Mapping[str, Any], int]]], baseline: Mapping[str, int]
) -> Dict[str, Any]:
    capacities = scenario.get("capacities", {})
    starts: Dict[str, int] = {}
    usage: Dict[Tuple[str, int], int] = {}
    for task_id in order:
        task = tasks[task_id]
        earliest = baseline[task_id]
        for dep, weight in incoming[task_id]:
            earliest = max(earliest, starts[dep["predecessor"]] + weight)
        candidate = earliest
        while True:
            fits = all(
                usage.get((resource, unit), 0) + demand <= capacities.get(resource, 0)
                for resource, demand in task.get("resources", {}).items()
                for unit in range(candidate, candidate + task["duration"])
            )
            if fits:
                break
            candidate += 1
        starts[task_id] = candidate
        for resource, demand in task.get("resources", {}).items():
            for unit in range(candidate, candidate + task["duration"]):
                usage[(resource, unit)] = usage.get((resource, unit), 0) + demand
    finish = max((starts[task_id] + task["duration"] for task_id, task in tasks.items()), default=0)
    return {"id": scenario.get("id", "bounded-capacity"), "method": "bounded_serial_capacity_scenario",
            "task_starts": starts, "project_finish": finish,
            "limitations": ["Heuristic bounded scenario; not global resource leveling or Critical Chain."]}


def analyze_schedule(payload: Mapping[str, Any]) -> Dict[str, Any]:
    calendar, reasons, diagnostics = _validate(payload)
    if reasons:
        return _blocked(reasons, diagnostics)
    assert calendar is not None
    tasks = {task["id"]: task for task in payload["tasks"]}
    dependencies = tuple(payload.get("dependencies", ()))
    order = _topological_order(tasks, dependencies)
    if order is None:
        return _blocked(("schedule_dependency_cycle",), ("Dependency graph must be acyclic.",))

    incoming = {task_id: [] for task_id in tasks}
    outgoing = {task_id: [] for task_id in tasks}
    for dep in dependencies:
        weight = _constraint_weight(dep["type"], dep.get("lag", 0),
                                    tasks[dep["predecessor"]]["duration"], tasks[dep["successor"]]["duration"])
        incoming[dep["successor"]].append((dep, weight))
        outgoing[dep["predecessor"]].append((dep, weight))

    earliest = {task_id: 0 for task_id in tasks}
    for task_id in order:
        earliest[task_id] = max((earliest[dep["predecessor"]] + weight
                                 for dep, weight in incoming[task_id]), default=0)
    natural_finish = max(earliest[task_id] + task["duration"] for task_id, task in tasks.items())
    start_date = date.fromisoformat(payload["project_start"])
    required_finish = payload.get("required_finish")
    finish_boundary = calendar.distance(start_date, date.fromisoformat(required_finish)) if required_finish else natural_finish

    latest = {task_id: finish_boundary - task["duration"] for task_id, task in tasks.items()}
    for task_id in reversed(order):
        if outgoing[task_id]:
            latest[task_id] = min(latest[dep["successor"]] - weight for dep, weight in outgoing[task_id])

    task_results = {}
    for task_id, task in tasks.items():
        es, duration = earliest[task_id], task["duration"]
        ls = latest[task_id]
        task_results[task_id] = {
            "es": es, "ef": es + duration, "ls": ls, "lf": ls + duration, "total_float": ls - es,
            "es_date": calendar.boundary(start_date, es).isoformat(),
            "ef_date": calendar.boundary(start_date, es + duration).isoformat(),
            "ls_date": calendar.boundary(start_date, ls).isoformat(),
            "lf_date": calendar.boundary(start_date, ls + duration).isoformat(),
        }
    driving = [dep.get("id", f"{dep['predecessor']}->{dep['successor']}")
               for dep in dependencies for candidate, weight in outgoing[dep["predecessor"]]
               if candidate is dep and earliest[dep["successor"]] == earliest[dep["predecessor"]] + weight]
    critical_tasks = sorted(task_id for task_id, values in task_results.items() if values["total_float"] <= 0)
    critical_dependencies = [dep.get("id", f"{dep['predecessor']}->{dep['successor']}") for dep in dependencies
                             if dep["predecessor"] in critical_tasks and dep["successor"] in critical_tasks
                             and dep.get("id", f"{dep['predecessor']}->{dep['successor']}") in driving]
    threshold = int(payload.get("near_critical_threshold", 0))
    near_critical = sorted(task_id for task_id, values in task_results.items()
                           if 0 < values["total_float"] <= threshold)

    capacities = payload.get("resource_capacities", {})
    overloads = _resource_overloads(tasks, earliest, capacities)
    scenarios = [_bounded_capacity_scenario(item, order, tasks, incoming, earliest)
                 for item in payload.get("capacity_scenarios", ())]
    pert = {}
    for task_id, task in tasks.items():
        if all(key in task for key in ("optimistic", "most_likely", "pessimistic")):
            optimistic, likely, pessimistic = (Decimal(str(task[key])) for key in ("optimistic", "most_likely", "pessimistic"))
            if not optimistic <= likely <= pessimistic:
                return _blocked(("schedule_pert_estimates_invalid",), (f"Invalid PERT range for {task_id}.",))
            pert[task_id] = {"expected_duration": str((optimistic + 4 * likely + pessimistic) / 6),
                             "variance": str(((pessimistic - optimistic) / 6) ** 2),
                             "method": "analytic_pert_approximation"}

    return {
        "status": "ok", "calendar_contract": "discrete_working_day_boundaries_v1",
        "project_finish": natural_finish, "required_finish": finish_boundary if required_finish else None,
        "finish_variance": finish_boundary - natural_finish if required_finish else 0,
        "tasks": task_results, "driving_dependencies": driving,
        "dependency_edges": [
            {
                "id": dep.get("id", f"{dep['predecessor']}->{dep['successor']}"),
                "predecessor": dep["predecessor"],
                "successor": dep["successor"],
                "type": dep["type"],
                "lag": dep.get("lag", 0),
            }
            for dep in dependencies
        ],
        "critical_subgraph": {"task_ids": critical_tasks, "dependency_ids": critical_dependencies},
        "near_critical_threshold": threshold, "near_critical_task_ids": near_critical,
        "overload_intervals": overloads, "capacity_scenarios": scenarios, "pert": pert,
        "limitations": [
            "PERT values are analytic task-level approximations; no Monte Carlo or project P80 is claimed.",
            "Capacity scenarios are bounded heuristics, not global resource leveling or full Critical Chain.",
        ],
    }


class ScheduleAnalysisFramework:
    framework_id = "schedule_analysis"
    version = "1.0.0"
    decision_types = frozenset({DecisionType.SCHEDULE})

    @staticmethod
    def _payload(case: DecisionCase) -> Mapping[str, Any]:
        return case.extensions.get("schedule", {})

    def assess_sufficiency(self, case: DecisionCase) -> SufficiencyReport:
        payload = self._payload(case)
        required = ("project_start", "calendar", "tasks", "dependencies", "data_date")
        missing = tuple(key for key in required if key not in payload)
        return SufficiencyReport(not missing, missing, ("required_evidence_missing",) if missing else ())

    def validate_evidence(self, case: DecisionCase) -> ValidationReport:
        _, reasons, diagnostics = _validate(self._payload(case))
        issues = tuple(ValidationIssue(code, diagnostics[index] if index < len(diagnostics) else code)
                       for index, code in enumerate(reasons))
        return ValidationReport(not issues, issues)

    def analyze(self, case: DecisionCase) -> AnalysisResult:
        payload = self._payload(case)
        result = analyze_schedule(payload)
        snapshot = sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
        findings = () if result["status"] != "ok" else (
            Finding("schedule-finish", f"Calculated finish is working-time unit {result['project_finish']}."),
        )
        return AnalysisResult(
            id=f"{case.id}-schedule", framework_id=self.framework_id, framework_version=self.version,
            input_snapshot_hash=snapshot, analysis_mode=case.question.requested_analysis_mode,
            findings=findings, limitations=tuple(result.get("limitations", ())),
            diagnostics=tuple(result.get("reason_codes", ())), extensions=MappingProxyType({"schedule": result}),
        )

    def run_sensitivity(self, case: DecisionCase, result: AnalysisResult) -> Tuple[SensitivityResult, ...]:
        return ()

    def build_recommendation(
        self, case: DecisionCase, result: AnalysisResult, sensitivity: Tuple[SensitivityResult, ...]
    ) -> Recommendation:
        blocked = bool(result.diagnostics)
        return Recommendation(
            id=f"{case.id}-schedule-recommendation",
            status=RecommendationStatus.INFEASIBLE if blocked else RecommendationStatus.NO_RECOMMENDATION,
            statement="Resolve invalid schedule inputs." if blocked else "Schedule analysis is diagnostic; no action is selected.",
            owner=case.question.owner, analysis_run_id=result.id, model_version=self.version,
        )

    def explain(self, result: AnalysisResult) -> ExplanationTrace:
        return ExplanationTrace("CPM using declared working-time calendar and precedence constraints.",
                                ("Validate graph and calendar.", "Run forward and backward passes.",
                                 "Trace driving dependencies and bounded constraints."))
