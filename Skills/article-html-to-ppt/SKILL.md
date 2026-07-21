---
name: "article-html-to-ppt"
description: "Use when turning articles, docs, PRDs, or specs into polished editable PPT decks."
metadata:
  display_name: MeowClaw 夜猫 PPT 工坊
  english_alias: MeowClaw PPTSmith
  registry_slug: article-html-to-ppt
  version: 2.0.5
  brand_aliases: [meowclaw-pptsmith, meowclaw-decksmith]
---

# MeowClaw PPTSmith

Build presentation-ready, evidence-bounded, hybrid-editable slide decks. A valid PPTX is not automatically a professionally designed deck.

## Release Boundary

Version `2.0.5` is the native-connector and visual-quality safety release.

Standard readiness is component-scoped:

- `python_pptx` is qualified for native text, cards, tables, charts, and simple process diagrams.
- A simple process arrow is one connector object with its arrowhead on the line and both endpoints bound to shape connection points.
- Complex architectures, layered systems, matrices, flywheels, ecosystems, stakeholder maps, and commercial staircases require a qualified component implementation.
- If no qualified implementation exists, stop at contracts or a labeled visual reference. Never flatten relationship semantics into generic text boxes and call the result final.
- PptxGenJS can produce editable visual output but does not prove native endpoint binding. Do not claim structurally movable diagrams unless binding is verified in the PPTX package.
- LibreOffice or other renderer evidence is environment-specific and does not promise Microsoft PowerPoint pixel parity.

## Core Standard

Optimize in this order:

1. Source truth and evidence boundaries.
2. Audience decision and storyline.
3. Judgment titles.
4. Correct expression mode.
5. One primary visual anchor per slide.
6. Page architecture and information design.
7. Component craft and style consistency.
8. Editability of message-bearing content.
9. Real render/readback verification.
10. Honest delivery status.

Do not confuse any of these with visual quality proof:

- file opens successfully;
- native text ratio is high;
- no object is out of bounds;
- slides are nonblank;
- all source text is present.

Those are necessary structural checks only.

## Production Profiles

- `fast`: internal draft, content validation, simple article, or explicit speed request.
- `standard`: formal internal, product, business, technical, or ordinary client deck.
- `premium`: public release, high-value client, reusable template, strong brand requirement, or complex diagrams.

Resolve the profile before artifact planning. User override wins, but it cannot waive truthful capability reporting.

For Standard and Premium, preserve internal work under `.ppt-work/` and keep one unique user-facing final.

## Required Production Chain

```text
source
-> content lock and evidence inventory
-> storyline and judgment titles
-> expression-mode gate
-> PPT IR
-> style contract or matched reference
-> page archetypes and component plans
-> capability probe
-> component delivery resolution
-> high-fidelity reference for polish-sensitive pages
-> editable/hybrid implementation
-> package inspection
-> real render/readback
-> visual review and revision
-> trusted delivery package
```

Use `scripts/run_pipeline.py` for the guarded pipeline. Do not bypass failed gates by manually labeling a deck final.

## Expression Mode Gate

Every slide chooses exactly one primary expression:

- `textual_argument`
- `structured_cards`
- `table_matrix`
- `data_visual`
- `relationship_visual`
- `conceptual_scene`
- `hybrid_panel`

Relationship, flow, system boundary, feedback loop, ecosystem, causal chain, architecture, hierarchy, or spatial metaphor content must not remain pure prose or generic cards.

Before implementing `relationship_visual`:

1. Define Diagram IR: nodes, groups, boundaries, edges, annotations, main path.
2. Choose a real diagram type: process, swimlane, layered architecture, hierarchy, matrix, flywheel, ecosystem, staircase, or another explicit structure.
3. Select a qualified component implementation.
4. Simplify, group, split, or move details before raster fallback.
5. Preserve one visually dominant main path.

Read `references/expression-mode-gate.md`, `references/diagram-ir-and-layout.md`, and `references/diagram-auto-repair.md`.

## Connector Invariants

These are hard requirements:

- Arrowheads belong to the connector line itself. Never simulate an arrow with a separate triangle or chevron shape.
- Native editable process connectors bind both endpoints to the connected shapes. Moving a node must preserve the relationship.
- A line merely positioned near a box is not a bound connector.
- A group containing a line and triangle is not a single connector.
- Connector direction and semantic relation must remain readable after rendering.
- If a Builder cannot bind endpoints, disclose the limitation and use a qualified route. Do not claim the diagram is structurally editable.

PPTX readback for a bound arrow connector should show:

- one connector shape;
- `a:stCxn`;
- `a:endCxn`;
- an arrow end element such as `a:tailEnd type="triangle"`;
- no separate triangle or chevron arrowhead shape.

## Solid-Block Invariants

Filled shapes without message content must be intentional and named with one of:

- `Decoration:`
- `Background:`
- `Material:`
- `Connector:`

An unnamed, empty, solid-color block is a QA error because it may be a detached arrowhead, stale shape, accidental overlay, or rendering artifact.

Do not silence this detector by naming arbitrary objects. A declared layer must have a real design role and must not occlude content.

## Style Contract

For serious decks, resolve a complete `style-contract.json` before building. It is the source of truth for:

- colors and opacity;
- typography and minimum sizes;
- grid and margins;
- spacing;
- cards and tables;
- charts and diagrams;
- image treatment;
- footer and density limits.

Confirm the style with the user or match an supplied reference. Do not invent visual tokens during implementation.

Read `references/design-token-contract.md`, `references/five-style-master-systems.md`, and the matching template pack.

## Information-Design Gates

A Standard or Premium slide fails when any applies:

- a requested process, architecture, hierarchy, matrix, flywheel, or staircase is replaced with one text box;
- titles and body content are not visually separated;
- the primary content occupies only the upper portion while the lower canvas is accidental empty space;
- low-content tables use tiny text;
- a formal slide looks like a wireframe or raw spec coverage output;
- connectors do not reach or bind to nodes;
- decorative shapes compete with the message;
- the Builder silently downgrades a native-required component;
- the visual review identifies a blocking issue.

Use `references/premium-page-archetypes.md`, `references/component-craft-checklist.md`, `references/spec-to-deck-visual-priority-gate.md`, and `references/anti-regression-examples.md`.

## Builder Selection

Before selecting a Builder:

1. Run Capability Probe.
2. Match the Component Registry against actual capabilities.
3. Select the Builder with the highest qualified editable-core coverage.
4. Treat support as component-specific, not Builder-wide.
5. Reject unknown or visual-only support for native-required objects.
6. Stop when no valid route exists.

`python_pptx` Standard qualification includes simple bound process diagrams only. It does not automatically qualify every `relationship_visual`.

Read `references/component-registry.md` and `references/builder-adapters.md`.

## Two-Lane Production

For polish-sensitive work:

### Lane A: Visual Reference

Use HTML/CSS, rendered previews, or bounded visual components to calibrate typography, composition, material, density, and diagram grammar.

### Lane B: Editable Reconstruction

Rebuild message-bearing content as native PPT objects:

- titles and body text;
- cards and callouts;
- tables and simple charts;
- simple processes and diagrams;
- labels and source notes.

Raster/SVG/generated layers are allowed for complex backgrounds, photos, illustrations, and bounded complex diagrams when disclosed. Do not rasterize ordinary editable content.

## Verification Gate

Before handoff:

1. Inspect package structure.
2. Verify expected native text, tables, charts, and connectors.
3. Check bound connector XML for native movable diagrams.
4. Detect orphan solid blocks.
5. Check clipping, overlap, out-of-bounds objects, missing media, and color/font drift.
6. Render with a real available renderer.
7. Inspect the full contact sheet.
8. Enlarge and inspect all process, architecture, matrix, staircase, risk, and closing pages.
9. Revise and rerender when any visual issue remains.
10. Package only after trusted status is calculated.

If the authoritative capability report says no renderer is available, do not secretly use an undeclared renderer. Preserve `RENDER_ENGINE_UNAVAILABLE` and mark the task blocked/provisional as appropriate.

A Standard or Premium deck must not be released merely because structural inspection passed.

## Delivery Status

Keep statuses distinct:

- `planned`
- `created`
- `rendered`
- `read_back`
- `verified`
- `final`
- `blocked`
- `failed`

Environment capability missing is `blocked`, not a fabricated success and not necessarily a product failure. Builders and agents must not handwrite `final`.

## Required References

Load only what the task needs:

- `references/master-presentation-design-language.md`
- `references/expression-mode-gate.md`
- `references/premium-page-archetypes.md`
- `references/five-style-master-systems.md`
- `references/spec-to-deck-visual-priority-gate.md`
- `references/component-craft-checklist.md`
- `references/component-registry.md`
- `references/builder-adapters.md`
- `references/diagram-ir-and-layout.md`
- `references/diagram-auto-repair.md`
- `references/master-ppt-design-rubric.md`
- `references/component-raster-fallback.md`
- `references/production-profiles.md`
- `references/production-readiness-gates.md`
- `references/anti-regression-examples.md`
- `references/benchmark-methodology.md`

## Final Rule

A professional deck must preserve both semantics and craft. When the source calls for a real diagram, draw the real diagram or stop. Never ship a rough wireframe simply because it is editable and technically valid.
