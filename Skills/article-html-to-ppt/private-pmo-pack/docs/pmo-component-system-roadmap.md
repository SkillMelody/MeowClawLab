# PPTSmith PMO Component System Roadmap

**System:** Boardroom Ink with Material-style tokens

**Primary package:** `private-artifacts/pptsmith-pmo-consulting-pack/`

**Current implementation phase:** Phase 2 P0 complete

**Status source of truth:** `state/component-system-progress.json`

## 1. Delivery model

The component pipeline is:

```text
PMO semantic data
  -> component IR validation
  -> deterministic layout contract
  -> Boardroom Ink token resolution
  -> native python-pptx renderer
  -> semantic and geometry QA
  -> package inspection
  -> LibreOffice render/readback
```

Component IR contains business meaning, not PowerPoint drawing commands. Layout
helpers own data-driven geometry. Renderers consume resolved geometry and create
editable PowerPoint objects.

## 2. Component classification

| Family | Components | Phase | Current status |
| --- | --- | ---: | --- |
| Composition | Annotated doughnut | 1 | Implemented |
| Delivery sequence | Phased Roadmap | 1 | Implemented |
| Schedule | Gantt timeline | 1 | Implemented |
| Executive status | KPI/status cards | 2 | P0 implemented |
| Event timeline | Milestone | 2 | P0 implemented |
| Risk and control | Risk Heat Map, RAID | 2 | Heat Map implemented; RAID interface only |
| Responsibility | RACI | 2 | P0 implemented |
| Governance tracking | Action Tracker, Decision Matrix | 2 | Interface contract only |
| Process topology | Swimlane/dependency | 2 | Interface contract only |
| Financial | Budget vs Actual, Waterfall | 3 | Planned |
| Capacity and portfolio | Resource Capacity, Portfolio Bubble | 3 | Planned |
| Agile delivery | Release Train, Trend/Burndown | 3 | Planned |
| Governance topology | Complex governance diagrams | 3 | Planned |
| Premium material | Liquid Glass skin | 3 | Planned |

## 3. Phase 0 baseline

Phase 0 is an existing baseline and is not reclassified as component-system
completion.

- PMO v0.1 direct Python renderer.
- Ten PMO page families and an 11-slide native sample deck.
- Structural QA and real PPTX rendering.
- Approved external preview baselines for annotated doughnut, Roadmap, and
  Gantt.
- Known baseline limitation: native connector endpoint binding was not
  claimed.

Acceptance boundary: Phase 0 proves the private PMO pack can generate native
PPTX, but it does not provide the separated component IR/layout/token
architecture delivered in Phase 1.

## 4. Phase 1 implementation

### 4.1 Token and schema resolver

Status: implemented and verified.

Deliverables:

- `components/tokens.py`
- `schemas/pmo-component-ir.schema.json`
- compatibility with `contracts/mckinsey-pmo.style.json`

Implemented contract:

- Boardroom Ink surface, text, line, sequence, state, and schedule roles;
- Latin/CJK font stack and explicit fallbacks;
- spacing scale and minimum clearances;
- line-width roles;
- status semantics;
- density limits by component;
- declared component fallback modes;
- explicit dotted-token fallback resolution.

Acceptance:

- legacy color and typography keys remain available;
- semantic token lookup is deterministic;
- missing roles fail unless an explicit fallback is supplied;
- density overrides do not delete unrelated defaults.

### 4.2 Semantic component IR

Status: implemented for the three Phase 1 components.

Supported semantic IR:

- annotated doughnut: categories, values, color roles, center metric, caption;
- Roadmap: phases, objectives, periods, outputs, exit conditions, gates;
- Gantt: timeline, tasks, owners, planned and actual intervals, health,
  milestones, reference date.

Acceptance:

- IR contains no coordinates or PowerPoint shape commands;
- category completeness and 100% total are validated;
- roadmap phase identity and required governance fields are validated;
- Gantt date ordering, disjoint interval declaration, baseline coverage, and
  milestone/reference range are validated.

### 4.3 Shared layout and QA

Status: implemented and verified.

Deliverables:

- `components/layout.py`
- `components/qa.py`
- `components/inspection.py`

Implemented helpers:

- cumulative angle and segment midpoint anchors;
- left/right label lanes;
- vertical collision resolution;
- leader crossing gate and legend fallback;
- Roadmap equal phase columns, boundaries, gate channel, output band, and
  duration band;
- date-to-position mapping;
- continuous planned bars and narrower actual overlays;
- declared disjoint interval preservation;
- legend completeness;
- text bounds and approximate overflow checks;
- PPTX native-object and package-media inspection.

Acceptance:

- crowded doughnut fixture selects the declared legend fallback;
- Roadmap gates equal phase-end boundaries;
- more than five Roadmap phases select split fallback;
- invalid dates fail validation;
- declared disjoint Gantt intervals remain separate;
- every Gantt encoding is present in the legend;
- text bounds and overflow gates are executable tests.

### 4.4 Native renderer and sample

Status: implemented and verified.

Deliverables:

- `components/renderer.py`
- `scripts/build_component_system_phase1.py`
- `scripts/verify_component_system_phase1.py`
- `examples/pmo-component-system-phase1.json`
- `output/pmo-component-system-phase1.pptx`

Native object policy:

- doughnut uses a native PowerPoint chart with editable chart data;
- doughnut labels, endpoint dots, and leaders are native objects;
- each leader is one continuous native elbow connector object;
- Roadmap uses native chevrons, diamonds, lines, panels, and text;
- Gantt uses native text, grid connectors, continuous bar shapes, overlays,
  dots, diamonds, and a reference line;
- message-bearing objects are not rasterized;
- package picture count must equal zero.

Acceptance:

- exactly three sample slides;
- at least one native chart;
- more than forty native objects;
- zero picture shapes and zero package media files;
- all component semantic shape-name prefixes present;
- LibreOffice opens and renders all three slides when available.

Limitation: python-pptx creates native connectors but does not expose a reliable
API to prove connector endpoint binding. Phase 1 therefore does not claim bound
connector editability. This is recorded in inspection, verification summary,
and state.

### 4.5 Edge fixtures

Status: implemented and verified.

- `tests/fixtures/doughnut-crowded.json`: small categories and crowded labels
  trigger legend fallback.
- `tests/fixtures/roadmap-overflow.json`: six phases trigger split fallback.
- `tests/fixtures/gantt-disjoint.json`: a declared schedule pause preserves
  separate intervals.
- `tests/fixtures/gantt-invalid-date.json`: invalid timeline and interval date
  order fails validation.

### 4.6 Final visual corrections

Status: verified.

Resolved defects:

- Annotated doughnut layout previously started at the 3 o'clock axis while the
  native chart starts at 12 o'clock and sweeps clockwise. The layout now starts
  at `-90 degrees`, stores each semantic segment start/end/mid angle, and checks
  every endpoint against its own angular interval with 0/360 wrap support.
- Roadmap phase one previously used the same notched chevron as middle phases.
  It now uses a flat-left pentagon; only middle phases use chevrons.
- Gantt previously labeled fourteen boundary ticks for a thirteen-column,
  ninety-one-day range. It now builds thirteen explicit weekly intervals,
  renders one bounded label per interval, and displays each interval's date
  span.
- End-date milestones are clamped by their half-width inside the timeline
  frame, so the final Go-live diamond remains inside W13.
- Gantt legend now declares healthy, watch, and neutral health encodings as
  `On track`, `Watch`, and `Not assessed`.

Regression acceptance:

- every doughnut endpoint angle is inside its target segment interval;
- endpoint color roles match the corresponding native chart series point;
- the first Roadmap phase shape type differs from middle chevrons and has a
  flat left boundary;
- week-label count equals timeline-column count;
- week labels and milestone shapes remain inside timeline bounds;
- month spans cover the full timeline without gaps;
- all health colors used by the sample appear in the legend;
- LibreOffice renders all three slides and the final PNGs pass explicit visual
  review.

## 5. Phase 2 implementation

Source: `components/contracts.py`, `PHASE2_CONTRACTS`.

### 5.1 Priority P0

Status: implemented and verified.

Delivered components:

1. KPI/status
   - semantic IR: id, label, value, unit, numeric target, direction, status,
     period, note, and optional numeric trend values;
   - deterministic 3-6 card layout with target/actual variance, status
     bar/dot, and bounded native mini-trend;
   - more than six metrics select deterministic page splitting rather than
     reducing text below the legibility floor.
2. Milestone timeline
   - semantic IR: id, label, date, owner, evidence, status, and optional phase;
   - exact date-to-axis mapping, alternating label lanes, collision
     resolution, native diamonds, and native leaders;
   - more than eight milestones split; more than sixteen select the declared
     table fallback.
3. Risk Heat Map
   - semantic IR: id, label, likelihood, impact, owner, status, and mitigation;
   - native editable 5x5 grid with explicit axis direction, ID-bearing points,
     and a readable right-side risk register;
   - same-cell risks use deterministic non-overlapping jitter; more than
     twelve risks select the risk-register table fallback.
4. RACI
   - semantic IR: roles, activities, and explicit activity/role/code
     assignments;
   - native editable PowerPoint table with strong header/activity-column
     treatment and restrained A/R/C/I encoding;
   - each activity must contain exactly one A and at least one R; role or
     activity overflow selects deterministic block splitting.

P0 deliverables:

- `examples/pmo-component-system-phase2-p0.json`
- `tests/fixtures/kpi-status-overflow.json`
- `tests/fixtures/milestone-overdense.json`
- `tests/fixtures/risk-heat-map-dense.json`
- `tests/fixtures/raci-overflow.json`
- `scripts/build_component_system_phase2.py`
- `scripts/verify_component_system_phase2.py`
- `output/pmo-component-system-phase2-p0.pptx`
- `qa/component-system-phase2-p0-manifest.json`
- `qa/component-system-phase2-p0-inspection.json`
- `qa/component-system-phase2-p0-render-report.json`
- `qa/component-system-phase2-p0-verification-summary.md`

Acceptance evidence:

- 36 full-suite tests pass, including all Phase 1 regressions;
- four slides and all four P0 component prefixes are present;
- 215 native PowerPoint objects, including one editable native RACI table;
- zero picture shapes and zero package media files;
- component semantic QA, geometry QA, text bounds, and text overflow gates pass;
- LibreOffice opens and renders all four slides;
- all four rendered PNGs passed explicit visual review after correcting KPI
  grid balance, same-cell risk-point overlap, and the two-line RACI title.

### Priority P1

5. RAID
   - IR: type, description, owner, date, mitigation, status.
   - QA: taxonomy, ownership, date, state completeness.
6. Action Tracker
   - IR: action, owner, due date, status.
   - QA: owner/date/state completeness and row overflow.
7. Decision Matrix
   - IR: options, criteria, weights, scores, recommendation.
   - QA: weights, score ranges, recommendation traceability, legend.

### Priority P2

8. Swimlane/dependency
   - IR: lanes, activities, dependencies.
   - QA: ownership, valid endpoints, connector crossing budget, text bounds.

Remaining Phase 2 dependencies:

- reusable native table layout contract;
- numeric formatting contract;
- status semantics from Phase 1;
- date mapping from Phase 1;
- reserved connector channels and improved routing;
- golden fixtures for each new family.

Remaining Phase 2 acceptance boundary:

- each family has validated semantic IR;
- each family has deterministic layout and native renderer;
- each family has at least one normal and one edge fixture;
- table/connector/text QA gates are automated;
- a Phase 2 sample PPTX passes package and render verification.

Those acceptance conditions are met for P0 only. P1 and P2 remain interface
contracts and must not be presented as implemented.

## 6. Phase 3 boundary

Status: planned only.

Source: `components/contracts.py`, `PHASE3_CONTRACTS`.

1. Budget vs Actual
   - dependencies: numeric formats, native chart theme, variance semantics;
   - uncertainty: currency/locale policy and forecast encoding.
2. Waterfall
   - dependencies: numeric formats and embedded workbook QA;
   - uncertainty: negative label routing and subtotal authoring parity.
3. Resource Capacity
   - dependencies: date mapping, capacity-unit contract, heat tokens;
   - uncertainty: mixed FTE/hours and overbooking policy.
4. Portfolio Bubble
   - dependencies: axis scales, label collision, native scatter chart;
   - uncertainty: bubble normalization and outlier fallback.
5. Release Train
   - dependencies: Roadmap boundaries, dependency channels, milestones;
   - uncertainty: cross-team density and calendar exceptions.
6. Trend/Burndown
   - dependencies: native line chart, date mapping, forecast semantics;
   - uncertainty: missing periods and target rebaseline disclosure.
7. Complex governance diagrams
   - dependencies: graph IR, routing, hierarchy layout, slide splitting;
   - uncertainty: arbitrary topology and connector endpoint binding.
8. Liquid Glass skin
   - dependencies: skin-independent geometry, solid fallback, renderer parity;
   - uncertainty: LibreOffice transparency, print contrast, shadows.

Phase 3 acceptance boundary:

- financial and capacity semantics are traceable to source values;
- complex diagrams have bounded topology and pagination rules;
- every chart maintains native editability or discloses any bounded exception;
- Liquid Glass never changes component meaning or geometry;
- solid fallback passes LibreOffice and print-contrast checks.

No Phase 3 layout solver, renderer, or skin is implemented in this delivery.

## 7. Dependencies and recovery

Recovery order:

1. Read `state/component-system-progress.json`.
2. Run `python3 scripts/build_component_system_phase2.py`.
3. Run `python3 scripts/verify_component_system_phase2.py --visual-review-status passed`.
4. Inspect `qa/component-system-phase2-p0-verification-summary.md`.
5. Start the `next_task` recorded in state.

Do not promote Phase 2 P1/P2 or Phase 3 status without corresponding IR
validation, tests, native sample output, static inspection, and rendered
evidence.
