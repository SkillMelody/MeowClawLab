---
name: "article-html-to-ppt"
description: "Use when converting articles/docs to polished hybrid-editable PPT decks"
---

# Article HTML To PPT

Convert articles, Markdown drafts, HTML pages, WeChat drafts, PRDs, automation plans, knowledge posts, design specs, and review-approved manuscripts into polished, low-rework, persona-fit slide decks.

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
9. Render/readback verification before final handoff.
10. Honest reporting of rasterized layers and conversion limits.

## Standard Production Chain

Use this chain for serious decks:

```text
source/article/design brief
-> content analysis and evidence inventory
-> slide storyline and judgment titles
-> expression mode gate
-> slide_manifest.json with expression plan
-> style selection and page archetype mapping
-> STYLE & PALETTE CONFIRMATION GATE (confirm with user OR match reference)
-> detailed design specification
-> visual priority map + deletion/noise budget
-> delivery-route decision for complex visual components
-> high-fidelity reference for key pages when polish matters
-> editable/hybrid PPT implementation
-> render/readback QA
-> rubric scoring + revision loop
-> final PPTX + verification report
```

The critical rules are:

- Do not choose layout before knowing what the audience must understand or decide.
- Do not send a detailed design spec directly into PPT production unless the deck is low-risk and visually simple.
- Do not treat image generation as only a late-stage rescue. For relationship-heavy or conceptual slides, bounded visual components can be the correct planned delivery route.
- Do not treat the deck as final when only `deck.pptx` exists.

### Style & Palette Confirmation Gate

`style_system` alone is too abstract. The same style name produces visibly different decks across models because style descriptions only encode mood (e.g. "restrained color"). Every style in this skill is now bound to one or more **named palette contracts** with exact hex values (see `references/five-style-master-systems.md`). Before building, do one of:

- **(a) Confirm with the user.** Present the candidate style(s) and the palette options under each style. Let the user pick `style_system` + `palette_name`. If the user does not pick, fall back to the default palette of the recommended style.
- **(b) Match a reference.** If the user supplied a reference image, brand deck, or explicit brand colors, extract the dominant primary / accent / background and pick the closest palette (or derive a new named palette and document it explicitly). Do not silently substitute.

Record the chosen `style_system` + `palette_name` and the resolved hex values in `style_contract.json` before any visual implementation. The build must read colors from this contract; do not invent hex values at build time.

The contract must contain:

```json
{
  "style_system": "consulting-light|product-report|technical-blueprint|consulting-blueprint-hybrid|editorial-knowledge",
  "palette_name": "<one of the named palettes for that style>",
  "colors": {
    "primary": "#RRGGBB",
    "accent": "#RRGGBB",
    "background": "#RRGGBB",
    "neutrals": ["#RRGGBB", "#RRGGBB", "#RRGGBB"]
  },
  "usage_rules": {
    "primary": "title bars, main color blocks, key structural elements",
    "accent": "data highlights, single-emphasis callouts, never as large fill",
    "background": "page base",
    "neutrals": "body text, dividers, secondary fills"
  }
}
```

## Production Artifact Contract

For non-trivial decks, create these artifacts in the project directory:

1. `content_analysis.md`: thesis, audience, evidence inventory, risks/caveats, reusable terms.
2. `storyboard.md`: slide sequence, judgment titles, audience action, source coverage.
3. `slide_manifest.json`: page archetypes, density, primary anchor, expression mode, visual component plan, editable core, raster allowance.
4. `style_contract.json`: style system, palette name, exact colors (primary/accent/background/neutrals), typography, layout primitives, usage rules, forbidden drift.
5. `detailed_design_spec.md` or `design_spec.json`: page-level implementation details.
6. `spec_implementation_plan.json`: visual priority map, deletion rules, noise budget, object roles, delivery route.
7. `visual_reference/`: at least cover + one representative content page when polish matters.
8. `deck.pptx`: final editable or hybrid-editable deck.
9. `verification-report.md`: object counts, media count, render/readback route, known limits.
10. `delivery-manifest.json`: canonical paths and final status.

Use `templates/ppt-production-artifact-checklist.md` to confirm completeness.

## Master Design Language Gate

Before implementing a serious deck, load the references that match the deck's risk and style needs:

- `references/master-presentation-design-language.md`: overall design hierarchy and hybrid-editable principles.
- `references/expression-mode-gate.md`: mandatory when creating storyboard or slide manifest.
- `references/premium-page-archetypes.md`: mandatory when selecting page archetypes.
- `references/five-style-master-systems.md`: mandatory when choosing a style system. **This file is now the source of truth for palette hex values; do not derive colors elsewhere.**
- `references/spec-to-deck-visual-priority-gate.md`: mandatory when a detailed spec, coordinates, or placeholder map is provided.
- `references/component-craft-checklist.md`: mandatory before scoring or handoff.
- `references/master-ppt-design-rubric.md`: mandatory for formal decks and final QA.
- `references/component-raster-fallback.md`: mandatory when using raster/SVG/generated visual components.
- `references/production-readiness-gates.md`: mandatory for non-trivial decks.
- `references/anti-regression-examples.md`: read when quality regresses into bullets, connector webs, literal spec execution, or raster overuse.

Templates:

- `templates/slide-manifest-template.json`
- `templates/design-language-schema.json`
- `templates/spec-implementation-priority-schema.json`
- `templates/visual-qa-gate-template.json`
- `templates/content-lock-template.md`
- `templates/storyboard-template.md`

Move in this order: content semantics -> expression mode -> page architecture -> visual priority/deletion -> visual grammar -> delivery implementation -> verification and scoring.

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
- colors used in implementation match `style_contract.json` exactly (no invented hex values)

Fail if the deck is screenshot-only without explicit user acceptance, text clips, media is missing, or final report overclaims editability.

## Style Systems

Use style systems as complete design languages, not skins. **Every style is now bound to one or more named palette contracts with exact hex values** — see `references/five-style-master-systems.md` for the palette table. The skill is no longer compatible with style descriptions that only encode mood; a model that invents its own colors will produce off-brand output and fail the Style & Palette Confirmation Gate.

Default options (5 styles):

1. `consulting-light`: formal boardroom, evidence-heavy, answer-first. Palettes: `mckinsey` (default), `bcg`.
2. `product-report`: product strategy, metrics, roadmap, tradeoffs. Palettes: `linear` (default), `stripe`.
3. `technical-blueprint`: precise engineering workflow/architecture/runbook. Palette: `ibm-whitepaper` (default).
4. `consulting-blueprint-hybrid`: consulting hierarchy with restrained technical accents. Palette: `deep-amber` (default).
5. `editorial-knowledge`: premium knowledge deck for longform ideas. Palette: `warm-paper` (default).

For Agent systems, automation workflows, architecture, toolchains, permissions, failure modes, observability, OpenClaw/Codex workflows, or engineering strategy decks, prefer `consulting-blueprint-hybrid` unless the audience is purely implementation-focused.

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
- implementation colors do not match `style_contract.json`

## Visual QA Gate

Before final handoff:

1. Inspect package structure.
2. Count editable text and media objects when possible.
3. Render with QuickLook, PowerPoint, Keynote, OfficeCLI, LibreOffice, or another available route.
4. Inspect representative screenshots/contact sheets.
5. Check blank slides, clipped text, overlaps, missing images, aspect ratio, private local paths, connector webs, high-contrast grids, and cramped matrices.
6. Confirm any raster/SVG/generated component is intentional, bounded, disclosed, and not replacing ordinary editable card/table/matrix content.
7. **Confirm every fill, stroke, and text color in the build matches `style_contract.json` exactly.** Drift from the contract is a defect, not a creative choice.
8. Revise and re-render if issues are found.
9. Write `verification-report.md` for non-trivial decks.

Final status must distinguish `Created`, `Rendered`, `Read back`, and `Final`.

## Privacy And Cloud Export

Local PPTX export is the safer default for sensitive drafts, PRDs, internal metrics, automation designs, and unpublished content. Only upload/share to Feishu/Lark Slides when the user explicitly requests cloud delivery and the content is appropriate.

## Default Workflow

1. Read source and identify audience/persona.
2. Extract semantic units, evidence inventory, entities, and relationship clues.
3. Create storyline and lock slide-level judgment titles.
4. Run Expression Mode Gate for every slide.
5. Create `slide_manifest.json` with expression mode and visual component plans.
6. **Run Style & Palette Confirmation Gate**: confirm `style_system` + `palette_name` with the user (or match a reference), and write `style_contract.json` with exact hex values.
7. Create detailed design specification (using contract colors only).
8. Create visual priority map, deletion rules, and noise budget.
9. Decide delivery route for complex visual components: `native_ppt`, `svg_html_render`, `generated_image`, or `hybrid_generated_component`.
10. Create high-fidelity visual reference for cover + representative content page when polish matters.
11. Build final PPTX using hybrid editable reconstruction, reading all colors from `style_contract.json`.
12. Apply component craft checklist and score with the master rubric.
13. Verify object counts, color compliance, and representative render/readback.
14. Report editability and rasterization honestly.

## Lessons From Recent Trials

- McKinsey-style specs work well when they encode hierarchy, restraint, and deletion-by-implication.
- Technical blueprint specs underperform when executed literally because grids, nodes, connectors, labels, and tables compound into visual noise.
- Detailed coordinates are not enough. A production-grade spec needs visual priority, deletion rules, density budgets, and component craft expectations.
- For Agent/system decks, target `consulting-blueprint-hybrid`: consulting structure with technical proof components, not raw blueprint drafting.
- Localized image generation is useful for complex relationship diagrams, ecosystem maps, conceptual visuals, and material layers; it is usually wrong for clean card grids, matrices, tables, and metric cards because it destroys useful editability without solving a structural problem.
- Style descriptions that only encode mood ("restrained color") produce visibly different decks across models. Pin exact hex values into each style and confirm them with the user before building.
- Do not introduce a style into the enumeration until its palette contract is written. Half-defined styles are a defect source.

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
