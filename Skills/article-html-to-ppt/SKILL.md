---
name: "article-html-to-ppt"
description: "MeowClaw PPTSmith: convert articles/docs to polished hybrid-editable PPT decks"
metadata:
  display_name: "MeowClaw 夜猫 PPT 工坊"
  english_alias: "MeowClaw PPTSmith"
  registry_slug: "article-html-to-ppt"
  version: "2.0.1"
  brand_aliases: ["meowclaw-pptsmith", "meowclaw-decksmith"]
---

# MeowClaw 夜猫 PPT 工坊 / MeowClaw PPTSmith

Convert articles, Markdown drafts, HTML pages, WeChat drafts, PRDs, automation plans, knowledge posts, design specs, and review-approved manuscripts into polished, low-rework, persona-fit slide decks.

Public identity:

- Display name: `MeowClaw 夜猫 PPT 工坊`
- English alias: `MeowClaw PPTSmith`
- ClawHub / installed route: `article-html-to-ppt`
- Brand aliases: `meowclaw-pptsmith`, `meowclaw-decksmith`

Keep the ClawHub slug, OpenClaw route, and directory name as `article-html-to-ppt` for backward compatibility and update continuity. `meowclaw-pptsmith` is the primary brand alias, not a separately registered ClawHub slug.

Version `2.0.1` is the Chinese-first documentation and public-distribution patch for the engineering-complete v2.0 capability line, which is **Standard production-ready on the verified acceptance environment**. The canonical Standard acceptance route is `python_pptx`; PptxGenJS is validated portability evidence on the same source semantic contracts. A separate **LibreOffice Premium acceptance** is final on the recorded environment: PptxGenJS 4.0.1 plus LibreOffice 26.2.4.2 rendered and read back all 9 slides, passed zero-error QA, and passed an evidence-bound model visual rubric at 15/18. This does **not** verify native Microsoft PowerPoint compatibility or promise cross-implementation pixel parity. See `docs/v2.0-acceptance-report.md`; generated acceptance artifacts are maintained outside the public source tree.

Default delivery is `hybrid editable`: polished material/background layers may be raster, SVG, or generated image components, while message-bearing content remains editable PowerPoint objects. Avoid both extremes: screenshot-only decks that cannot be edited, and pure native-object decks that look like rough wireframes.

## Core Standard

Optimize in this order:

1. Content truth and source boundaries.
2. Storyline and slide-level judgment clarity.
3. Audience/persona-fit structure and proof style.
4. Expression mode: text, cards, table, data visual, relationship visual, conceptual scene, or hybrid panel.
5. Page architecture and one primary anchor.
6. Design intent fidelity, not blind spec literalism.
7. Master-level visual design language and component craft.
8. Editability of core text, cards, diagrams, tables, simple charts, and labels.
9. Production profile fit: `fast`, `standard`, or `premium`.
10. Render/readback verification before final handoff.
11. Benchmark-calibrated rubric scoring for serious changes.
12. Honest reporting of rasterized layers, conversion limits, and trusted delivery status.

## Standard Production Chain

Use this chain for serious decks. For the v2 one-command Standard route, run `scripts/run_pipeline.py` with `--builder auto|python_pptx|pptxgenjs`, `--profile standard`, isolated `--work-dir`, and a unique `--output-dir`. Production runs select one Builder; do not routinely generate two user finals. The dual-Builder execution is acceptance/regression evidence only, with `python_pptx` as the canonical accepted deck.

```text
source/article/design brief
-> resolve production profile
-> content analysis and evidence inventory
-> slide storyline and judgment titles
-> expression mode gate
-> slide_manifest.json with expression plan
-> style selection and page archetype mapping
-> STYLE & PALETTE CONFIRMATION GATE (confirm with user OR match reference)
-> detailed design specification
-> visual priority map + deletion/noise budget
-> capability probe for builders/renderers/fonts
-> component registry lookup + delivery-plan route resolution
-> builder adapter selection with capability report
-> high-fidelity reference for key pages when polish matters
-> editable/hybrid PPT implementation
-> render/readback QA
-> rubric scoring + benchmark calibration where relevant
-> revision loop
-> package user-facing delivery + delivery-manifest.json
```

The critical rules are:

- Do not choose layout before knowing what the audience must understand or decide.
- Do not send a detailed design spec directly into PPT production unless the deck is low-risk and visually simple.
- Do not treat image generation as only a late-stage rescue. For relationship-heavy or conceptual slides, bounded visual components can be the correct planned delivery route.
- Do not treat the deck as final when only `deck.pptx` exists.
- Do not scatter process files into the user's final directory. Internal artifacts belong under `.ppt-work/`.
- Do not mark Premium `final` without real render evidence, readback, zero QA errors, and rubric pass.

### Production Profile Gate

Resolve the profile before artifact planning:

```bash
python3 scripts/resolve_production_profile.py \
  --requirements requirements.json \
  --ppt-ir .ppt-work/contracts/ppt-ir.json \
  --output .ppt-work/contracts/production-profile.json
```

Use only the artifacts required by the selected profile:

- `fast`: internal draft / content validation / simple article / explicit speed request.
- `standard`: formal internal report or ordinary client/product/technical/business deck.
- `premium`: public release, high-value client, template asset, strong brand requirement, complex diagrams, or explicit full validation request.

User override wins. Record the override and reason codes. Keep all internal work under `.ppt-work/`; deliver only the user-facing package plus `delivery-manifest.json`. Preserve `.ppt-work/` on failure. Premium should preserve it by default.

### Style Contract Gate

`style_id` alone is too abstract. The same style name produces visibly different decks across models because style descriptions only encode mood (e.g. "restrained color"). Every serious deck must resolve a complete `style-contract.json` before build. The contract is the source of truth for color, typography, grid, spacing, shape, shadows, cards, tables, charts, diagrams, images, icons, footer, density limits, effects, and forbidden drift.

Before building, do one of:

- **(a) Confirm with the user.** Present the candidate style(s), legacy palette aliases, and resulting token contract. Let the user pick `style_id` or an alias. If the user does not pick, fall back to the default fixture for the recommended style.
- **(b) Match a reference.** If the user supplied a reference image, brand deck, or explicit brand colors, extract the dominant primary / accent / background and pick the closest palette (or derive a new named palette and document it explicitly). Do not silently substitute.

Record the chosen `style_id`, compatibility alias or legacy palette source, and the resolved tokens in `style-contract.json` before any visual implementation. The build must read design parameters from this contract; do not invent hex values, font sizes, margins, radius values, table styles, chart colors, connector widths, crop modes, or footer styles at build time.

The contract must contain:

```json
{
  "schema_version": "2.0",
  "style_id": "consulting-light|product-report|technical-blueprint|consulting-blueprint-hybrid|editorial-knowledge",
  "display_name": "<human-readable name>",
  "colors": {
    "primary": "#RRGGBB",
    "accent": "#RRGGBB",
    "background": "#RRGGBB",
    "surface_1": "#RRGGBB",
    "surface_2": "#RRGGBB",
    "text_primary": "#RRGGBB",
    "text_secondary": "#RRGGBB",
    "border": "#RRGGBB"
  },
  "typography": {},
  "grid": {},
  "spacing": {},
  "card_tokens": {},
  "table_tokens": {},
  "chart_tokens": {},
  "diagram_tokens": {},
  "image_tokens": {},
  "footer_tokens": {},
  "density_limits": {}
}
```

Validate with:

```bash
python3 scripts/validate_contracts.py --style .ppt-work/contracts/style-contract.json --strict
```

### Component Delivery Route Gate

Before build, run Capability Probe and Component Registry resolution. The probe answers what this machine can actually do; the registry answers what each component is, which routes are allowed, which Builder levels are acceptable, what must remain editable, whether raster/SVG/generated output is allowed, and which QA checks are required.

Default registry:

```text
references/component-registry.json
```

Generate a capability report:

```bash
python3 scripts/capability_probe.py \
  --style .ppt-work/contracts/style-contract.json \
  --registry references/component-registry.json \
  --output .ppt-work/capability-report.json \
  --strict
```

Generate a delivery plan:

```bash
python3 scripts/resolve_component_delivery.py \
  --ppt-ir .ppt-work/contracts/ppt-ir.json \
  --style .ppt-work/contracts/style-contract.json \
  --registry references/component-registry.json \
  --capabilities .ppt-work/capability-report.json \
  --profile premium \
  --builder auto \
  --output .ppt-work/contracts/delivery-plan.json \
  --strict
```

Then validate:

```bash
python3 scripts/validate_contracts.py \
  --ppt-ir .ppt-work/contracts/ppt-ir.json \
  --style .ppt-work/contracts/style-contract.json \
  --component-registry references/component-registry.json \
  --delivery .ppt-work/contracts/delivery-plan.json \
  --strict
```

Never choose component routes ad hoc during drawing. Ordinary text, cards, tables, matrices, metric cards, and simple charts must remain native/editable. Complex diagrams may fall back to `hybrid_overlay` or `svg_component`; conceptual scenes may use `generated_image` with native title/caption/source overlay. `native_required` objects must not silently downgrade to SVG or image.

Before selecting a builder:

1. Run Capability Probe.
2. Match Component Registry against actual environment capabilities.
3. Select the builder with the highest editable-core coverage.
4. Do not use a visual-only adapter for native-required objects.
5. Record the requested builder, selected builder, version, selection score/reasons, and capability report path in the Build Manifest.
6. If no valid builder exists, stop at contracts and visual references.

Forbidden:

- assuming a Builder or Renderer exists because it is mentioned in the Skill
- continuing Premium when support is `unknown`
- using Visual Only output as if it were Native
- claiming Final without a real renderer for Premium

## Production Artifact Contract

For non-trivial decks, create only the artifacts required by the resolved profile. Internal artifacts go under `.ppt-work/`; user-facing output goes into the delivery folder.

Profile matrix:

| Artifact | Fast | Standard | Premium |
|---|---:|---:|---:|
| Content Lock | Required | Required | Required |
| Storyboard | Optional | Required | Required |
| PPT IR | Required | Required | Required |
| Style Contract | Required | Required | Required |
| Asset Manifest | If used | Required if used | Required |
| Delivery Plan | Required | Required | Required |
| Build Manifest | Required | Required | Required |
| Full Render | Optional | Representative | Required |
| QA Report | Basic | Required | Required |
| Benchmark Score | No | Optional | Required |
| Verification Report | No | Required | Required |
| Delivery Manifest | Required | Required | Required |

User-facing defaults:

- Fast: `deck.pptx`, `delivery-manifest.json`.
- Standard: `deck.pptx`, `deck-preview.pdf`, `verification-report.md`, `delivery-manifest.json`.
- Premium: Standard package plus optional `assets/` and `source-package/` only when intended for the recipient.

Use `templates/ppt-production-artifact-checklist.md` to confirm completeness.

## Master Design Language Gate

Before implementing a serious deck, load the references that match the deck's risk and style needs:

- `references/master-presentation-design-language.md`: overall design hierarchy and hybrid-editable principles.
- `references/expression-mode-gate.md`: mandatory when creating storyboard or slide manifest.
- `references/premium-page-archetypes.md`: mandatory when selecting page archetypes.
- `references/five-style-master-systems.md`: mandatory when choosing a style system. **This file is now the source of truth for palette hex values; do not derive colors elsewhere.**
- `references/spec-to-deck-visual-priority-gate.md`: mandatory when a detailed spec, coordinates, or placeholder map is provided.
- `references/component-craft-checklist.md`: mandatory before scoring or handoff.
- `references/component-registry.md`: mandatory before building; explains Component Registry and Delivery Plan routing.
- `references/builder-adapters.md`: mandatory before selecting a builder; explains capability reports, support levels, and adapter contracts.
- `references/diagram-ir-and-layout.md`: mandatory for `relationship_visual`; explains Diagram IR semantics, layout choice, complexity analysis, and delivery guidance.
- `references/diagram-auto-repair.md`: read when Diagram IR validation reports broken paths, unknown nodes, connector web risk, or type mismatch.
- `references/master-ppt-design-rubric.md`: mandatory for formal decks and final QA.
- `references/component-raster-fallback.md`: mandatory when using raster/SVG/generated visual components.
- `references/production-profiles.md`: mandatory before artifact planning or packaging.
- `references/production-readiness-gates.md`: mandatory for non-trivial decks.
- `references/anti-regression-examples.md`: read when quality regresses into bullets, connector webs, literal spec execution, or raster overuse.
- `references/benchmark-methodology.md`: read when running formal rubric scoring, comparing tool/prompt changes, or adding regression fixtures.

Templates:

- `templates/slide-manifest-template.json`
- `templates/style-contract-example.json`
- `templates/component-registry-example.json`
- `templates/capability-report-example.json`
- `templates/delivery-plan-example.json`
- `templates/delivery-manifest-example.json`
- `templates/diagram-ir-example.json`
- `templates/design-language-schema.json` (deprecated pointer only)
- `templates/spec-implementation-priority-schema.json`
- `templates/visual-qa-gate-template.json`
- `templates/content-lock-template.md`
- `templates/storyboard-template.md`
- `templates/benchmark-case-example.json`
- `templates/rubric-score-example.json`

Move in this order: content semantics -> expression mode -> Diagram IR for relationship visuals -> page architecture -> visual priority/deletion -> visual grammar -> delivery implementation -> verification and scoring.

## Readiness Gates

### Gate 1: Content Lock

Pass only when:

- each slide has a judgment title, not a topic title
- every major claim is sourced, inferred, or explicitly marked as an assumption
- no important source section is silently dropped
- dense paragraphs are transformed into structure, not copied as walls of text

Fail if the title could fit any generic deck, bullets are copied without prioritization, evidence and conclusion disconnect, or the slide would misrepresent the source.

### Gate 2: Expression Mode Lock

Run this before finalizing `slide_manifest.json`.

Every slide must choose exactly one `expression_mode`:

- `textual_argument`: answer-first title plus short support.
- `structured_cards`: parallel ideas or grouped examples.
- `table_matrix`: precise comparison, scoring, checklist, or coverage lookup.
- `data_visual`: magnitude, trend, ranking, contrast, distribution, or composition.
- `relationship_visual`: architecture, ecosystem, flow, causal chain, dependency, flywheel, stakeholder map, ownership boundary, trust boundary, or operating model.
- `conceptual_scene`: editorial illustration, IP/persona scene, metaphor, or abstract visual hook.
- `hybrid_panel`: one primary visual component plus concise interpretation.

Classify as `relationship_visual` when the source contains one strong trigger or two medium triggers from `references/expression-mode-gate.md`.

Pass only when every slide records:

- `expression_mode`
- `expression_mode_reason`
- `audience_question`
- `primary_anchor`
- `visual_component_plan` when the mode is `relationship_visual`, `conceptual_scene`, or visual-heavy `hybrid_panel`
- `visual_component_delivery` when the bounded component may be `native_ppt`, `svg_html_render`, `generated_image`, or `hybrid_generated_component`

Fail if relationship, flow, system boundary, feedback loop, ecosystem, causal chain, or spatial metaphor content remains pure prose or generic cards without deliberate simplification.

### Gate 3: Architecture Lock

Pass only when:

- every slide has exactly one primary anchor
- every slide has one page archetype
- density label matches actual content
- high-density pages have a structural reason to be dense
- tables/dashboards are not used as dumping grounds

Fail if two diagrams compete, a slide tries to explain workflow/metrics/risks at once, or layout is chosen before message.

### Gate 4: Spec Priority Lock

Use whenever the user provides a detailed design spec, coordinates, placeholder map, brand template, or page-by-page layout description.

A design spec is not a command to draw every listed object at full strength. Treat it as design intent plus candidate inventory.

Before PPT implementation, create `spec_implementation_plan.json` with:

- slide intent
- one primary visual anchor
- object roles and priorities
- keep/merge/weaken/move/delete decisions
- connector, icon, grid, table, and callout budgets
- editable core and material layers
- delivery route for complex visual components

Fail if detailed coordinates are executed literally, background or technical decoration competes with content, or connector webs appear.

### Gate 5: Visual Reference Lock

Use when the user expects polish, formal quality, style exploration, template creation, or public/client-facing delivery.

Pass only when:

- at least cover + one representative content page are previewed
- preview demonstrates typography, spacing, component style, and density
- preview is clearly labeled as non-final when not editable
- the direction can be reconstructed as hybrid-editable PPT

Fail if a final deck is built without seeing visual direction for a polish-sensitive request.

### Gate 6: PPT Implementation Lock

Pass only when:

- message-bearing content is editable
- material/raster layers are allowed and disclosed
- localized raster/SVG/generated components are bounded and intentional
- all key text fits within boxes
- representative slides render nonblank
- package/object counts match expected structure
- visual parameters used in implementation match `style-contract.json` exactly (no invented hex, type sizes, spacing, radius, table, chart, diagram, image, or footer values)

Fail if the deck is screenshot-only without explicit user acceptance, text clips, media is missing, or final report overclaims editability.

## Style Systems

Use style systems as complete design languages, not skins. **Every style is now bound to a strict Style Contract fixture** — see `tests/fixtures/styles/` and `references/five-style-master-systems.md`. The skill is no longer compatible with style descriptions that only encode mood; a model that invents its own colors or component parameters will produce off-contract output and fail the Style Contract Gate.

Default options (5 styles):

1. `consulting-light`: formal boardroom, evidence-heavy, answer-first. Palettes: `mckinsey` (default), `bcg`.
2. `product-report`: product strategy, metrics, roadmap, tradeoffs. Palettes: `linear` (default), `stripe`.
3. `technical-blueprint`: precise engineering workflow/architecture/runbook. Palette: `ibm-whitepaper` (default).
4. `consulting-blueprint-hybrid`: consulting hierarchy with restrained technical accents. Palette: `deep-amber` (default).
5. `editorial-knowledge`: premium knowledge deck for longform ideas. Palette: `warm-paper` (default).

For Agent systems, automation workflows, architecture, toolchains, permissions, failure modes, observability, OpenClaw/Codex workflows, or engineering strategy decks, prefer `consulting-blueprint-hybrid` unless the audience is purely implementation-focused.

## Production Template Packs

For a reusable v2 production starting point, select one validated pack before mapping slides:

- `references/template-packs/editorial-knowledge.json`: longform explainers, newsletters, courses, personal IP, and knowledge products.
- `references/template-packs/technical-blueprint.json`: implementation-focused architecture, workflow, runbook, and engineering evidence decks.

Validate packs against `schemas/template-pack.schema.json`. Each pack binds a v2 Style Contract to exactly six production roles (cover, judgment, evidence/data, process/relationship, comparison/implementation, and closing), current `primary_expression` modes, named Component Registry types, allowed delivery routes, editable-core policy, forbidden patterns, and truthful delivery constraints.

A template pack is **not** a screenshot library or dead master deck. It is reusable Style Contract plus archetype/component-routing policy. Resolve its component policies through `references/component-registry.json` and the normal Delivery Plan gate; do not treat a preferred route as proof that the active builder supports it. Keep message-bearing titles, arguments, data, labels, tables, diagrams, source notes, and actions editable as declared. Any bounded SVG, raster, background, or generated component must preserve the required native overlay and be disclosed. Pack selection does not waive render/readback/QA requirements or justify a Premium `final` claim without evidence.

## Technical Blueprint Refinement

Technical blueprint style must not become raw blueprint/wireframe. For client-facing or high-stakes technical decks:

- consulting-grade whitespace and answer-first titles
- technical diagrams as proof layer
- restrained grid/blueprint accents only when meaningful
- visible security, ownership, trust, failure, and observability boundaries when relevant
- minimal meaningful connectors
- precise labels, not label noise

Default technical noise budgets:

- background grid opacity: 4%-10%, or omit on dense pages
- connector lines: 3-9 meaningful lines
- decorative marks: max 3 per slide
- primary nodes: max 8 before grouping/splitting
- dashboard cards: max 4 KPI cards + 3 charts for ordinary slides
- tables: max 5 rows x 6 columns unless table is the single anchor

If a technical slide exceeds budget, group, split, move details to appendix/notes, or choose SVG/HTML/generated bounded component.

## Two-Lane Production Model

### Lane A: High-Fidelity Visual Reference

Use HTML/CSS, code-rendered references, screenshots, or contact sheets to calibrate typography, material/background systems, layout rhythm, component style, and density.

This lane may use browser-level craft, but do not pretend the screenshot is editable PPT.

### Lane B: Editable Delivery Reconstruction

Build final PPTX from structured manifest or generation code.

Keep editable as native PPT objects:

- slide titles, subtitles, body text
- captions and source notes
- cards and callout boxes
- tables and simple charts
- flow diagrams, issue trees, timelines, matrices, and simple architecture diagrams
- meaningful connectors and labels

Allow raster/SVG/generated layers for material backgrounds, photos, illustrations, IP character art, complex relationship maps, conceptual scenes, ecosystem maps, dense architecture murals, or soft-boundary components.

## Component Raster And Generated Delivery

Use `references/component-raster-fallback.md` whenever considering raster/SVG/generated components.

For `relationship_visual`, `conceptual_scene`, and visual-heavy `hybrid_panel`, bounded visual components are a planned delivery strategy, not merely late-stage rescue.

Good candidates:

- complex relationship maps with many cross-links
- ecosystem maps or stakeholder networks
- capability landscapes with nested regions and soft boundaries
- conceptual metaphors or abstract spatial structures
- dense architecture murals where visual comprehension matters more than direct editing
- illustrated process scenes, IP illustrations, or editorial visual metaphors
- complex textures, material backgrounds, photos, or atmospheric layers

Poor candidates:

- 2x2, 2x3, or 3x3 card grids
- ordinary comparison matrices
- tables and scorecards
- metric cards
- simple process lanes
- clean issue trees or dependency trees
- simple architecture diagrams with modest connector counts
- already-stabilized layouts after reducing connectors, grouping, or switching to cards

When using raster/SVG/generated components:

- crop to the component region, not the full slide
- keep title, interpretation line, source note, footer, legend, and key labels editable where practical
- store prompt/source path in the project directory
- disclose the component in `verification-report.md`
- count media objects and confirm only intended components are rasterized

## Relationship Diagram Contract

When `primary_expression=relationship_visual`:

1. Do not draw directly from prose.
2. Create or reference a valid Diagram IR.
3. Identify nodes, groups, edges, boundaries, annotations, and main paths.
4. Validate Diagram IR before selecting a delivery route.
5. Use relationship semantics to choose line styles.
6. Preserve one visually dominant main path or relationship structure.
7. Use Component Registry and Delivery Resolver.
8. Simplify, cluster, annotate, or split before falling back to raster.

Do not:

- convert relationship-heavy content into generic cards by default;
- assign equal visual priority to every edge;
- use curves merely for decoration;
- draw connectors through nodes;
- place large paragraphs inside nodes;
- rasterize the entire relationship slide;
- claim a diagram is editable when labels and nodes are embedded in one image.

## Scoring And Revision

Use `references/master-ppt-design-rubric.md`. A production slide must score at least `14/18`, with no zero.

Six dimensions:

1. Judgment quality.
2. Content fidelity and evidence.
3. Expression mode and page architecture.
4. Page composition.
5. Component craft and style consistency.
6. Editability and delivery hygiene.

Revise before final handoff if any are true:

- average score below 14/18
- any dimension scores 0
- more than 20% of slides have topic titles
- more than 15% of slides have clipped or overlapping text
- any formal deck page looks like raw wireframe/spec coverage output
- any key technical diagram has connector web or unclear boundaries
- any claimed editable core is rasterized
- ordinary card/matrix/table/metric content is rasterized without explicit user approval
- implementation visual parameters do not match `style-contract.json`

## Visual QA Gate

Before final handoff:

1. Inspect package structure.
2. Count editable text and media objects when possible.
3. Run the Stage 6 verifier:
   `python3 scripts/verify_deck.py deck.pptx --ppt-ir .ppt-work/contracts/ppt-ir.json --style .ppt-work/contracts/style-contract.json --delivery .ppt-work/contracts/delivery-plan.json --build .ppt-work/contracts/build-manifest.json --render --output .ppt-work/qa/qa-report.json`
4. Render with PowerPoint, Keynote, LibreOffice, or another real available route. If no renderer is available, preserve `RENDER_ENGINE_UNAVAILABLE`, return/carry the unavailable status, and cap final status honestly. Do not create fake screenshots or claim visual QA passed.
5. Inspect representative screenshots/contact sheets when they exist.
6. Check blank slides, clipped text, overlaps, missing images, aspect ratio, private local paths, connector webs, high-contrast grids, and cramped matrices.
7. Confirm any raster/SVG/generated component is intentional, bounded, disclosed, and not replacing ordinary editable card/table/matrix content.
8. **Confirm every fill, stroke, text color, font size, spacing, radius, connector, table, chart, image, and footer value in the build matches `style-contract.json` exactly.** Drift from the contract is a defect, not a creative choice.
9. For repair, use `python3 scripts/repair_deck.py deck.pptx --qa-report .ppt-work/qa/qa-report.json --output-pptx .ppt-work/qa/repaired.pptx --output-report .ppt-work/qa/repair-report.json`. Only safe deterministic repairs may be attempted; never mark visual/render issues repaired without a real render recheck.
10. Revise and re-render if issues are found.
11. Package the user-facing delivery with `scripts/package_delivery.py`; validate `delivery-manifest.json` and keep `.ppt-work/` if packaging fails.

Final status must distinguish `planned`, `created`, `rendered`, `read_back`, `verified`, `final`, and `failed`. The status is calculated from Build Manifest, QA Report, and benchmark evidence. Builders and agents must not handwrite `final`; Premium without real render evidence is not final.

## Privacy And Cloud Export

Local PPTX export is the safer default for sensitive drafts, PRDs, internal metrics, automation designs, and unpublished content. Only upload/share to Feishu/Lark Slides when the user explicitly requests cloud delivery and the content is appropriate.

## Default Workflow

1. Resolve trigger and production profile.
2. Analyze source and evidence.
3. Create PPT IR.
4. Validate title role and expression.
5. Resolve Style Contract.
6. Resolve component delivery routes.
7. Build visual reference only when needed.
8. Build PPTX through available adapter.
9. Run verification harness.
10. Repair and re-run when deterministic repairs are safe.
11. Deliver trusted status and report.

Keep this main workflow as routing only. Use references for detailed gates:
`production-profiles.md`, `expression-mode-gate.md`, `design-token-contract.md`,
`component-registry.md`, `diagram-ir-and-layout.md`, `builder-adapters.md`,
`verification-harness.md`, and `production-readiness-gates.md`.

## Lessons From Recent Trials

- McKinsey-style specs work well when they encode hierarchy, restraint, and deletion-by-implication.
- Technical blueprint specs underperform when executed literally because grids, nodes, connectors, labels, and tables compound into visual noise.
- Detailed coordinates are not enough. A production-grade spec needs visual priority, deletion rules, density budgets, and component craft expectations.
- For Agent/system decks, target `consulting-blueprint-hybrid`: consulting structure with technical proof components, not raw blueprint drafting.
- Localized image generation is useful for complex relationship diagrams, ecosystem maps, conceptual visuals, and material layers; it is usually wrong for clean card grids, matrices, tables, and metric cards because it destroys useful editability without solving a structural problem.
- Style descriptions that only encode mood ("restrained color") produce visibly different decks across models. Pin complete design tokens into each style contract and confirm them with the user before building.
- Do not introduce a style into the enumeration until its strict style fixture validates. Half-defined styles are a defect source.

---

## FILE: references/five-style-master-systems.md

# Five Style Master Systems

Use style systems as complete design languages, not skins. **Every style in this file is bound to one or more named palette contracts with exact hex values.** The build must read colors from `style_contract.json`; do not invent hex values at build time. If a style needs a new palette, add it to this file first, then update `style_contract.json` to reference it.

Global color usage rules (apply to every palette):

- `primary`: title bars, main color blocks, key structural elements, top-of-page header strips, large callout blocks.
- `accent`: data highlights, single-emphasis callouts, key numbers, focused labels. **Never use accent as a large fill or as a page background.**
- `background`: page base. The whole slide sits on this color.
- `neutrals` (3 grays): body text, secondary text, dividers, borders, subtle fills, table strokes. Choose values that harmonize with the palette.
- Reserve at least 70% of any slide for background + neutrals; primary and accent together should occupy at most ~30% of a slide's visual weight, with accent far less than primary.

---

## consulting-light

Boardroom, evidence-heavy, answer-first, decision-oriented. Use for formal reports, executive updates, market analysis, investor-style briefs, and McKinsey-like decks. White space, strong titles, restrained color, and clean proof components matter more than visual novelty.

Available palettes:

### `mckinsey` (default)

| Token | Hex | Use |
| --- | --- | --- |
| primary | `#051C2C` | deep navy titles, header bars, primary structural blocks |
| accent | `#2251FF` | single-emphasis data highlights, key callouts |
| background | `#FFFFFF` | page base |
| neutral-900 (text) | `#1F2937` | body text, judgment titles |
| neutral-500 (muted) | `#6B7280` | secondary text, source notes, captions |
| neutral-200 (border/fill) | `#E5E7EB` | dividers, table strokes, subtle card fills |

### `bcg`

| Token | Hex | Use |
| --- | --- | --- |
| primary | `#004C2F` | deep green titles, header bars, primary structural blocks |
| accent | `#00823B` | single-emphasis data highlights, key callouts |
| background | `#F9F9F9` | page base |
| neutral-900 (text) | `#1F2937` | body text, judgment titles |
| neutral-500 (muted) | `#6B7280` | secondary text, source notes, captions |
| neutral-200 (border/fill) | `#E5E7EB` | dividers, table strokes, subtle card fills |

---

## product-report

Modern product strategy deck with metrics, roadmap, tradeoffs, operating decisions, and user/business evidence. Use for PRDs, MVP plans, retrospectives, roadmap proposals, and launch reviews.

Available palettes:

### `linear` (default)

| Token | Hex | Use |
| --- | --- | --- |
| primary | `#1A1A2E` | near-black titles, header bars, primary structural blocks |
| accent | `#7B68EE` | medium-violet single-emphasis data highlights, key callouts |
| background | `#F7F7FB` | cool off-white page base |
| neutral-900 (text) | `#1F2937` | body text, judgment titles |
| neutral-500 (muted) | `#6B7280` | secondary text, source notes, captions |
| neutral-200 (border/fill) | `#E5E7EB` | dividers, table strokes, subtle card fills |

### `stripe`

| Token | Hex | Use |
| --- | --- | --- |
| primary | `#0F0F0F` | near-black titles, header bars, primary structural blocks |
| accent | `#0055FF` | bright blue single-emphasis data highlights, key callouts |
| background | `#FAFAFA` | page base |
| neutral-900 (text) | `#1A1A1A` | body text, judgment titles |
| neutral-500 (muted) | `#6B6E73` | secondary text, source notes, captions |
| neutral-200 (border/fill) | `#E6E6E9` | dividers, table strokes, subtle card fills |

---

## technical-blueprint

Precise executable engineering deck with lanes, nodes, boundaries, failure modes, observability, and runbooks. Use when implementation detail is the audience's main need. Keep diagrams disciplined and avoid raw tool-screenshot aesthetics. Light-mode, formal technical whitepaper / RFC feel, print-friendly.

Available palettes:

### `ibm-whitepaper` (default)

| Token | Hex | Use |
| --- | --- | --- |
| primary | `#005A9E` | IBM blue titles, header bars, primary structural blocks, node outlines |
| accent | `#005A9E` | single-emphasis highlights (same as primary; rely on weight and isolation rather than a second hue) |
| background | `#FAFAFA` | page base |
| secondary-surface | `#F0F4F8` | panel / code-block / table-header fills |
| neutral-900 (text) | `#1F2937` | body text, judgment titles |
| neutral-500 (muted) | `#4B5563` | secondary text, source notes, captions |
| neutral-200 (border/fill) | `#D1D5DB` | dividers, table strokes, subtle card fills |

When accent and primary are identical, use neutral-700 `#374151` as the de-facto "second accent" for a second tier of emphasis (e.g. secondary nodes) so the deck does not collapse to monochrome.

---

## consulting-blueprint-hybrid

Formal consulting hierarchy with restrained technical blueprint accents. Use for Agent systems, automation workflows, architecture strategy, platform operating models, and technical decks for business audiences. The slide should feel like consulting output first and engineering blueprint second. Consulting-first, restrained amber-gold technical accent.

Available palettes:

### `deep-amber` (default)

| Token | Hex | Use |
| --- | --- | --- |
| primary | `#1B2A4A` | deep navy titles, header bars, primary structural blocks |
| accent | `#E8A838` | restrained amber-gold single-emphasis highlights, key callouts |
| background | `#F9FAFB` | page base |
| neutral-900 (text) | `#2D3748` | body text, judgment titles (slightly differentiated from primary navy) |
| neutral-500 (muted) | `#4A5568` | secondary text, source notes, captions |
| neutral-200 (border/fill) | `#E2E8F0` | dividers, table strokes, subtle card fills |

Use accent `#E8A838` sparingly: it is a highlight, not a fill. A small accent block, an underline beneath a number, or a single labeled arrow is enough.

---

## editorial-knowledge

Premium knowledge deck that turns longform writing into frameworks, contrasts, steps, mistakes, examples, and memorable ideas. Use for explainers, newsletters, courses, personal IP, and knowledge products. Paper texture, knowledge-blogger feel.

Available palettes:

### `warm-paper` (default)

| Token | Hex | Use |
| --- | --- | --- |
| primary | `#2D2926` | warm dark titles, header bars, primary structural blocks |
| accent | `#E8633A` | warm orange-red single-emphasis highlights, key callouts |
| background | `#FAF7F2` | warm paper page base |
| neutral-900 (text) | `#4A4540` | body text, judgment titles (warm dark, harmonized with primary) |
| neutral-500 (muted) | `#7A736D` | secondary text, source notes, captions |
| neutral-200 (border/fill) | `#E5E0D8` | dividers, table strokes, subtle card fills (warm beige) |

---

## FILE: templates/design-language-schema.json

```json
{
  "style_system": "consulting-light|product-report|technical-blueprint|consulting-blueprint-hybrid|editorial-knowledge",
  "palette_name": "string (must match a named palette under the chosen style_system)",
  "audience": "",
  "formality": "draft|internal|executive|client|public",
  "colors": {
    "primary": "#RRGGBB (required, must match palette)",
    "accent": "#RRGGBB (required, must match palette)",
    "background": "#RRGGBB (required, must match palette)",
    "secondary_surface": "#RRGGBB (optional, required for technical-blueprint)",
    "neutrals": ["#RRGGBB", "#RRGGBB", "#RRGGBB"]
  },
  "usage_rules": {
    "primary": "title bars, main color blocks, key structural elements",
    "accent": "data highlights, single-emphasis callouts, never as large fill",
    "background": "page base",
    "neutrals": "body text, dividers, secondary fills"
  },
  "typography": {
    "title_role": "judgment title",
    "body_role": "evidence or interpretation",
    "minimum_body_size_pt": 10
  },
  "layout": {
    "grid": "",
    "spacing_rules": [],
    "density_limits": []
  },
  "components": {
    "cards": "",
    "tables": "",
    "charts": "",
    "relationship_diagrams": "",
    "raster_layers": ""
  },
  "forbidden_drift": []
}
```

---

## FILE: templates/slide-manifest-template.json

```json
{
  "deck": {
    "source": "",
    "source_rights": "owned|licensed|external-reference|unknown",
    "usage_boundary": "private draft|internal review|public sharing|client delivery|training|publication",
    "export_target": "pptx|native-dynamic-pptx|html-preview|dynamic-html|feishu-slides|multi",
    "audience": "",
    "visual_system": "consulting-light|product-report|technical-blueprint|consulting-blueprint-hybrid|editorial-knowledge",
    "palette_name": "string (must match a named palette under visual_system)",
    "logical_slide_count": 0,
    "physical_slide_count": 0,
    "content_lock": "content_analysis.md",
    "storyboard": "storyboard.md",
    "style_contract": "style_contract.json",
    "verification_report": "verification-report.md"
  },
  "slides": [
    {
      "logical_slide_id": "S01",
      "title": "",
      "judgment_title": "",
      "content_lock_ref": "content_analysis.md#slide-1",
      "physical_slide_ids": ["pptx-slide-1"],
      "page_archetype": "claim-evidence|metric-proof|framework-map|process-lane|system-architecture|ecosystem-map|decision-matrix|risk-register|observability-dashboard|comparison-contrast|editorial-scene|closing-standard",
      "density_label": "low|medium|high",
      "primary_anchor": "",
      "audience_question": "",
      "expression_mode": "textual_argument|structured_cards|table_matrix|relationship_visual|conceptual_scene|data_visual|hybrid_panel",
      "expression_mode_reason": "",
      "relationship_types": [],
      "visual_component_plan": {
        "component_type": "none|ecosystem map|dependency graph|layered architecture|swimlane|flywheel|causal chain|stakeholder network|capability landscape|conceptual scene|chart",
        "audience_question": "",
        "primary_entities": [],
        "relationship_types": [],
        "simplification_strategy": "grouping|lanes|layers|split slide|appendix|label reduction|not needed",
        "editable_core": [],
        "visual_component_delivery": "native_ppt|svg_html_render|generated_image|hybrid_generated_component|none",
        "raster_acceptance_reason": ""
      },
      "editable_text_objects": [],
      "must_keep_editable_text": [],
      "visual_objects": [],
      "images": [],
      "charts": [],
      "tables": [],
      "asset_provenance": [],
      "source_labels": [],
      "rasterization_tradeoff": "none|bounded_component|material_layer|full_slide_approved",
      "score": {
        "judgment_quality": "unknown",
        "content_fidelity": "unknown",
        "expression_architecture": "unknown",
        "page_composition": "unknown",
        "component_craft": "unknown",
        "editability_hygiene": "unknown",
        "total": "unknown"
      },
      "verification": {
        "nonblank_render": "unknown",
        "text_overflow": "unknown",
        "editable_core_text": "unknown",
        "visual_structure_preserved": "unknown",
        "source_labels_present": "unknown",
        "raster_component_disclosed": "unknown"
      }
    }
  ]
}
```
