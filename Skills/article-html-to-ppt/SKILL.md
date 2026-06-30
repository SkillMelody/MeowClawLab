---
name: "article-html-to-ppt"
description: "Turn articles into formal brand-consistent decks with gated export checks."
---

# Article HTML To PPT

## Core Principle

Convert articles into speakable, professionally designed slide decks. The workflow is: normalize source, build storyboard, define a formal brand-consistent visual direction, produce preview artifacts, export to PPTX or Feishu Slides, then verify honestly.

Do not mechanically slice a long article into slides. Do not let article-specific visual metaphors fragment the deck. Content-fit design must operate inside a stable visual system so the final deck feels like a deliberate, professional product from the owner.

A visual system is more than a color palette. It includes layout grid, page rhythm, typography hierarchy, footer/source pattern, caption style, shape language, evidence labels, brand marks, and export verification language.

This skill must be honest about rights, capabilities, and verification. A deck is not final merely because files were created. If the export cannot be rendered or read back, say so and deliver the best verified artifact with clear limits.

## Default Design Goal

Default to **formal brand-consistent deck design**, unless the user explicitly asks for an experimental keynote, poster-like deck, or highly expressive editorial style.

A good default deck should feel:

- professional enough for internal leadership review, client discussion, training, or public-facing brand use
- visually consistent from first page to last
- clearly produced by the owner or brand, not by a generic AI slide generator
- content-aware without becoming visually chaotic
- restrained, readable, and repeatable

Use article-specific visual metaphors as motifs, diagrams, section markers, or accent treatments, not as a reason for every slide to change background system.

## When To Use

Use this skill when the user asks to:

- turn an article, Markdown draft, HTML article, WeChat draft, report, or review-approved manuscript into slides
- create PPT/PPTX/PowerPoint/Feishu Slides from article content
- make an HTML slide preview before exporting slides
- adapt MeowClawLab / 夜猫子弦月 content into a presentation
- preserve image prompts, captions, figure notes, visual identity, or desensitization constraints in the deck
- improve a deck because it looks stiff, generic, ugly, mismatched, not professional, or not brand-consistent

Do not use this for ordinary document editing, raw article writing, or a one-off visual image request.

## Inputs To Collect Or Infer

Prefer inferring from local context before asking. Ask only when rights, export target, audience, or brand constraints cannot be reasonably inferred.

Required:

- Source content: Markdown, HTML, Docx text, article path, pasted text, or URL content already retrieved by a suitable skill.
- Export target: `html-preview`, `pptx`, `feishu-slides`, or `both`.
- Usage boundary: private draft, internal review, public sharing, client delivery, training, or publication.

Optional:

- Audience and scenario: talk, pitch, internal briefing, public sharing, article-to-video outline.
- Duration or slide count.
- Visual system id and overrides.
- Assets: cover image, logo, screenshots, diagrams, existing PPT template.
- Sensitivity level: public, internal, private.
- Formality target: working draft, formal internal, client-facing, public keynote.

## P0 Preflight And Checkpoints

These checkpoints are mandatory for non-trivial decks and for any external article. Do not bury checkpoint failures in a successful-looking handoff.

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

Record the decision in the handoff as `Source rights: ...`.

### CHECKPOINT 2: Capability Matrix

Before export, state what the current environment can actually do:

| Capability | Check | If Missing |
| --- | --- | --- |
| HTML preview | Can write and inspect local HTML | Deliver storyboard + preview source, report limit |
| PPTX export | PptxGenJS / Marp / Pandoc or local helper available | Do not promise PPTX; offer HTML or Feishu path |
| Feishu Slides create/write | Relevant Lark/Feishu scopes available | Ask for auth or deliver local preview |
| Feishu Slides readback/screenshot | Read scope or render route available | Mark Feishu verification as creation-only |
| Image upload/use | Asset rights and upload scope available | Use placeholders/prompts with captions |

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

Each gate page must pass:

- one clear message
- stable layout grid and spacing
- consistent typography hierarchy
- consistent footer/source/brand marker pattern
- background system consistent with the rest of the deck
- accent colors mapped to meaning, not decoration
- captions distinguish facts, reconstructions, prompts, and assumptions
- visual motif supports the article without overpowering brand identity

If the user says the deck should be more formal, professional, or brand-consistent, reduce visual variation first. Do not defend expressive variation as the default.

## Workflow

### 1. Normalize Source

Extract structured content into:

- title
- subtitle or thesis
- section headings
- core claims
- emotional tone
- rhetorical pattern
- evidence and examples
- tables or frameworks
- image suggestions and captions
- risks, caveats, or internal-only details

Keep source citations or file paths when available. Do not invent historical screenshots, metrics, quotes, or examples.

### 2. Build A Storyboard

Create a storyboard before making slides.

Each storyboard frame should include:

- slide title
- speaker point
- visual job: what the visual must help the audience understand
- body bullets or diagram elements
- source section
- image prompt or asset requirement
- caption / footnote requirement
- sensitivity notes
- verification notes for facts, screenshots, and reconstructed visuals
- brand consistency notes: background mode, layout family, footer/caption pattern

Default deck shape for long articles:

1. Cover: title, subtitle, visual hook, source/usage boundary when needed.
2. Problem: why this matters now.
3. False belief: what the article argues against.
4. Evidence sequence: 2-5 slides showing the argument.
5. Framework: one reusable model or checklist.
6. Case / workflow proof: what happened in the real process.
7. Risks and boundaries: what not to overclaim.
8. Close: memorable conclusion and next action.

### 3. Derive Formal Content-Fit Visual Direction

Before choosing colors or XML layout, write a short `visual_design_brief`:

- Article type: argument, case study, tutorial, briefing, narrative essay, framework explainer, news analysis, pitch.
- Formality target: working draft, formal internal, client-facing, public keynote.
- Brand posture: MeowClawLab, pitfall guide, nightly report, client-neutral, or custom.
- Core metaphor: pressure, fracture, map, bridge, machine, notebook, courtroom, lab bench, signal, ledger, timeline, etc.
- Emotional temperature: cold judgment, warm narrative, urgent warning, calm tutorial, executive clarity, field report.
- Visual density: sparse, standard, dense.
- Evidence mode: screenshots, reconstructed diagrams, process map, comparison table, quote cards, timeline, matrix.
- Audience posture: persuade, teach, brief, review, sell, provoke, align.
- Rejected visual directions: styles that would be generic, misleading, too playful, too dark, too fragmented, or mismatched.

Then select one visual archetype from `references/visual-design-archetypes.md`, or define a task-specific archetype if none fits. Archetype selection does not override brand consistency.

### 4. Apply Brand System As Primary Design Frame

Select a brand or column visual system from `references/visual-systems.md` if present. Use it as the primary design frame:

- palette and semantic color mapping
- typography hierarchy
- title and subtitle rhythm
- recurring footer/source pattern
- logo/mark or text brand marker
- shape language
- caption and fact-boundary rules
- page grid and margins

Allowed variation:

- A deck may use one dominant background family plus one limited contrast mode.
- Use contrast mode for cover, chapter divider, or one major tension slide, not every other page.
- Use article-specific motifs as accents, diagrams, dividers, and semantic shapes.
- Keep brand markers, caption style, and typography consistent across modes.

Avoid:

- alternating dark/light backgrounds without a clear chapter logic
- every slide looking like a different visual experiment
- full brand palette dumped onto every slide
- generic blue-purple AI gradients
- decorative dashboards that do not explain the argument

The deck must pass the brand consistency test:

- Does this look like one deck from one owner?
- Is the brand signal visible beyond tiny nav text?
- Would a viewer remember who produced it?
- Are page transitions calmer than the article's emotional rhetoric?
- Are colors doing semantic work, or just decorating?

### 5. Design Slide-Specific Visual Jobs

For every slide, assign a visual job before writing XML/PPTX:

- Hook: create tension or curiosity.
- Contrast: show before/after or false belief/reality.
- Explain: make an abstract concept visible.
- Evidence: present screenshot, quote, or reconstructed diagram with caption.
- Framework: organize reusable thinking.
- Process: show sequence or workflow.
- Boundary: mark risk, caveat, or fact/source distinction.
- Close: leave a memorable takeaway.

Reuse a stable layout library. A professional deck can vary slide type without varying the entire visual system.

### 6. Generate HTML Preview First

For non-trivial decks, create an HTML preview before final export unless the user asks for direct PPTX only.

HTML preview should make these easy to inspect:

- slide order
- title hierarchy
- text overflow
- visual rhythm
- whether the visual direction fits the article
- whether the whole deck feels brand-consistent
- image slots and prompts
- captions and warnings
- public/internal boundary labels

Use responsive slide containers or print-friendly HTML. Avoid decorative complexity that cannot survive PPTX export.

### 7. Export

Choose the export method based on target and local capabilities:

- `pptx`: prefer PptxGenJS or an existing slides/PPTX helper if available.
- `feishu-slides`: use the Lark/Feishu slides skill or lark-cli route when available.
- `marp`: acceptable for Markdown-first decks, especially if the deck is text-heavy and HTML/PDF/PPTX output is enough.
- `html-preview`: deliver the preview path or published app link.

When using Feishu assets, route through the relevant Feishu/Lark skill instead of ad hoc API calls.

If a requested export is blocked, produce the strongest available intermediate artifact and make the missing capability explicit.

### 8. Verify Before Completion

At minimum:

- Open or inspect the generated HTML preview.
- Check slide count and ordering against storyboard.
- Check text overflow on desktop and mobile-ish widths when HTML is used.
- Check whether visual design matches the article's content and rhetorical tone.
- Check whether the deck feels professional and brand-consistent.
- Check captions, figure labels, and desensitization notes.
- For PPTX/Feishu Slides, render screenshots or read back XML when possible; otherwise report the verification limit.

Do not call a deck `final` if only creation succeeded but rendering/readback failed or was unavailable. Use `created`, `previewed`, or `needs visual readback` instead.

## Failure Modes And Required Responses

| Failure Mode | Trigger | Required Response |
| --- | --- | --- |
| Source rights unclear | External article, third-party images, unknown author | Ask or mark as private/internal; preserve attribution |
| Fixed brand shell | Same layout/palette ignores article meaning | Keep brand frame but add content-specific motif/diagram |
| Visual fragmentation | Backgrounds/layouts change too much | Reduce to one dominant background family and one contrast mode |
| Weak brand signal | Deck could be mistaken for generic AI output | Add consistent brand marker, footer, typography, semantic palette |
| Fake evidence | Reconstructed UI, inferred timeline, synthetic diagram | Label as reconstruction or assumption visibly |
| Scope/auth missing | Feishu/PPTX export cannot be created/read | Report exact missing capability and deliver preview/storyboard |
| Dependency missing | No pptx/marp/pandoc/helper available | Do not promise PPTX; pick available route |
| Text overflow | HTML/PPTX has clipped text or crowded slide | Reduce copy, split slide, or change layout before handoff |
| Visual mismatch | User says deck is ugly/generic/mismatched | Diagnose mismatch, revise visual brief, regenerate representative pages first |
| Platform mismatch | HTML looks good but Feishu/PPTX constraints differ | Simplify shapes/layouts and verify platform output when possible |
| Privacy leak | Tokens, raw local paths, unpublished names, account names | Redact before export and mention redaction class |

## Red-Light Blacklist

Never do these:

- Never claim reconstructed UI, inferred process, or synthetic image is a historical screenshot.
- Never call a Feishu/PPTX deck final when it was only created but not rendered or read back, unless the user explicitly accepts that limit.
- Never upload a public-redistribution deck from an external copyrighted article without confirming usage rights.
- Never use article-specific visual metaphors to justify a fragmented, inconsistent deck.
- Never hide dependency, export, or scope failures behind a successful-looking handoff.
- Never remove source attribution when the argument depends on an external article.
- Never include private local paths, tokens, account names, unpublished leads, or raw review trails in public decks.
- Never let decorative visuals overpower the article's actual argument or brand identity.

## MeowClawLab Defaults

When source content belongs to MeowClawLab / 夜猫子弦月, first produce a professional MeowClawLab deck, then adapt content motifs inside it.

Default constraint palette:

- `moon-ink #14161F`
- `lunar-slate #2A3142`
- `claw-coral #FF6B5F`
- `copper-glow #C9824B`
- `mist-white #F6F4EF`
- `terminal-green #2DBE7E`
- `warning-amber #F2B84B`

Recommended formal deck modes:

- `formal-light`: mist-white / paper background, moon-ink text, coral/copper accents. Best for professional readability.
- `formal-dark`: moon-ink background, mist-white text, restrained coral/copper accents. Best for keynote mood.
- `hybrid-formal`: one dominant mode plus a limited contrast mode for cover/dividers only.

Default for article-to-PPT unless otherwise specified: `formal-light` or `hybrid-formal` with light body pages.

Use colors semantically:

- `claw-coral`: rupture, warning, action, core tension.
- `copper-glow`: warmth, human context, narrative emphasis.
- `mist-white`: reading surface, framework diagrams, tutorial clarity.
- `terminal-green`: verified/pass state, workflow continuation.
- `warning-amber`: cost/risk/caveat.

Required recurring brand elements:

- Small text mark such as `MeowClawLab` or the user-approved brand name on content pages.
- Consistent footer source/caption pattern.
- Consistent page number or section marker when appropriate.
- Stable margins and title positions.

Required labels for current article family:

- v1/v2/v3 UI images: `基于功能演进复原的界面示意图，非历史截图`.
- Interception examples: `基于拦截逻辑复盘的示意图`.
- Internal details: redact local paths, unpublished titles, private service leads, tokens, account names, and raw review paths unless the user explicitly approves internal-only usage.

## Output Package

For a complete deck task, produce one primary deliverable plus a short handoff.

Recommended local files:

- `storyboard.md`
- `visual-design-brief.md` or `visual-system.json`
- `brand-consistency-check.md`
- `slides-preview.html`
- `deck.pptx` or Feishu Slides link
- `verification-report.md` for non-trivial or externally shared decks

Handoff should include:

- source rights and usage boundary
- export target and final link/path
- slide count
- chosen visual archetype and why it fits the article
- selected brand system and consistency decisions
- capability matrix result
- verification performed: created / rendered / read back / final
- remaining risks or manual checks

## Common Mistakes

- Long article slicing: turns paragraphs into crowded slides. Fix by writing a storyboard first.
- Brand shell lock-in: makes every article look the same. Fix by keeping a stable brand frame and using article-specific motifs inside it.
- Visual fragmentation: deep/light/random background changes make the deck feel unprofessional. Fix with one dominant background family and limited contrast mode.
- Pretty but irrelevant visuals: looks designed but does not explain the argument. Fix by assigning every slide a visual job.
- Fixed dark theme: makes decks heavy and monotonous. Fix by using formal-light body pages or dark only for cover/dividers.
- Fake evidence visuals: reconstructed images look like historical screenshots. Fix with visible figure labels.
- PPT-first editing: hard to review structure and visual rhythm. Fix with HTML preview before PPTX for non-trivial work.
- Ignoring final platform: Feishu Slides, PPTX, and HTML have different layout constraints. Choose export path early.
- Success theater: reporting a deck as done when only one export step succeeded. Fix by naming the actual verification state.

## Collaboration Rules

For one-shot conversions, prefer run/one-shot execution and write durable output files. Do not rely on a long chat history as the deck state. When delegating to another agent, pass the source path, rights boundary, capability matrix, storyboard requirements, formal brand direction, selected brand constraints, export target, and expected final deliverable.
