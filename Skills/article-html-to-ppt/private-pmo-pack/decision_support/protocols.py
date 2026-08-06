from typing import Protocol, Tuple

from .model import (
    AnalysisResult,
    DecisionCase,
    DecisionType,
    ExplanationTrace,
    Recommendation,
    SensitivityResult,
    SufficiencyReport,
    ValidationReport,
)


class DecisionFramework(Protocol):
    framework_id: str
    version: str
    decision_types: frozenset[DecisionType]

    def assess_sufficiency(self, case: DecisionCase) -> SufficiencyReport: ...
    def validate_evidence(self, case: DecisionCase) -> ValidationReport: ...
    def analyze(self, case: DecisionCase) -> AnalysisResult: ...
    def run_sensitivity(self, case: DecisionCase, result: AnalysisResult) -> Tuple[SensitivityResult, ...]: ...
    def build_recommendation(
        self, case: DecisionCase, result: AnalysisResult, sensitivity: Tuple[SensitivityResult, ...]
    ) -> Recommendation: ...
    def explain(self, result: AnalysisResult) -> ExplanationTrace: ...

