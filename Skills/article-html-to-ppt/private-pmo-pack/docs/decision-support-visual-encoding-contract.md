# Decision-Support Visual Encoding Contract

**System:** Boardroom Ink  
**Acceptance target:** the 11-page decision-support gold deck  
**Canvas:** 13.333 × 7.5 in / 16:9  
**Native-editable requirement:** PowerPoint shapes, connectors, text, tables, and charts only; whole-slide raster count must remain zero.

## Product objective and acceptance hierarchy

PPTSmith is a private PMO commercial production pack. Its objective is not
merely to emit an editable, renderable, structurally compliant PPTX. It must
automatically translate project-management and decision information into a
consulting-grade visual narrative that is projection-readable, scan-readable,
and natively editable.

Every page must be designed in this order:

1. What judgment must the audience make?
2. What is the core conclusion?
3. Which visual encoding most directly proves that conclusion?
4. Only then: which native PowerPoint implementation expresses that proof?

Acceptance priority is fixed:

1. information judgment and visual proof;
2. consulting-grade narrative, hierarchy, and readability;
3. native editability;
4. structural and rendering QA.

Items 3–4 are necessary controls, but they cannot compensate for failure on
Items 1–2.

This contract supersedes acceptance based on shape counts, editability, or
successful rendering alone. A page passes only when its governing judgment is
encoded by a spatial relationship that a viewer can scan before reading the
supporting annotations.

## Cross-page rules

- The dominant visual occupies at least 55% of the usable content region
  (approximately x=0.55..12.78, y=1.35..6.88).
- Every page declares one primary encoding among position, length, area, path,
  connection, time, matrix, or coordinate.
- Rectangles may annotate a visual but may not become the default page
  grammar. Repeated unconnected field cards do not count as a visual encoding.
- Green means passed/selected/within tolerance; amber means conditional,
  near-critical, or watch; red means failed/binding/above tolerance; blue and
  navy carry neutral sequence and comparison.
- Minimum body copy target is 9 pt; captions and metadata may use 7.2–8.5 pt.
- Titles must be supported by the dominant encoding and must not overstate
  readiness. Diagnostic and aggregate no-recommendation boundaries remain
  explicit.

## Page contracts

### 1. Decision Brief

- **Audience judgment:** decide whether the evidence can support one aggregate
  recommendation or must remain routed to separate framework decisions.
- **Data / judgment:** valid evidence routes through sufficiency and four
  framework assessments, but no aggregate recommendation is produced.
- **Core conclusion:** the case is analyzable and routed, yet the final state is
  deliberately `NO AGGREGATE RECOMMENDATION`.
- **Primary encoding:** a left-to-right decision funnel / chained arrow stages:
  `evidence -> sufficiency gate -> routed frameworks -> recommendation state`.
- **Required structure:** connected stage shapes with monotonically increasing
  x-position; a distinct terminal state node; framework branches rejoin before
  the terminal state.
- **Acceptance criteria:** solid-fill stage labels are fully readable; framework
  lanes do not cover the assessment-stage headline; separate branches visibly
  rejoin at the terminal no-recommendation state.

### 2. Benefits Dashboard

- **Audience judgment:** decide whether realized and forecast benefits justify
  continued economic review.
- **Data / judgment:** actual-to-date is ahead of plan and forecast is above
  target; future economics still govern the decision.
- **Core conclusion:** current realization is 120% of plan and forecast is five
  units above target, but the decision still rests on future incremental value.
- **Primary encoding:** a bullet chart for actual vs plan and a two-step
  target-to-forecast bridge.
- **Required structure:** common quantitative baseline; actual bar length,
  plan marker, target marker, forecast extension, and signed gap annotation.
- **Acceptance criteria:** actual visibly exceeds the plan marker; forecast
  visibly exceeds target on the same declared scale; current uplift and future
  economics remain separate judgments.

### 3. Business Case Gate

- **Audience judgment:** decide which future option should proceed after all
  policy and evidence gates are applied.
- **Data / judgment:** ten ordered gates pass and Continue has the strongest
  future NPV / incremental economics.
- **Core conclusion:** every gate clears and Continue leads Pivot and Stop.
- **Primary encoding:** a connected horizontal gate path ending in a three-way
  NPV comparison.
- **Required structure:** ten gate nodes joined in order; pass/fail state
  encoded on the path; three option bars share a zero baseline; nine audited
  calculations are aligned under the relevant options as a secondary trace
  strip, not as a card wall.
- **Acceptance criteria:** the viewer can trace gates 1–10 in sequence and see
  Continue as the longest positive NPV bar; Stop must remain left of zero and
  the audit table must remain subordinate to the path and comparison.

### 4. Weighted Decision Matrix

- **Audience judgment:** compare portfolio options without confusing score rank
  with the constraint-aware selected set.
- **Data / judgment:** fixed-anchor scores rank Platform, Growth, Migration,
  then Security; the selected portfolio is not identical to a simple top-N
  rank because hard constraints precede scoring.
- **Core conclusion:** Platform leads, Growth is second, and selection is not a
  naive threshold cut because constraints precede score.
- **Primary encoding:** fixed-anchor heat matrix plus horizontal ranking bars
  and a declared selection threshold.
- **Required structure:** heat cells share a 0–1 scale; score bars are
  monotonic with score; threshold line is explicit; selection marks remain
  separate from score.
- **Acceptance criteria:** score order is visible from bar length without
  reading values; the 0.75 line is explicit; selected/not-selected marks do not
  falsely imply that the threshold alone made the decision.

### 5. Capacity Scenario Allocation

- **Audience judgment:** decide whether each scenario fits the bounded team and
  budget capacity, and where headroom exists.
- **Data / judgment:** Base consumes all team capacity, Downside leaves
  headroom, and Relief expands the ceiling.
- **Core conclusion:** Base is binding at 6/6, Downside uses 4/6, and Relief
  uses 6/8.
- **Primary encoding:** three 100% stacked capacity bars.
- **Required structure:** option segments use length proportional to declared
  team demand; unused capacity is visible; capacity ceiling and budget
  used/limit are marked for each scenario; scenario bars share a normalized
  0–100% frame.
- **Acceptance criteria:** Base reaches its ceiling; Downside and Relief expose
  two capacity units of unused space; scenario comparisons are possible from
  proportional segment length and visible limits.

### 6. Critical Path Gantt

- **Audience judgment:** decide which tasks drive finish and whether the
  required date can be met.
- **Data / judgment:** the driving A-B-D-F chain determines the finish and
  breaches the required finish boundary by two working days.
- **Core conclusion:** the critical chain finishes at day 8 against a day 6
  requirement; the finish breach is two working days.
- **Primary encoding:** time position and duration on a Gantt grid.
- **Required structure:** task bars, dependency connectors, critical vs
  near-critical color, float labels, required-finish reference, project-finish
  marker, and a total-duration bracket.
- **Acceptance criteria:** A-B-D-F forms one connected red path; the project
  finish marker lies to the right of the required-finish line; task duration,
  float, and total duration remain projection-readable.

### 7. Constraint Board

- **Audience judgment:** decide where recovery action must focus first and which
  tasks are next to become binding.
- **Data / judgment:** negative-float tasks form the binding recovery boundary;
  near-critical tasks have only one day of float.
- **Core conclusion:** A-B-D-F are already binding; C-E-G are the next
  watchlist.
- **Primary encoding:** a dependency / constraint network with severity and
  trigger-time encoding.
- **Required structure:** task nodes are positioned by earliest start,
  dependency edges preserve direction, node color encodes float severity, and
  the required-finish boundary cuts the network at its trigger time.
- **Acceptance criteria:** the red binding chain and amber watch chain are
  visually distinct; edge direction and earliest-start position are legible;
  the required-finish boundary intersects the time field at day 6.

### 8. Risk Exposure

- **Audience judgment:** decide whether mitigation brings residual exposure
  within tolerance.
- **Data / judgment:** mitigation reduces central exposure from 450k to 135k,
  but residual exposure remains 35k above the 100k tolerance.
- **Core conclusion:** mitigation is material but insufficient; residual
  exposure remains 35k above tolerance.
- **Primary encoding:** baseline-to-reduction-to-residual waterfall with a
  tolerance reference.
- **Required structure:** baseline, signed reduction, residual, tolerance line,
  and residual gap; lengths share one monetary scale.
- **Acceptance criteria:** the reduction connects baseline to residual on one
  monetary scale; the residual endpoint remains visibly beyond the tolerance
  line; the 35k gap is explicit.

### 9. Mitigation ROI

- **Audience judgment:** decide whether treatment economics are positive enough
  to support conditional action.
- **Data / judgment:** 315k gross exposure reduction minus 150k full-life cost
  yields 165k net benefit; ROI is 1.1 and BCR is 2.1.
- **Core conclusion:** treatment is economically positive, conditional on
  probability and consequence calibration.
- **Primary encoding:** cost-benefit bridge on a common monetary scale.
- **Required structure:** gross benefit bar, cost subtraction, net benefit
  endpoint, zero baseline, and ROI/BCR annotations tied to the bridge.
- **Acceptance criteria:** cost visibly subtracts from gross reduction to a
  positive net endpoint; ROI and BCR annotations remain linked to that bridge;
  the calibration condition is visible, not buried in metadata.

### 10. Recommendation Trace

- **Audience judgment:** decide which framework outputs are prescriptive-ready
  and where counterarguments, sensitivities, or evidence gaps block readiness.
- **Data / judgment:** each framework carries recommendation/diagnostic status,
  counterargument, sensitivity, and evidence boundary as one trace.
- **Core conclusion:** only Value Gate is prescriptive-ready; three diagnostic
  paths retain explicit evidence boundaries, so no aggregate recommendation is
  produced.
- **Primary encoding:** four horizontal swimlanes with connected evidence
  nodes.
- **Required structure:** stable left-to-right stages
  `stance -> counterargument -> sensitivity -> evidence boundary`; connectors
  remain within each framework lane; readiness state is encoded at lane start.
- **Acceptance criteria:** each framework is traceable left-to-right as one
  lane; Value Gate is the only green prescriptive lane; missing readiness is
  visible at the evidence boundary rather than inferred from a dense table.

### 11. Decision Record

- **Audience judgment:** decide whether each framework record is governance-ready
  and when it must be reviewed or rerun.
- **Data / judgment:** governance is review-ready only if owner, conditions,
  review date, and rerun trigger remain attached to each framework record.
- **Core conclusion:** Value Gate and Resource Allocation are near-term, Risk
  Treatment reviews later, and Schedule Analysis remains incomplete.
- **Primary encoding:** dated governance timeline with framework lanes.
- **Required structure:** review dates map monotonically to x-position; owner
  is visible per lane; missing review date is rendered in a distinct undated
  holding area; status and trigger are tied to timeline nodes.
- **Acceptance criteria:** 1 Aug, 31 Aug, and 30 Oct are ordered by x-position;
  each dated node remains tied to owner/condition/trigger; Schedule Analysis is
  isolated in a red undated holding area.

## Acceptance evidence

The acceptance report must record, for every page:

1. the data or judgment presented;
2. the visual encoding actually rendered;
3. the conclusion available from the visual relationship;
4. the concrete difference from the superseded card/table version;
5. automated structural checks and enlarged 1920×1080 visual review status.
