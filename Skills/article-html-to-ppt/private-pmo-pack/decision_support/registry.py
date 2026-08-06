from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .evidence import EvidenceRequirement
from .model import DecisionType
from .protocols import DecisionFramework


@dataclass(frozen=True)
class FrameworkMetadata:
    framework_id: str
    version: str
    decision_types: frozenset[DecisionType]
    required_evidence: Tuple[EvidenceRequirement, ...] = ()


class FrameworkRegistry:
    def __init__(self) -> None:
        self._metadata: Dict[str, FrameworkMetadata] = {}
        self._frameworks: Dict[str, DecisionFramework] = {}

    def register_metadata(self, metadata: FrameworkMetadata) -> None:
        if metadata.framework_id in self._metadata:
            raise ValueError(f"framework already registered: {metadata.framework_id}")
        self._metadata[metadata.framework_id] = metadata

    def register(self, framework: DecisionFramework, required_evidence: Tuple[EvidenceRequirement, ...] = ()) -> None:
        metadata = FrameworkMetadata(framework.framework_id, framework.version, framework.decision_types, required_evidence)
        self.register_metadata(metadata)
        self._frameworks[framework.framework_id] = framework

    def metadata(self, framework_id: str) -> FrameworkMetadata:
        return self._metadata[framework_id]

    def framework(self, framework_id: str) -> Optional[DecisionFramework]:
        return self._frameworks.get(framework_id)

    def all_metadata(self) -> Tuple[FrameworkMetadata, ...]:
        return tuple(self._metadata.values())


def default_registry() -> FrameworkRegistry:
    from .frameworks import (
        ResourceAllocationFramework,
        RiskTreatmentFramework,
        ScheduleAnalysisFramework,
        ValueGateFramework,
    )

    registry = FrameworkRegistry()
    for framework in (
        ValueGateFramework(),
        ResourceAllocationFramework(),
        ScheduleAnalysisFramework(),
        RiskTreatmentFramework(),
    ):
        registry.register(framework)
    return registry
