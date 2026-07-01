---
name: "article-html-to-ppt"
description: "Generate PPTX directly with native dynamic step-build support."
---

# Article HTML To PPT

## Core Principle

Convert articles into speakable, professionally designed slide decks. The workflow is: normalize source, build storyboard, define a formal brand-consistent visual direction, produce reviewable preview artifacts, export to the requested deck format, then verify honestly.

This skill treats **direct PPTX generation** as a first-class export path. When the environment has PptxGenJS or an equivalent local helper, generate a real `.pptx` file instead of stopping at guidance.

When the user asks for **dynamic PPT**, **dynamic presentation**, **animated PPT**, or says the exported PPT should dynamically display during presentation, default to a **native PPTX progressive-build deck**: duplicate each logical slide into multiple build steps so each click reveals more content in PowerPoint/Keynote presentation mode. Add native slide transitions when possible. HTML dynamic decks are optional companion artifacts, not the default answer for “dynamic PPT”.

Object-level PowerPoint animations inside a single slide remain experimental because they require fragile OOXML timing/animation structures or target-player automation. Do not promise object-level animation unless a prototype is verified in PowerPoint/Keynote.

A deck is not final merely because files were created. If the export cannot be rendered, opened, read back, or visually checked, say so and deliver the best verified artifact with clear limits.

## When To Use

Use this skill when the user asks to:

- turn an article, Markdown draft, HTML article, WeChat draft, report, or review-approved manuscript into slides
- create PPT/PPTX/PowerPoint/Feishu Slides from article content
- directly generate a `.pptx` file from article or HTML content
- create a dynamic PPT/PPTX that reveals content during presentation
- create native PowerPoint/Keynote-compatible step-by-step presentation behavior
- make an HTML slide preview before exporting slides
- create an optional reveal.js or web presentation companion
- adapt MeowClawLab / 夜猫子弦月 content into a presentation
- preserve image prompts, captions, figure notes, visual identity, source rights, or desensitization constraints in the deck

Do not use this for ordinary document editing, raw article writing, or a one-off visual image request.

## Inputs To Collect Or Infer

Required:

- Source content: Markdown, HTML, Docx text, article path, pasted text, or URL content already retrieved by a suitable skill.
- Export target: `pptx`, `native-dynamic-pptx`, `html-preview`, `dynamic-html`, `feishu-slides`, `object-animation-pptx-experimental`, or `multi`.
- Usage boundary: private draft, internal review, public sharing, client delivery, training, or publication.

Optional:

- Audience and scenario.
- Duration or slide count.
- Visual system id and overrides.
- Assets: cover image, logo, screenshots, diagrams, existing PPT template.
- Dynamic behavior: step-by-step reveals, section transitions, speaker notes, auto-slide timing, embedded media, or object-level animation.

## P0 Preflight And Checkpoints

### CHECKPOINT 1: Source Rights And Use Boundary

Before generating an export intended for sharing, classify the source:

- `owned`: written by the user or their team.
- `licensed`: user provided permission, template, or explicit reuse rights.
- `external-reference`: public article or third-party source used for analysis or private transformation.
- `unknown`: rights are unclear.

Rules:

- For `owned` or `licensed`, continue normally.
- For `external-reference`, produce a private/internal working deck unless the user confirms public redistribution is allowed.
- For `unknown`, ask for confirmation before uploading a public or broadly shared deck.
- Always preserve source attribution when the deck depends on a public article.
- Do not download, rehost, or imply ownership of third-party images unless rights are clear.

### CHECKPOINT 2: Export Capability Matrix

Before export, state what the current environment can actually do.

| Capability | Stable Route | Check | If Missing |
| --- | --- | --- | --- |
| Direct PPTX | PptxGenJS or equivalent helper | `node -e "require.resolve('pptxgenjs')"` or helper exists | Install only with user approval, or deliver HTML/Feishu route |
| Native dynamic PPTX | Progressive-build slides + optional native transitions | PPTX builder can duplicate slide states | Deliver static PPTX; explain limit |
| PPTX render check | LibreOffice/PowerPoint/Keynote/QuickLook/screenshot route | Can open/export/screenshot generated PPTX | Mark PPTX as created but not visually verified |
| Feishu Slides create/write | Lark/Feishu slides skill or lark-cli route | Scopes available | Ask for auth or deliver local PPTX/preview |
| Dynamic HTML companion | reveal.js/plain HTML runtime | Can generate local HTML and open/render it | Omit companion |
| Object-level animated PPTX | OOXML/PowerPoint automation support | Prototype renders in target player | Treat as experimental; do not promise |
| Image upload/use | Asset rights and upload scope available | Upload/use allowed | Use placeholders/prompts with captions |

The final handoff must distinguish:

- `Created`: artifact was generated or uploaded.
- `Rendered`: artifact was opened or rendered locally.
- `Read back`: exported platform content was inspected after creation.
- `Final`: all required checks passed, or remaining limits were accepted by the user.

### CHECKPOINT 3: Formal Brand Consistency Gate

Before batch-generating all slides, validate representative pages whenever practical:

- Cover or opening slide.
- Evidence or example slide.
- Framework / process / checklist slide.
- Closing slide if the deck is public or client-facing.

Each gate page must pass one clear message, stable grid, consistent typography, consistent footer/source/brand marker, and visible fact/reconstruction labels.

### CHECKPOINT 4: Native Dynamic PPT Gate

Use this checkpoint when the user requests dynamic PPT or exported PPT presentation motion.

Classify the dynamic request:

- `native-dynamic-pptx`: stable default. Generate a PPTX where each logical slide is expanded into multiple build steps. Each click reveals more content by advancing to the next visually similar slide. Add slide transitions when supported.
- `pptx-with-notes`: stable. Static PPTX with speaker notes and presenter-friendly structure.
- `dynamic-html-companion`: optional companion for web-native motion, not a substitute when the user asked for PPTX.
- `object-animation-pptx-experimental`: object-level animation inside one slide. Experimental only.

Rules:

- If the user says “dynamic PPT”, do not answer with only HTML.
- Prefer native progressive-build PPTX because it works across PowerPoint/Keynote without fragile object animation XML.
- Keep build-step slides visually identical except for newly revealed content.
- Add slide transitions such as fade when possible and verify transition XML exists.
- Report logical slide count and build-step slide count separately.
- If object-level animation is required, prototype 1-2 slides first and verify in the target player.

## Workflow

### 1. Normalize Source

Extract title, thesis, section headings, claims, evidence, examples, frameworks, image suggestions, caveats, and sensitivity notes. Preserve citations or file paths when useful. Do not invent screenshots, metrics, quotes, or examples.

### 2. Build A Storyboard

Create a storyboard before making slides. Each frame should include:

- slide title
- speaker point
- visual job
- body bullets or diagram elements
- source section
- caption / footnote requirement
- brand consistency notes
- export notes: PPTX layout mapping and dynamic build steps

### 3. Derive Formal Content-Fit Visual Direction

Write a short `visual_design_brief` with article type, formality target, brand posture, metaphor, emotional temperature, visual density, evidence mode, audience posture, and rejected directions. Then select a visual archetype from `references/visual-design-archetypes.md` or define one.

### 4. Apply Brand System As Primary Design Frame

Select a brand/column visual system from `references/visual-systems.md` if present. Use it for palette, typography, title rhythm, footer/source pattern, shape language, captions, and grid.

### 5. Design Slide-Specific Visual Jobs

Assign every slide a visual job: hook, contrast, explain, evidence, framework, process, boundary, or close.

### 6. Generate Preview Or Direct PPTX

For non-trivial decks, create an HTML preview before final export unless the user asks for direct PPTX only. If the user asks for direct or native-dynamic PPTX, still build a storyboard and verification report.

### 7. Export

#### 7.1 Direct PPTX Export

Use PptxGenJS or an existing local helper as the preferred direct `.pptx` route.

Minimum requirements:

- 16:9 wide layout unless user asks otherwise
- theme fonts and colors
- shared layout helpers or slide masters
- PowerPoint-safe text, shapes, tables, charts, images, and SVGs
- speaker notes when useful
- captions and source/rights labels
- no private paths in slide-visible text
- `deck.pptx` plus `pptx-build-report.json` or `verification-report.md`

#### 7.2 Native Dynamic PPTX Export

Use this when the user wants exported PPT to dynamically display during presentation.

Implementation pattern:

1. Start from the logical storyboard.
2. For each logical slide, define reveal steps.
3. Generate one PPTX slide per reveal step.
4. Keep stable coordinates, typography, background, and footer across all steps in the same logical slide.
5. Add only the newly revealed bullet, diagram part, or emphasis between steps.
6. Add native slide transitions if supported.
7. Embed speaker notes for each build step or logical slide.
8. Write `deck-dynamic-native.pptx`.
9. Report both counts: `logical slides` and `native build-step slides`.

Verification:

- inspect `.pptx` zip for expected slide count
- confirm notes count when speaker notes are generated
- confirm transition XML exists if transitions are added
- render via QuickLook/PowerPoint/Keynote/LibreOffice/screenshot route when available
- if only first-slide render is possible, say so

#### 7.3 Feishu Slides Export

Use the Lark/Feishu slides skill or lark-cli route when available. Creation success is not final; readback/screenshot requires extra scopes.

#### 7.4 Dynamic HTML Companion

Use reveal.js or custom HTML only as an optional companion format or when the user explicitly asks for a web presentation. Do not substitute it for native dynamic PPTX when the user asked for PPT.

#### 7.5 Object-Level Animated PPTX Experimental

Only attempt PowerPoint-native object animation inside a single slide if a proven helper, OOXML patcher, or PowerPoint automation route exists.

Rules:

- prototype 1-2 slides first
- render or manually inspect in the target player
- if verification fails, deliver native dynamic PPTX instead
- mark result as experimental

### 8. Verify Before Completion

At minimum:

- Check logical slide count and build-step slide count.
- Check text overflow in preview and/or exported target.
- Check whether visual design is professional and brand-consistent.
- Check captions, figure labels, and desensitization notes.
- For native dynamic PPTX, verify slide count, notes count, transition XML if added, and at least one render/screenshot when possible.
- Do not call a deck `final` if only creation succeeded but rendering/readback failed or was unavailable.

## Failure Modes And Required Responses

| Failure Mode | Trigger | Required Response |
| --- | --- | --- |
| User wanted dynamic PPT but got HTML | User asks for PPT motion/presentation mode | Generate native dynamic PPTX; HTML only as companion |
| Direct PPTX dependency missing | PptxGenJS/helper unavailable | Ask before installing; otherwise deliver preview/Feishu route |
| PPTX creation succeeds but cannot render | No renderer/checker available | Mark as created but not visually verified |
| Native build-step deck too long | Too many reveal steps | Group reveals, reduce bullets, or use section-level builds |
| Object animation requested | User needs same-slide PowerPoint object animation | Prototype; mark experimental; do not promise |
| Source rights unclear | External article or third-party images | Ask or mark as private/internal; preserve attribution |
| Visual fragmentation | Backgrounds/layouts change too much | Reduce to one dominant background family and one contrast mode |
| Fake evidence | Reconstructed UI or synthetic diagram | Label as reconstruction or assumption visibly |
| Privacy leak | Tokens, raw local paths, unpublished names | Redact before export and mention redaction class |

## Red-Light Blacklist

Never do these:

- Never answer a request for dynamic PPT with only HTML.
- Never claim object-level PowerPoint animations are supported unless a verified prototype worked in the target player.
- Never call a generated PPTX final when it was only created but not rendered or inspected.
- Never claim reconstructed UI, inferred process, or synthetic image is a historical screenshot.
- Never upload a public deck from an external copyrighted article without confirming usage rights.
- Never include private local paths, tokens, account names, unpublished leads, or raw review trails in public decks.

## Output Package

For a complete deck task, produce one primary deliverable plus a short handoff.

Recommended files:

- `storyboard.md`
- `visual-design-brief.md` or `visual-system.json`
- `slides-preview.html` when useful
- `deck.pptx` for static PPTX
- `deck-dynamic-native.pptx` for native dynamic PPTX
- `dynamic-deck.html` only as companion or web export
- Feishu Slides link when requested
- `pptx-build-report.json` or `native-dynamic-pptx-report.json`
- `verification-report.md`

Handoff should include source rights, usage boundary, export target, logical slide count, build-step slide count if dynamic, chosen visual system, capability matrix, verification performed, and remaining manual checks.

## Collaboration Rules

For one-shot conversions, prefer run/one-shot execution and write durable output files. Do not rely on long chat history as deck state. When delegating, pass the source path, rights boundary, capability matrix, storyboard requirements, brand direction, export target, dynamic PPT requirements, and expected final deliverable.
