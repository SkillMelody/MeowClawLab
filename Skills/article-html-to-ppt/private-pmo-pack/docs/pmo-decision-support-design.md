# PPTSmith PMO Decision Support Design

**Status:** frozen for implementation

**Positioning:** consulting-grade, explainable PMO decision support. This is
not represented as a proprietary McKinsey methodology.

## 1. Goal

Upgrade the private PMO pack from a visualization system into a bounded
decision-support system:

```text
source material
  -> evidence and assumption ledger
  -> decision question
  -> deterministic router and sufficiency gate
  -> framework analysis
  -> recommendation, counterargument, and sensitivity
  -> decision record
  -> native editable PowerPoint views
```

The system must distinguish:

- descriptive: what happened;
- diagnostic: why it happened;
- predictive: what may happen under declared assumptions;
- prescriptive: what action is supported by sufficient evidence;
- governance: who decides, under what conditions, and when to review.

## 2. Non-negotiable rules

- `components/` renders information. It does not decide what management should
  do.
- `decision_support/` computes and records analysis. It creates no PowerPoint
  coordinates or shapes.
- Routing is deterministic. LLM free-form classification cannot authorize a
  prescriptive result.
- Every recommendation references evidence, assumptions, calculations,
  counterarguments, sensitivity results, a decision owner, and a review date.
- Confidence describes evidence quality. It is not probability.
- Facts, estimates, assumptions, and external benchmarks remain distinct.
- Hard constraints are checked before scoring or economic comparison.
- Missing evidence can produce `ask`, `describe_only`, `block`,
  `no_recommendation`, or `infeasible`. The system is not required to select a
  winner.
- Public standards and classic methods are cited as public methods. Product
  thresholds are labeled PPTSmith policy and remain configurable.
- Structured analysis JSON is the audit source. PPTX is a presentation view.

## 3. Package boundaries

```text
decision_support/
  model.py                 shared immutable domain records and enums
  validation.py            references, units, dates, conflicts, and graph QA
  evidence.py              evidence ledger and sufficiency assessment
  router.py                deterministic decision routing
  protocols.py             framework plugin protocol
  recommendation.py        trace construction and prescriptive readiness
  registry.py              plugin registration and framework metadata
  serialization.py         versioned JSON load/save
  frameworks/
    value_gate.py          Benefits + Continue/Pivot/Stop
    resource_allocation.py MCDA + bounded portfolio allocation
    schedule_analysis.py   CPM + bounded constraint scenarios
    risk_treatment.py      Risk exposure + mitigation economics
  presentation/
    adapter.py             analysis result -> semantic presentation IR
    renderer.py            native decision-page PPT renderer
```

Framework modules may depend on shared model/protocol/validation code. They may
not import one another or `components.renderer`.

## 4. Shared domain model

All top-level records carry `id`, `schema_version`, `created_at`, `updated_at`,
and optional `extensions`.

### 4.1 Enums

- `EvidenceKind`: `fact`, `estimate`, `assumption`, `external_benchmark`.
- `ConfidenceLevel`: `low`, `medium`, `high`.
- `FreshnessStatus`: `current`, `aging`, `stale`, `unknown`.
- `DecisionType`: `value`, `resource`, `schedule`, `risk`, `multi_domain`,
  `unknown`.
- `AnalysisMode`: `descriptive`, `diagnostic`, `prescriptive`.
- `RouteAction`: `route`, `ask`, `describe_only`, `block`.
- `RecommendationStatus`: `recommend`, `conditional`, `defer`,
  `no_recommendation`, `infeasible`.
- `RecordStatus`: `draft`, `review_ready`, `approved`, `rejected`,
  `superseded`, `expired`.

### 4.2 Records

`SourceReference` identifies a document, sheet/range, system record/field,
interview timestamp, or URL retrieval. A URL without a source location is
insufficient.

`UnitSpec` records dimension, symbol, currency, scale, and time denominator.
Values cannot be compared until units and time bases are compatible.

`EstimateRange` contains `low`, `central`, `high`, unit, basis, method, and
confidence. It expresses a reasonable range, not a probability distribution.

`EvidenceItem` contains claim, optional metric/value, unit/time basis,
source references or derivation reference, evidence kind, confidence rationale,
freshness, conflict status, and tags.

`Assumption` contains statement, impact, owner, validation method, review or
expiry date, trigger, and status.

`DecisionQuestion` contains decision type, question, owner, decision date,
horizon, requested analysis mode, option IDs, and constraint IDs.

`FrameworkSelection` contains candidate framework IDs, selected framework IDs,
route action, sufficiency report, reason codes, and requested evidence fields.

`AnalysisResult` contains framework ID/version, input snapshot hash, analysis
mode, calculations, findings, limitations, evidence and assumption references,
and diagnostics.

`Recommendation` contains status, statement, selected/rejected/deferred
options, evidence references, assumptions, trade-offs, binding constraints,
counterarguments, sensitivity summary, confidence and basis, owner, conditions,
review date, triggers, model version, and analysis run ID.

`DecisionRecord` contains the question, analysis runs, recommendation, approval
status, approver, decision date, supersession link, and follow-up metrics.

## 5. Framework protocol

Every plugin implements:

```python
class DecisionFramework(Protocol):
    framework_id: str
    version: str
    decision_types: frozenset[DecisionType]

    def assess_sufficiency(self, case: DecisionCase) -> SufficiencyReport: ...
    def validate_evidence(self, case: DecisionCase) -> ValidationReport: ...
    def analyze(self, case: DecisionCase) -> AnalysisResult: ...
    def run_sensitivity(
        self, case: DecisionCase, result: AnalysisResult
    ) -> tuple[SensitivityResult, ...]: ...
    def build_recommendation(
        self,
        case: DecisionCase,
        result: AnalysisResult,
        sensitivity: tuple[SensitivityResult, ...],
    ) -> Recommendation: ...
    def explain(self, result: AnalysisResult) -> ExplanationTrace: ...
```

The registry exposes metadata and required evidence keys without importing PPT
rendering code.

## 6. Decision router

Router order:

1. Validate question, owner, horizon, option identity, sources, units, and time
   basis.
2. Detect hard blockers and material evidence conflicts.
3. Match explicit question signals and available evidence to candidate
   frameworks.
4. Run each candidate's sufficiency assessment.
5. Return:
   - `route`: one framework or an ordered multi-framework analysis;
   - `ask`: exact missing evidence fields;
   - `describe_only`: visualization/diagnosis is allowed, recommendation is not;
   - `block`: invalid or contradictory decision case.

Priority rules:

- continue/pivot/stop, benefit or business-case questions -> value framework;
- prioritization, budget cut, capacity allocation -> resource framework;
- delay, critical path, bottleneck, crash or gate date -> schedule framework;
- accept/mitigate/transfer/escalate or mitigation economics -> risk framework;
- multi-domain cases run an explicit ordered plan. They are not merged into an
  opaque score.

## 7. Prescriptive readiness

Prescriptive output is blocked when any material condition applies:

- missing decision owner, date, horizon, option boundary, or baseline;
- stale/disputed critical evidence;
- incompatible units, currency, scope, or time basis;
- decisive estimate without a range or method;
- unsupported weight or normalization rubric;
- invalid dependency graph;
- missing stop/alternative option for an economic gate;
- hard constraint failure hidden inside a weighted score;
- recommendation without counterargument or required sensitivity;
- missing recommendation owner, review date, or trigger conditions.

Reason codes are stable machine-readable strings. User-facing output translates
them into evidence requests.

## 8. Initial frameworks

### 8.1 Value realization and Continue/Pivot/Stop

Calculates direction-normalized benefit realization, forecast gap, future
incremental NPV, and optional incremental ROI. Historical sunk cost is disclosed
but excluded from option economics. Gates run in order: valid question, hard
constraints, evidence sufficiency, future economics/executability, sensitivity.

Recommendations: Continue, Pivot, Stop, Conditional, Defer, or No clear winner.
All product thresholds are configurable and labeled product policy.

### 8.2 MCDA and resource allocation

Checks must-do, dependencies, exclusions, budget, capacity, dates, and policy
thresholds before scoring. Uses approved fixed anchors or rubrics, never default
candidate-set min-max normalization. Weight sets require named sources.

Small simple portfolios (`n <= 20`) may use complete subset enumeration and
claim optimality only within the declared model. Larger/cross-period problems
use an explainable heuristic and are labeled heuristic.

### 8.3 Critical path and constraint analysis

Requires duration, valid dependency endpoints/types/lags, calendars, data date,
and an acyclic network. Computes ES/EF/LS/LF/total float and traces driving
dependencies. Multiple critical paths are preserved.

Initial support includes resource overload detection and bounded scenarios. It
does not claim global resource leveling, a full Critical Chain implementation,
or project-level probabilistic P80. PERT output is labeled analytic
approximation.

### 8.4 Risk exposure and mitigation economics

Separates screening (heat map/register) from treatment decisions. Computes
baseline exposure, adjusted residual exposure, exposure reduction, mitigation
net benefit, ROI/BCR, and sensitivity when calibrated probability/impact data
exists.

Ordinal 1-5 heat-map scores cannot be converted to monetary exposure. Tail,
correlated, compliance, safety, and non-monetizable risks may block ROI-based
recommendation or require escalation.

## 9. Presentation views

Initial native editable views:

- Benefits Dashboard;
- Business Case Bridge;
- Continue/Pivot/Stop Gate;
- Weighted Decision Matrix;
- Capacity vs Demand;
- Scenario Allocation;
- Critical Path Gantt;
- Constraint Board;
- Risk Exposure Bridge;
- Mitigation ROI;
- Recommendation Trace and Decision Record.

Each slide carries analysis run ID, evidence cutoff, model version, and status.
Detailed evidence and sensitivity remain in appendix pages or JSON evidence.

## 10. QA

Blocking QA covers:

- broken or cyclic references;
- unit/currency/time/scope incompatibility;
- stale or unresolved conflicting decisive evidence;
- assumptions without owner/expiry/trigger;
- unsupported weights and sample-relative normalization;
- invalid CPM network or untraceable critical path;
- monetary risk claims derived from ordinal heat scores;
- recommendation without evidence trace, counterargument, sensitivity,
  decision owner, review date, or conditions;
- rendering that changes analysis meaning;
- planned framework or component represented as implemented.

## 11. Delivery phases

### DS0: shared foundation

Domain model, JSON schema, validation, router, plugin protocol, registry,
serialization, recommendation trace, and readiness gate.

### DS1: four framework engines

Four independently testable plugins, fixtures, calculations, diagnostics, and
sensitivity output. No PPT rendering in framework tasks.

### DS2: presentation integration

Adapters and native editable decision components. Existing visualization
components remain compatible.

### DS3: gold benchmark deck

One evidence-backed 10-12 page Steering Committee deck with calculations,
recommendation, counterargument, sensitivity, source trace, and decision log.

## 12. Explicit exclusions for this release

- LLM free-form framework routing;
- ontology or knowledge graph platform;
- global mixed-integer resource optimizer;
- full resource-leveled Critical Chain;
- Monte Carlo project simulation;
- automatic reference-class forecasting without a valid historical dataset;
- causal attribution inferred from correlation;
- legal, safety, compliance, or investment advice without authorized owners;
- claims of proprietary McKinsey methodology.
