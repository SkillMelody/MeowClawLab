from dataclasses import dataclass
from typing import Iterable, Tuple

from .model import DecisionCase, SufficiencyReport


@dataclass(frozen=True)
class EvidenceRequirement:
    key: str
    description: str


def assess_evidence(case: DecisionCase, requirements: Iterable[EvidenceRequirement]) -> SufficiencyReport:
    available = {tag for item in case.evidence for tag in item.tags}
    missing = tuple(requirement.key for requirement in requirements if requirement.key not in available)
    return SufficiencyReport(
        sufficient=not missing,
        missing_fields=missing,
        reason_codes=("required_evidence_missing",) if missing else (),
    )

