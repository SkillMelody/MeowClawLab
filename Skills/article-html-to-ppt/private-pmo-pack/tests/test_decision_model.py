import json
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from decision_support.model import (
    AnalysisMode,
    ConfidenceLevel,
    DecisionCase,
    DecisionQuestion,
    DecisionType,
    EstimateRange,
    EvidenceItem,
    EvidenceKind,
    FreshnessStatus,
    RouteAction,
    SourceLocation,
    SourceReference,
    TimeBasis,
    UnitSpec,
)
from decision_support.serialization import (
    SCHEMA_VERSION,
    canonical_json,
    input_snapshot_sha256,
    load_decision_case,
    save_decision_case,
)
from decision_support.validation import validate_decision_case


NOW = datetime(2026, 7, 25, tzinfo=timezone.utc)


def build_case() -> DecisionCase:
    source = SourceReference(
        id="src-1",
        title="Approved business case",
        source_type="document",
        location=SourceLocation(kind="page", value="12"),
        retrieved_at=NOW,
    )
    unit = UnitSpec(dimension="currency", symbol="USD", currency="USD", scale=Decimal("1"))
    evidence = EvidenceItem(
        id="ev-1",
        claim="Forecast benefit is USD 1.2m",
        value=Decimal("1200000.00"),
        unit=unit,
        time_basis=TimeBasis(period="year", start=date(2026, 1, 1), end=date(2026, 12, 31)),
        source_ids=(source.id,),
        kind=EvidenceKind.ESTIMATE,
        confidence=ConfidenceLevel.HIGH,
        confidence_rationale="Finance-approved model",
        freshness=FreshnessStatus.CURRENT,
        decisive=True,
        estimate=EstimateRange(
            low=Decimal("1000000"),
            central=Decimal("1200000"),
            high=Decimal("1400000"),
            unit=unit,
            basis="FY2026 plan",
            method="bottom-up forecast",
            confidence=ConfidenceLevel.HIGH,
        ),
    )
    question = DecisionQuestion(
        id="q-1",
        decision_type=DecisionType.VALUE,
        question="Should the steering committee continue the programme?",
        owner="Executive sponsor",
        decision_date=date(2026, 8, 1),
        horizon="FY2026",
        requested_analysis_mode=AnalysisMode.PRESCRIPTIVE,
        option_ids=("continue", "stop"),
        baseline_id="baseline",
    )
    return DecisionCase(
        id="case-1",
        created_at=NOW,
        updated_at=NOW,
        question=question,
        sources=(source,),
        evidence=(evidence,),
        option_ids=("baseline", "continue", "stop"),
    )


class DecisionModelTests(unittest.TestCase):
    def test_frozen_enum_values(self):
        self.assertEqual([item.value for item in EvidenceKind], ["fact", "estimate", "assumption", "external_benchmark"])
        self.assertEqual([item.value for item in DecisionType], ["value", "resource", "schedule", "risk", "multi_domain", "unknown"])
        self.assertEqual([item.value for item in RouteAction], ["route", "ask", "describe_only", "block"])

    def test_records_are_immutable_and_use_decimal_and_tuple(self):
        case = build_case()
        self.assertIsInstance(case.evidence, tuple)
        self.assertIsInstance(case.evidence[0].value, Decimal)
        with self.assertRaises(FrozenInstanceError):
            case.id = "changed"

    def test_estimate_range_requires_ordered_bounds(self):
        with self.assertRaisesRegex(ValueError, "low <= central <= high"):
            EstimateRange(low=Decimal("3"), central=Decimal("2"), high=Decimal("4"))

    def test_source_reference_requires_specific_location(self):
        with self.assertRaisesRegex(ValueError, "source location"):
            SourceReference(id="src", title="Bare URL", source_type="url", url="https://example.com")

    def test_duplicate_ids_and_broken_references_are_reported(self):
        case = build_case()
        duplicate = EvidenceItem(id="ev-1", claim="duplicate")
        broken = EvidenceItem(id="ev-2", claim="broken", source_ids=("missing",))
        report = validate_decision_case(
            DecisionCase(
                id=case.id,
                created_at=NOW,
                updated_at=NOW,
                question=case.question,
                sources=case.sources,
                evidence=(case.evidence[0], duplicate, broken),
                option_ids=case.option_ids,
            )
        )
        self.assertIn("duplicate_id", report.reason_codes)
        self.assertIn("broken_reference", report.reason_codes)

    def test_canonical_json_round_trip_and_hash_are_stable(self):
        case = build_case()
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "case.json"
            second = Path(tmp) / "case-2.json"
            save_decision_case(case, first)
            loaded = load_decision_case(first)
            save_decision_case(loaded, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(loaded, case)
            self.assertEqual(input_snapshot_sha256(case), input_snapshot_sha256(loaded))
            self.assertEqual(canonical_json(case), first.read_text(encoding="utf-8").rstrip("\n"))

    def test_unknown_schema_version_is_rejected(self):
        payload = json.loads(canonical_json(build_case()))
        payload["schema_version"] = "9.9.9"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unknown.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported schema version"):
                load_decision_case(path)
        self.assertEqual(SCHEMA_VERSION, "1.0.0")


if __name__ == "__main__":
    unittest.main()
