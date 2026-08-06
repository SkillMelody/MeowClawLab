# PPTSmith PMO Consulting Pack

Private production pack for McKinsey-style project management and PMO visualization decks.

This is a commercial-side pack, not part of the public `article-html-to-ppt` Skill. It keeps the PMO page families, style rules, sample data, and renderer in `private-artifacts/` while remaining compatible with the PPTSmith direction: editable PPTX, structured contracts, and evidence-backed QA.

## What v0.1 Proves

- Generates one 11-page editable PPTX sample from structured PMO domain JSON.
- Covers the 10 requested PMO page families:
  - Executive Dashboard
  - Project Roadmap
  - Milestone
  - RAID Log
  - Workstream
  - RACI Matrix
  - Risk Heat Map
  - Decision Page
  - KPI Dashboard
  - Action Tracker
- Uses PowerPoint-native text, shapes, tables, connectors, and chart objects.
- Avoids screenshot-only delivery: the generated deck has `0` picture objects.
- Renders successfully with LibreOffice in the current environment.

## Main Outputs

- PPTX: `output/ai-platform-project-pmo.pptx`
- Build manifest: `qa/build-manifest.json`
- Structural inspection: `qa/inspection.json`
- Render report: `qa/rendered/render-report.json`
- Rendered PDF: `qa/rendered/deck.pdf`
- Contact sheet: `qa/rendered/contact-sheet.png`
- Verification summary: `qa/verification-summary.md`

## Current Verification

Latest v0.1 run:

- Status: `passed`
- Slides: `11`
- Native shapes: `274`
- Native graphic frames: `6`
- Native connectors: `23`
- Native charts: `1`
- Pictures / raster media objects: `0`
- Render status: `passed`
- Renderer: LibreOffice 26.2.4.2

The raw generic PPTSmith inspection intentionally remains available. For v0.1, the private verifier allowlists:

- `PPTX_ORPHAN_SOLID_COLOR_BLOCK`, because PMO status dots and heat-map cells are intended unlabeled indicator shapes.
- `PPTX_TEXT_FRAGMENTATION` only on S08, because risk heat-map coordinate labels are intentionally split into small editable labels.

## Architecture Direction

v0.1 contains a direct Python renderer so the pack can prove the visual and editable output quickly.

The target architecture is:

```text
PMO domain JSON
  -> PMO page-family adapter
  -> PPTSmith PPT IR / Diagram IR
  -> Delivery Plan
  -> Builder
  -> Inspect / Render / Verify
```

This avoids forking the public PPTSmith engine and keeps commercial assets private. The public engine remains the lower-level contract and trusted delivery layer.

## Files

```text
contracts/
  mckinsey-pmo.style.json
schemas/
  pmo-input.schema.json
examples/
  ai-platform-project.pmo.json
taxonomy/
  status-rag.json
  raci-codes.json
  raid-types.json
scripts/
  build_pmo_deck.py
  verify_pmo_deck.py
output/
  ai-platform-project-pmo.pptx
qa/
  build-manifest.json
  inspection.json
  verification-summary.md
  rendered/
```

## Run

```bash
python3 private-artifacts/pptsmith-pmo-consulting-pack/scripts/build_pmo_deck.py
python3 private-artifacts/pptsmith-pmo-consulting-pack/scripts/verify_pmo_deck.py
```

## v0.2 Backlog

- Add `adapters/pmo_domain_to_ppt_ir.py` so this pack emits PPTSmith PPT IR instead of rendering directly.
- Add `adapters/pmo_domain_to_diagram_ir.py` for roadmap, swimlane, and workstream topology.
- Split renderer into `components/` modules per page family.
- Add PMO semantic QA:
  - owner fields are non-empty;
  - dates parse and sort correctly;
  - RACI codes are legal;
  - RAID type is legal;
  - risk heat-map coordinates are 1-5;
  - decision pages include recommendation and next step;
  - action tracker rows include owner, due date, and status.
- Promote `raid_register` to a private first-class semantic component
  (`risk_heat_map` and `raci_matrix` are complete in Phase 2 P0).
- Add 10 golden-slide fixtures, one per page family.
- Add a client-ready Premium sample deck with better visual polish and manual PowerPoint compatibility check.

## v0.2 Completed: Content-Aware Page Selection

The private pack now includes an auditable routing layer:

```text
evidence units
  -> page router
  -> layout budget
  -> PMO semantic QA
  -> selection-manifest.json
  -> native PPTX page family
```

Supported page families now include:

- single-project health dashboard
- portfolio dashboard
- time and resource dashboard
- PMO control tower
- executive status one-pager
- implementation roadmap
- milestone timeline
- RAID register
- workstream board
- RACI matrix
- risk heat map
- decision page
- KPI dashboard
- action tracker

The router records why a page family was selected and refuses to force a data visualization when evidence is too thin. Layout QA caps supporting visual count and body density; semantic QA checks action owner/deadline/status, legal RACI codes and accountable-owner count, risk coordinates, and decision recommendation/next step.

### v0.2 Validation Run

- Test suite: `13 passed`
- Auto-selection manifest: `5/5 page families selected and layout-approved`
- Validation deck: `output/dashboard-auto-selection-validation.pptx`
- Slides: `6` (cover + five automatically selected dashboard families)
- Native shapes: `217`
- Native tables: `3`
- Native charts: `1`
- Pictures / raster media objects: `0`
- LibreOffice render: `6/6 passed`
- Static text overflow risks after revision: `0`
- Generic inspector advisories are retained in `qa/dashboard-inspection.json` and are not hidden; status blocks and chart/table visual containers are intentional native objects.

## v0.3 Prototype: Uploaded Reference Visual Styles

The pack now includes a focused six-slide prototype for the uploaded PMO chart styles:

- half-gauge dashboard
- basic doughnut composition
- annotated external-callout doughnut
- budget KPI ring group
- roadmap Gantt timeline
- milestone trend line

The prototype is intentionally separate from the main sample deck so these styles can be promoted into reusable PMO components without destabilizing the v0.1/v0.2 renderers.

### v0.3 Validation Run

- Builder script: `scripts/build_visual_style_prototype.py`
- Prototype deck: `output/pmo-reference-visual-styles.pptx`
- Manifest: `qa/visual-style-prototype-manifest.json`
- Structural inspection: `qa/visual-style-prototype-inspection.json`
- Render report: `qa/visual-style-prototype-rendered/render-report.json`
- Slides: `6`
- Native shapes: `158`
- Native charts: `6`
- Native connectors: `11`
- Pictures / raster media objects: `0`
- Generic PPTSmith inspection: `passed`
- LibreOffice render: `6/6 passed`

## Known v0.1 Limits

- Connector endpoint binding is not claimed.
- Text density is acceptable for a proof sample but some table rows need v0.2 auto-fit polish.
- In the v0.1 deck, Risk Heat Map is a direct native shape grid; Phase 2 P0 now
  supersedes it with a validated semantic component.
- The direct renderer is a proof vehicle; it should not become the long-term architecture.

## PMO Component System Phases

The reusable component-system implementation is tracked separately from the
existing v0.1-v0.3 prototype history.

- Phase 1: Boardroom Ink tokens, semantic IR, deterministic layout/QA, and
  native renderers for annotated doughnut, Roadmap, and Gantt.
- Phase 2 P0: implemented semantic IR, deterministic layout/QA, and native
  renderers for KPI/status, Milestone, Risk Heat Map, and RACI.
- Phase 2 P1/P2: interface contracts only for RAID, Action Tracker, Decision
  Matrix, and Swimlane/dependency.
- Phase 3: planned only for financial, capacity, portfolio, agile delivery,
  complex governance, and Liquid Glass skin families.

Phase 1 paths:

- Roadmap: `docs/pmo-component-system-roadmap.md`
- State: `state/component-system-progress.json`
- Sample: `output/pmo-component-system-phase1.pptx`
- Build: `python3 scripts/build_component_system_phase1.py`
- Verify: `python3 scripts/verify_component_system_phase1.py`

Phase 2 P0 paths:

- Sample: `output/pmo-component-system-phase2-p0.pptx`
- Manifest: `qa/component-system-phase2-p0-manifest.json`
- Inspection: `qa/component-system-phase2-p0-inspection.json`
- Render report: `qa/component-system-phase2-p0-render-report.json`
- Verification: `qa/component-system-phase2-p0-verification-summary.md`
- Build: `python3 scripts/build_component_system_phase2.py`
- Verify: `python3 scripts/verify_component_system_phase2.py --visual-review-status passed`

Latest Phase 2 P0 acceptance evidence:

- 36/36 full-suite tests passed, including Phase 1 regression coverage.
- 4 native editable slides and 215 native objects.
- 1 native editable RACI table.
- 0 picture shapes and 0 package media files.
- LibreOffice rendered 4/4 slides.
- Explicit rendered-slide review passed after KPI balance, heat-map jitter, and
  RACI title corrections.

## Wave E Visual-Narrative-First Acceptance

Wave E was repeated after the original decision-support sample failed user
visual review. The 11 decision pages were reconstructed as semantic visuals
(decision funnel, bullet/bridge, ordered gate path, matrix/ranking,
capacity stacks, dependency Gantt, constraint network, monetary waterfalls,
swimlanes, and governance timeline), then the full 18-page acceptance set was
freshly rendered and reviewed at 1920×1080.

The product objective is a private PMO commercial production pack that
translates project and decision information into a consulting-grade,
projection-readable, scan-readable, editable visual narrative. Acceptance
therefore evaluates audience judgment, core conclusion, and visual proof before
native editability, structural inspection, and rendering checks.

- Final QA report: `qa/wave-e-final-acceptance-report.md`
- Decision-support sample: `output/pmo-decision-support-gold.pptx`
- Decision-support structural inspection:
  `qa/wave-e-decision-support-inspection.json`
- Decision-support render evidence:
  `qa/wave-e-decision-support-rendered/render-report.json`
- Result: 18/18 rendered pages reviewed; 105/105 unittest tests and 114/114
  pytest tests passed; decision-support Inspector passed with 0 issues.

LibreOffice evidence verifies current-environment open/export behavior and does
not claim Microsoft PowerPoint pixel parity.

Phase 2 P1/P2 and Phase 3 must not be presented as implemented until their
native renderers, fixtures, QA gates, sample PPTX, and render evidence exist.
