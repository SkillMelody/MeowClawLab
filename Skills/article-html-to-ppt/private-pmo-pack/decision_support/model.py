from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple


SCHEMA_VERSION = "1.0.0"


class EvidenceKind(str, Enum):
    FACT = "fact"
    ESTIMATE = "estimate"
    ASSUMPTION = "assumption"
    EXTERNAL_BENCHMARK = "external_benchmark"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FreshnessStatus(str, Enum):
    CURRENT = "current"
    AGING = "aging"
    STALE = "stale"
    UNKNOWN = "unknown"


class DecisionType(str, Enum):
    VALUE = "value"
    RESOURCE = "resource"
    SCHEDULE = "schedule"
    RISK = "risk"
    MULTI_DOMAIN = "multi_domain"
    UNKNOWN = "unknown"


class AnalysisMode(str, Enum):
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PRESCRIPTIVE = "prescriptive"


class RouteAction(str, Enum):
    ROUTE = "route"
    ASK = "ask"
    DESCRIBE_ONLY = "describe_only"
    BLOCK = "block"


class RecommendationStatus(str, Enum):
    RECOMMEND = "recommend"
    CONDITIONAL = "conditional"
    DEFER = "defer"
    NO_RECOMMENDATION = "no_recommendation"
    INFEASIBLE = "infeasible"


class RecordStatus(str, Enum):
    DRAFT = "draft"
    REVIEW_READY = "review_ready"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"


def _extensions() -> Mapping[str, Any]:
    return MappingProxyType({})


@dataclass(frozen=True)
class SourceLocation:
    kind: str
    value: str
    field: Optional[str] = None


@dataclass(frozen=True)
class UnitSpec:
    dimension: str
    symbol: str
    currency: Optional[str] = None
    scale: Decimal = Decimal("1")
    time_denominator: Optional[str] = None
    scope: Optional[str] = None


@dataclass(frozen=True)
class TimeBasis:
    period: str
    start: Optional[date] = None
    end: Optional[date] = None
    as_of: Optional[date] = None


@dataclass(frozen=True)
class SourceReference:
    id: str
    title: str
    source_type: str
    location: Optional[SourceLocation] = None
    url: Optional[str] = None
    retrieved_at: Optional[datetime] = None
    schema_version: str = SCHEMA_VERSION
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extensions: Mapping[str, Any] = field(default_factory=_extensions, compare=False)

    def __post_init__(self) -> None:
        if self.location is None:
            raise ValueError("source location is required")


@dataclass(frozen=True)
class EstimateRange:
    low: Decimal
    central: Decimal
    high: Decimal
    unit: Optional[UnitSpec] = None
    basis: str = ""
    method: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.LOW

    def __post_init__(self) -> None:
        if not self.low <= self.central <= self.high:
            raise ValueError("estimate range must satisfy low <= central <= high")


@dataclass(frozen=True)
class EvidenceItem:
    id: str
    claim: str
    metric: Optional[str] = None
    value: Optional[Decimal] = None
    unit: Optional[UnitSpec] = None
    time_basis: Optional[TimeBasis] = None
    source_ids: Tuple[str, ...] = ()
    derivation_id: Optional[str] = None
    kind: EvidenceKind = EvidenceKind.FACT
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    confidence_rationale: str = ""
    freshness: FreshnessStatus = FreshnessStatus.UNKNOWN
    conflict_status: str = "none"
    tags: Tuple[str, ...] = ()
    decisive: bool = False
    estimate: Optional[EstimateRange] = None
    schema_version: str = SCHEMA_VERSION
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extensions: Mapping[str, Any] = field(default_factory=_extensions, compare=False)


@dataclass(frozen=True)
class Assumption:
    id: str
    statement: str
    impact: str = ""
    owner: Optional[str] = None
    validation_method: str = ""
    review_date: Optional[date] = None
    expiry_date: Optional[date] = None
    trigger: Optional[str] = None
    status: str = "open"
    schema_version: str = SCHEMA_VERSION
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extensions: Mapping[str, Any] = field(default_factory=_extensions, compare=False)


@dataclass(frozen=True)
class DecisionQuestion:
    id: str
    decision_type: DecisionType
    question: str
    owner: Optional[str] = None
    decision_date: Optional[date] = None
    horizon: Optional[str] = None
    requested_analysis_mode: AnalysisMode = AnalysisMode.DESCRIPTIVE
    option_ids: Tuple[str, ...] = ()
    constraint_ids: Tuple[str, ...] = ()
    baseline_id: Optional[str] = None
    schema_version: str = SCHEMA_VERSION
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extensions: Mapping[str, Any] = field(default_factory=_extensions, compare=False)


@dataclass(frozen=True)
class ValidationIssue:
    reason_code: str
    message: str
    path: str = ""
    blocking: bool = True


@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    issues: Tuple[ValidationIssue, ...] = ()

    @property
    def reason_codes(self) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(issue.reason_code for issue in self.issues))


@dataclass(frozen=True)
class SufficiencyReport:
    sufficient: bool
    missing_fields: Tuple[str, ...] = ()
    reason_codes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ReadinessReport:
    ready: bool
    reason_codes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class FrameworkSelection:
    candidate_framework_ids: Tuple[str, ...]
    selected_framework_ids: Tuple[str, ...]
    route_action: RouteAction
    sufficiency_report: SufficiencyReport
    reason_codes: Tuple[str, ...] = ()
    requested_evidence_fields: Tuple[str, ...] = ()


@dataclass(frozen=True)
class CalculationTrace:
    id: str
    expression: str
    value: Optional[Decimal] = None
    input_evidence_ids: Tuple[str, ...] = ()
    assumption_ids: Tuple[str, ...] = ()
    unit: Optional[UnitSpec] = None


@dataclass(frozen=True)
class Finding:
    id: str
    statement: str
    evidence_ids: Tuple[str, ...] = ()
    calculation_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AnalysisResult:
    id: str
    framework_id: str
    framework_version: str
    input_snapshot_hash: str
    analysis_mode: AnalysisMode
    calculations: Tuple[CalculationTrace, ...] = ()
    findings: Tuple[Finding, ...] = ()
    limitations: Tuple[str, ...] = ()
    evidence_ids: Tuple[str, ...] = ()
    assumption_ids: Tuple[str, ...] = ()
    diagnostics: Tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extensions: Mapping[str, Any] = field(default_factory=_extensions, compare=False)


@dataclass(frozen=True)
class Counterargument:
    id: str
    statement: str
    response: str = ""
    evidence_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class SensitivityResult:
    id: str
    variable: str
    low_case: str
    high_case: str
    conclusion: str
    calculation_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewTrigger:
    id: str
    condition: str
    action: str


@dataclass(frozen=True)
class Recommendation:
    id: str
    status: RecommendationStatus
    statement: str
    selected_option_ids: Tuple[str, ...] = ()
    rejected_option_ids: Tuple[str, ...] = ()
    deferred_option_ids: Tuple[str, ...] = ()
    evidence_ids: Tuple[str, ...] = ()
    assumption_ids: Tuple[str, ...] = ()
    calculation_ids: Tuple[str, ...] = ()
    trade_offs: Tuple[str, ...] = ()
    binding_constraints: Tuple[str, ...] = ()
    counterarguments: Tuple[Counterargument, ...] = ()
    sensitivity_summary: Tuple[str, ...] = ()
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    confidence_basis: str = ""
    owner: Optional[str] = None
    conditions: Tuple[str, ...] = ()
    review_date: Optional[date] = None
    triggers: Tuple[ReviewTrigger, ...] = ()
    model_version: str = ""
    analysis_run_id: str = ""
    schema_version: str = SCHEMA_VERSION
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extensions: Mapping[str, Any] = field(default_factory=_extensions, compare=False)


@dataclass(frozen=True)
class ExplanationTrace:
    summary: str
    steps: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DecisionRecord:
    id: str
    question_id: str
    analysis_run_ids: Tuple[str, ...] = ()
    recommendation_id: Optional[str] = None
    status: RecordStatus = RecordStatus.DRAFT
    approver: Optional[str] = None
    decision_date: Optional[date] = None
    supersedes_id: Optional[str] = None
    follow_up_metrics: Tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extensions: Mapping[str, Any] = field(default_factory=_extensions, compare=False)


@dataclass(frozen=True)
class DecisionCase:
    id: str
    question: DecisionQuestion
    sources: Tuple[SourceReference, ...] = ()
    evidence: Tuple[EvidenceItem, ...] = ()
    assumptions: Tuple[Assumption, ...] = ()
    option_ids: Tuple[str, ...] = ()
    constraint_ids: Tuple[str, ...] = ()
    dependencies: Tuple[Tuple[str, str], ...] = ()
    recommendations: Tuple[Recommendation, ...] = ()
    decision_records: Tuple[DecisionRecord, ...] = ()
    schema_version: str = SCHEMA_VERSION
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extensions: Mapping[str, Any] = field(default_factory=_extensions, compare=False)

