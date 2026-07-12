---
name: "article-html-to-ppt"
description: "PPT skill for polished hybrid-editable decks"
---

# Article HTML To PPT

Convert articles, Markdown drafts, HTML pages, WeChat drafts, PRDs, automation plans, knowledge posts, design specs, and review-approved manuscripts into polished, low-rework, persona-fit slide decks.

## Core Standard

Optimize in this order:

1. Content truth and source boundaries.
2. Storyline and slide-level message clarity.
3. Persona-fit structure and proof style.
4. Design intent fidelity, not blind spec literalism.
5. Master-level visual design language.
6. Editability of core text, cards, diagrams, tables, and simple charts.
7. Render/readback verification before final handoff.
8. Honest reporting of rasterized layers and conversion limits.

Default delivery should be `Hybrid editable`: polished material/background layers may be raster or SVG, while message-bearing content remains editable PowerPoint objects. Avoid both extremes: screenshot-only decks that cannot be edited, and pure native-object decks that look like rough wireframes.

## Updated Standard PPT Production Chain

Use this as the default chain for serious decks:

```text
source/article/design brief
-> content analysis and evidence inventory
-> slide storyline and judgment titles
-> slide_manifest.json
-> style selection and page archetype mapping
-> detailed design specification
-> visual priority map + deletion/noise budget
-> high-fidelity reference for key pages when polish matters
-> editable/hybrid PPT implementation
-> render/readback QA
-> revision loop
-> final PPTX + verification report
```

The critical update is this:

```text
detailed design specification -> visual priority map + deletion/noise budget -> PPT implementation
```

Do not send a detailed design spec directly into PPT production unless the deck is low-risk and visually simple. A detailed spec can over-specify coordinates, placeholders, grids, connectors, and decorative marks. Before implementation, decide what matters, what should be weakened, what should be merged, and what should be deleted.

## Production Artifact Contract

For non-trivial decks, create these artifacts in the project directory:

1. `content_analysis.md`: thesis, audience, evidence inventory, risks/caveats, reusable terms.
2. `storyboard.md`: slide sequence, slide judgments, audience action, source coverage.
3. `slide_manifest.json`: page archetypes, density, primary anchor, editable core, raster allowance.
4. `style_contract.json`: style system, typography, color, layout primitives, forbidden drift.
5. `detailed_design_spec.md` or `design_spec.json`: page-level implementation details.
6. `spec_implementation_plan.json`: visual priority map, deletion rules, noise budget, object roles.
7. `visual_reference/`: at least cover + one representative content page when polish matters.
8. `deck.pptx`: final editable or hybrid-editable deck.
9. `verification-report.md`: object counts, media count, render/readback route, known limits.
10. `delivery-manifest.json`: canonical paths and final status.

Do not treat the deck as final when only `deck.pptx` exists. The intermediate artifacts are how quality survives retries, interruptions, and later edits.

## Readiness Gates

### Gate 1: Content Lock

Pass only when:

- each slide has a judgment title, not a topic title
- every major claim is sourced, inferred, or explicitly marked as an assumption
- no important source section is silently dropped
- dense paragraphs are transformed into structure, not copied as walls of text

Fail triggers:

- title could fit any generic deck
- bullets are copied from source without prioritization
- evidence and conclusion are disconnected
- user-facing deck would misrepresent the source

### Gate 2: Architecture Lock

Pass only when:

- every slide has exactly one primary anchor
- every slide has one page archetype
- density label matches actual content
- high-density pages have a structural reason to be dense
- tables/dashboards are not used as dumping grounds

Fail triggers:

- two diagrams compete on one slide
- a page tries to explain workflow, metrics, and risks at once
- a table is too dense for its intended audience
- layout is chosen before message is clear

### Gate 3: Spec Priority Lock

Pass only when:

- every object has role and priority
- low-priority objects are deleted, merged, weakened, or moved to notes
- grid/connector/icon/table budgets are explicit
- the implementation plan preserves design intent instead of raw object count

Fail triggers:

- detailed coordinates are executed without hierarchy review
- background or technical decoration competes with content
- connector web appears
- icon/label repetition creates noise

### Gate 4: Visual Reference Lock

Use when the user expects polish, formal quality, style exploration, template creation, or public/client-facing delivery.

Pass only when:

- at least cover + one representative content page are visually previewed
- preview demonstrates typography, spacing, component style, and density
- the user or agent can compare the direction before full PPT construction
- screenshot/reference is clearly labeled as non-final if not editable

Fail triggers:

- final deck is built without seeing any visual direction
- visual reference looks good but cannot be reconstructed editably
- reference uses effects that cannot be transferred or approximated

### Gate 5: PPT Implementation Lock

Pass only when:

- message-bearing content is editable
- material/raster layers are allowed and disclosed
- localized raster fallback is limited to intended complex components
- all key text fits within boxes
- representative slides render nonblank
- package/object counts match expected structure

Fail triggers:

- whole deck is screenshot-only without explicit user acceptance
- text, table, or chart labels clip or overlap
- file renders blank or missing images
- final report overclaims editability
- ordinary card grids, matrices, tables, or metric cards are rasterized without user approval

## Design Spec Execution Gate

Use this gate whenever the user provides a detailed PPT design spec, coordinates, placeholder map, brand template, visual grammar, or page-by-page layout description.

A design spec is not a command to draw every listed placeholder at full strength. Treat it as design intent plus a candidate object inventory.

Before PPT implementation, create a `spec_implementation_plan`:

1. Identify the intent of each slide.
2. Assign one primary visual anchor.
3. Assign visual priority to every requested object.
4. Decide what to keep, merge, weaken, move to notes, or delete.
5. Convert coordinates into a responsive grid only after hierarchy is clear.
6. Set a noise budget for grid lines, connectors, labels, decorative marks, and icons.
7. Define the editable core and material layer.
8. Run a preflight composition score before generating the PPT.

### Visual Priority And Deletion Rules

Every object must have one role:

- `message`: states the slide's judgment
- `proof`: supports the judgment
- `structure`: organizes reading order
- `navigation`: orientation, page number, section marker
- `brand`: restrained identity cue
- `material`: mood/background atmosphere
- `decoration`: optional visual texture

Priority levels:

| Priority | Meaning | Treatment |
| --- | --- | --- |
| `hero` | Main visual anchor | largest, clearest, never competes with another hero |
| `primary` | Required for meaning | editable, high contrast, aligned to grid |
| `secondary` | Supports reading | smaller, grouped, lower contrast |
| `tertiary` | Context or atmosphere | low contrast, may be moved to notes/footer |
| `delete` | Noise or duplication | remove before implementation |

Hard deletion triggers:

- decorative grid competes with text or charts
- connector line does not clarify flow or dependency
- icon repeats the label without adding meaning
- table cell forces body text below minimum size
- more than two callout systems compete on one slide
- multiple diagrams explain the same relationship
- background motif occupies attention needed by the primary anchor

## Technical Blueprint Refinement Gate

Use for Agent systems, automation workflows, architecture, toolchains, permissions, failure modes, observability, runbooks, OpenClaw/Codex workflows, or other engineering decks.

Technical blueprint style must not become a raw blueprint/wireframe. For client-facing or high-stakes technical decks, default to `consulting-blueprint-hybrid`:

- consulting-grade white space and answer-first titles
- technical diagrams as the main proof layer
- restrained blueprint/grid only as material layer
- visible security/failure/observability boundaries when relevant
- minimal but meaningful connectors
- precise labels, not label noise

### Technical Blueprint Noise Budget

Per slide defaults:

- Background grid opacity: 4%-10% equivalent, or omit on dense pages.
- Connector lines: 3-9 meaningful lines; more requires grouping or lane structure.
- Decorative crosses/circles/technical marks: max 3 per slide, never near dense text.
- Node labels: max 8 primary nodes; collapse the rest into grouped modules.
- Dashboard cards: max 4 KPI cards + 3 charts for ordinary slides; 6 charts only for a true dashboard page.
- Tables: max 5 rows x 6 columns unless the slide's single anchor is the table.

If a technical slide exceeds the budget, revise by grouping, splitting, or moving details to appendix/speaker notes.

### Technical Blueprint Component Polish

Prefer:

- swimlanes over tangled node maps
- module groups over many isolated boxes
- issue-tree or dependency tree over arbitrary spokes
- colored state pills for success/risk/manual/automated
- risk callouts with clear mitigation
- source/assumption notes for technical uncertainty

Avoid:

- full-page grid at high contrast
- unweighted connector webs
- tiny mono labels everywhere
- equal-size boxes for unequal concepts
- dashboard panels that look like monitoring UI mockups unless the slide is explicitly an observability page

## Consulting-Grade Adaptation Rule

If the user says the deck should feel formal, McKinsey-like, professional, client-facing, report-like, executive-ready, or if a previous formal style outperformed the current spec, adapt toward `consulting-light` even when the subject is technical.

Adaptation pattern:

```text
technical blueprint content -> consulting slide hierarchy -> blueprint accents only where they add meaning
```

For `McKinsey x Technical Blueprint` decks, the hierarchy should feel like consulting output first, engineering blueprint second.

## Master Design Language Gate

Before implementing a serious deck, load and apply:

- `references/master-presentation-design-language.md`
- `references/master-ppt-design-rubric.md`
- `references/five-style-master-systems.md`
- `references/premium-page-archetypes.md`
- `references/component-craft-checklist.md`
- `references/spec-to-deck-visual-priority-gate.md`
- `references/production-readiness-gates.md`
- `references/anti-regression-examples.md`
- `references/component-raster-fallback.md`
- `templates/design-language-schema.json`
- `templates/spec-implementation-priority-schema.json`
- `templates/ppt-production-artifact-checklist.md`

The model must move in this order:

1. Content semantics.
2. Page architecture.
3. Visual priority and deletion rules.
4. Visual grammar.
5. Delivery implementation.

Do not choose a visual style before understanding what the page is supposed to make the audience think or do. Do not execute a detailed design spec literally when that would produce visual noise, cramped slides, weak hierarchy, or wireframe-like output.

## Content Semantics Layer

Classify source content into thesis, judgment, evidence, framework, process, contrast, risk, action, story, and definition before design.

Required extraction before layout:

- article thesis or deck purpose
- target audience
- audience action after viewing
- 5-12 candidate slide judgments
- evidence inventory
- risk/caveat inventory
- reusable terms/entities
- sections that should not be over-compressed

## Page Architecture Layer

Each slide must have one page archetype, such as executive-cover, technical-cover, claim-evidence, metric-proof, framework-map, process-lane, system-architecture, decision-matrix, risk-register, observability-dashboard, closing-standard, or social-card.

Each slide must define one_message_takeaway, audience_action, primary_anchor, supporting_units, density_label, visual_priority, editable_core, and raster_allowance.

If a page has more than one primary anchor, split it or demote one anchor.

## Style Systems

Use style systems as complete design languages, not skins:

1. `consulting-light`: boardroom, evidence-heavy, answer-first, decision-oriented.
2. `product-report`: modern product strategy/report deck with metrics, roadmap, tradeoffs, and decision asks.
3. `technical-blueprint`: precise executable engineering deck with lanes, nodes, boundaries, failure modes, and verification.
4. `consulting-blueprint-hybrid`: formal consulting hierarchy with restrained technical blueprint accents for Agent/system architecture decks.
5. `editorial-knowledge`: premium knowledge deck that turns longform writing into frameworks, contrasts, steps, mistakes, and examples.
6. `meowclaw-ip`: mature personal-IP system with recognizable motifs but formal content pages.

## Two-Lane Production Model

### Lane A: High-Fidelity Visual Reference

Use HTML/CSS or code-rendered visual references to calibrate typography, material/background systems, layout rhythm, visual hierarchy, screenshot/contact-sheet review, and user-facing design approval.

This lane may use browser-level craft, but do not pretend the screenshot is editable PPT.

### Lane B: Editable Delivery Reconstruction

Build final PPTX from a structured manifest or generation code.

Keep editable as native PPT objects:

- slide titles, subtitles, body text
- captions and source notes
- cards and callout boxes
- tables and simple charts
- flow diagrams, issue trees, timelines, matrices, and simple architecture diagrams
- meaningful connectors and labels

Allow raster or SVG layers for paper/material background, glow, grain, complex texture, photo, screenshot, illustration, or IP character art.

## Localized Component Raster Fallback

Use localized raster or image generation only when a specific bounded component expresses relationship complexity, visual metaphor, or spatial structure that native PPT primitives are likely to make confusing, ugly, or fragile.

This is a fallback for relationship complexity, not a generic fallback for style polish.

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

Before choosing raster fallback, answer:

1. Is the component's value mainly the spatial relationship, visual metaphor, or complex visual texture?
2. Would native PPT reconstruction require many fragile connectors, nested shapes, masks, or effects?
3. Would a user reasonably accept that this component is less editable if the slide title, explanatory labels, source notes, and surrounding text remain editable?
4. Have simpler editable alternatives been tried first, such as a card grid, lane diagram, grouped modules, issue tree, or split slide?

Use localized raster fallback only when 1-3 are yes, and 4 has been attempted or rejected for a clear reason.

When using it:

- crop the image to the component region, not the full slide
- keep slide title, short interpretation, source note, and page footer native/editable
- preferably overlay key labels or section tags as editable PPT text if they may need later editing
- store the prompt and image path in the project directory
- disclose the rasterized component in `verification-report.md`
- count media objects and confirm only intended components are rasterized

Slide 08 lesson: the original tangled six-practice relationship diagram was a candidate for restructuring or localized image fallback; the revised 2x3 six-practice card arrangement is a poor candidate because it is stable, clear, and editable as PPT objects. Once a complex diagram has been simplified into a clean card or matrix layout, preserve editability unless the user explicitly asks for image styling.

## Scoring And Revision Triggers

A production slide must score at least 14/18 on the master rubric, with no zero in any dimension:

1. Judgment quality.
2. Content fidelity and evidence.
3. Page composition.
4. Component craft.
5. Style system consistency.
6. Editability and delivery hygiene.

Revise before final handoff if any of these are true:

- average score below 14
- any slide has a zero
- more than 20% of slides have topic titles instead of judgment titles
- more than 15% of slides have clipped/overlapping text
- any formal deck page looks like raw wireframe/spec coverage output
- any key technical diagram has connector web or unclear ownership boundaries
- any claimed editable core is actually rasterized
- ordinary card/matrix/table content is rasterized without explicit user approval

## Visual QA Gate

Before final handoff:

1. Inspect package structure.
2. Count editable text and media objects when possible.
3. Render with QuickLook, PowerPoint, Keynote, OfficeCLI, LibreOffice, or another available route.
4. Inspect representative screenshots/contact sheets.
5. Check for blank slides, clipped text, overlapping labels, missing images, incorrect aspect ratio, private local paths, excessive connector webs, high-contrast background grids, and cramped matrices.
6. Check that any localized raster component is intentional, bounded, disclosed, and not replacing ordinary editable card/matrix/table content.
7. Revise and re-render if issues are found.
8. Write a verification report for non-trivial decks.

Final status must distinguish `Created`, `Rendered`, `Read back`, and `Final`.

## Privacy And Cloud Export Gate

Local PPTX export is the safer default for sensitive drafts, PRDs, internal metrics, automation designs, and unpublished content. Only upload/share to Feishu/Lark Slides when the user explicitly requests cloud delivery and the content is appropriate.

## Default Workflow

1. Read source and identify audience/persona.
2. Extract semantic units and evidence inventory.
3. Create storyline and lock slide-level judgments.
4. Select production style system and page archetypes.
5. Create `slide_manifest.json`.
6. Create detailed design specification.
7. Create visual priority map, deletion rules, and noise budget.
8. Create high-fidelity visual reference for key pages when polish matters.
9. Build final PPTX using hybrid editable reconstruction.
10. Use localized component raster fallback only for bounded complex relationship/visual-metaphor components that fail editable construction.
11. Apply component craft checklist and score with the master rubric.
12. Verify object counts and representative render.
13. Report editability honestly.

## Lessons From Recent Trials

- McKinsey-style specs work well when they encode hierarchy, restraint, and deletion-by-implication.
- Technical blueprint specs can underperform when executed literally because grids, nodes, connectors, labels, and tables compound into visual noise.
- Detailed coordinates are not enough. A production-grade spec must include visual priority, deletion rules, density budgets, and component craft expectations.
- For Agent/system decks, the target should often be `consulting-blueprint-hybrid`: consulting structure with technical proof components, not raw blueprint drafting.
- Localized image generation is useful for complex relationship diagrams, ecosystem maps, conceptual visuals, and material layers; it is usually wrong for already-clean card grids, matrices, tables, and metric cards because it destroys useful editability without solving a real structural problem.
