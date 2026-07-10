---
name: "article-html-to-ppt"
description: "PPT skill for low-rework persona-fit decks"
---

# Proposal: Upgrade `article-html-to-ppt` For Low-Rework Persona-Fit PPTs

## Target Skill

`article-html-to-ppt`

## Product Goal

The skill should help users produce PPT decks that require as little second-pass editing as practical. The default standard is not flashy presentation art. The default standard is:

- logically clear
- simple but not empty
- appropriate to the user's role and delivery context
- editable where practical
- visually calm and consistent
- verified before handoff

The skill should support consulting-style decks, but it should not force every user into the same McKinsey template. It should identify the likely audience and produce decks whose structure, density, visual language, and proof style fit that audience.

Primary audiences:

1. Product owners / product reporters.
2. Agent engineers / automation developers.
3. Self-media authors / knowledge bloggers.

## Why Update

Recent PPT skill research showed that our current skill already has a good foundation: direct PPTX generation, content lock, manifests, and honest verification. The missing upgrade is to make the decision framework explicit and to bias every route toward low-rework, editable, verified decks.

Useful influences:

- EditableImage2PPTSkill: reference images and screenshots should be rebuilt as editable text/shapes/charts where practical, not dumped as full-page screenshots.
- PPT Master: use an intermediate visual blueprint/spec layer, such as SVG, JSON, HTML, or manifest, so a deck can be previewed, debugged, and converted into PPTX objects.
- OfficeCLI / QuickLook style validation: generated files are not finished until rendered/read back or otherwise verified.
- CyberPPT: high-value decks need quality gates around evidence, story, density, editability, overflow, and final handoff.
- Design spec POC: model-generated images do not reliably return real layer sidecars; the stable path is `design_spec.json -> PPTX/PNG render -> visual QA -> spec correction -> export`.

## Proposed Additions To `SKILL.md`

Add the following sections after the current `Quality Contract` or before `Workflow`.

---

## Low-Rework PPT Contract

Optimize for decks that users can present or lightly edit, not decks that only look good in a screenshot.

Default priorities:

1. Clear story and slide intent.
2. Persona-fit structure and style.
3. Editable core text, shapes, tables, and simple charts.
4. Consistent layout grid, spacing, typography, footer, section labels, and page rhythm.
5. Conservative visual system with one accent color, neutral support colors, and no visual noise.
6. Render/readback verification before claiming final status.
7. Honest limitations when some elements remain raster images.

A deck does not need to be highly ornate. It must feel deliberate, legible, and structurally polished.

## Persona Selection

Before choosing a route or visual style, identify the primary user persona and presentation context.

If the user states a persona, use it. If not, infer from source material and goal:

| Persona | Common Inputs | Typical Goal | Default Style |
| --- | --- | --- | --- |
| `product-owner` | PRD, roadmap, feature analysis, metrics, business review, stakeholder update | align decisions, secure resources, report progress | business-consulting, structured, metric-aware |
| `agent-engineer` | architecture notes, automation workflow, tool chain, runbook, technical proposal | explain system design, implementation path, reliability, ROI | technical blueprint, flow-first, precise |
| `knowledge-creator` | article, newsletter, course notes, research synthesis, IP content | explain ideas, teach, publish, attract audience | editorial knowledge deck, visually memorable but clean |
| `consulting-general` | strategy, market, operations, analysis, client-facing deck | persuade with structured reasoning | restrained McKinsey-like deck |

If multiple personas apply, choose the persona whose audience will judge the deck. Example: an Agent engineering automation proposal for executives should use `product-owner` story framing plus selected `agent-engineer` architecture slides.

## Persona-Specific Deck Defaults

### Product Owners / Product Reporters

Use when the deck is for product负责人、产品汇报、业务复盘、路线图、版本规划、增长/留存/转化分析、资源申请、项目阶段汇报。

What this audience needs:

- Fast executive understanding: what changed, why it matters, what decision is needed.
- Clear product logic: user problem -> opportunity -> solution -> impact -> next step.
- Evidence from metrics, user feedback, market signals, milestones, and risks.
- A deck that can be reused in meetings with leaders, cross-functional teams, and stakeholders.

Recommended structure:

1. Executive summary: one-slide answer and decision request.
2. Context and problem: user/business pain, current baseline.
3. Insight: key finding or opportunity.
4. Proposal: product direction, feature package, or roadmap.
5. Impact model: metrics, funnel, adoption, revenue, efficiency, or qualitative value.
6. Execution plan: milestones, owners, dependencies.
7. Risks and tradeoffs: what could fail and mitigation.
8. Ask / decision: required resources, approval, or next step.

Visual style:

- Consulting-style white/light background, dark text, one confident accent color.
- Strong title hierarchy and executive takeaway titles.
- Use roadmaps, funnels, metric cards, 2x2 prioritization, before/after flows, simple dashboards, risk matrices.
- Keep slides dense enough for business review, but not wall-of-text.
- Make charts and tables editable whenever practical.

Quality gates:

- Every major claim should connect to a metric, user signal, source, or clearly labeled assumption.
- The deck must make the decision/ask obvious.
- Roadmap and plan slides must be scannable within 20 seconds.
- Avoid vague product language such as “提升体验” without mechanism or measure.

### Agent Engineers / Automation Developers

Use when the deck is for Agent工程师、自动化开发者、OpenClaw/Codex/工作流开发、系统设计、工具链说明、部署方案、技术评审、自动化 ROI 说明。

What this audience needs:

- System clarity: components, inputs, outputs, tools, triggers, states, failure modes.
- Implementation credibility: what runs where, what is automated, what is manual, what is risky.
- Operational view: observability, retries, permissions, data flow, handoff, rollback.
- A bridge between technical details and business value.

Recommended structure:

1. Problem / automation target: current workflow pain and desired outcome.
2. System overview: agents, tools, data sources, execution environment.
3. Workflow diagram: trigger -> planning -> execution -> verification -> handoff.
4. Architecture / integration: APIs, local files, queues, cron, sessions, storage, permissions.
5. Reliability model: failure modes, retries, logs, alerts, human approval points.
6. Implementation plan: phases, milestones, test plan.
7. ROI / impact: time saved, quality gain, risk reduction, cost implications.
8. Appendix: technical details, schemas, prompts, runbooks.

Visual style:

- Technical blueprint style: clean grid, neutral background, monospace labels only where useful.
- Use system diagrams, swimlanes, state machines, sequence flows, dependency maps, API callouts, config tables.
- SVG is especially useful for flow diagrams, architecture maps, icons, connector lines, and state machines.
- HTML/CSS preview is useful for dense technical dashboards, workflow boards, or runbook-style pages before PPT export.
- Avoid marketing-like hero slides; precision beats decoration.

Quality gates:

- Diagram labels must be readable and not overlap.
- Every automation step should identify owner: agent, script, API, human, cron, or external service.
- Security/privacy/permission boundaries must be visible when relevant.
- Do not hide uncertainty: mark assumptions, manual steps, and unimplemented pieces.

### Self-Media Authors / Knowledge Bloggers

Use when the deck is for 自媒体作者、知识博主、课程内容、公众号/知乎/小红书内容、选题拆解、知识卡片、内容产品、IP 风格展示。

What this audience needs:

- A memorable teaching arc: hook -> concept -> example -> takeaway -> shareable conclusion.
- Strong information design, but lighter than business consulting decks.
- Visual identity and content rhythm that can become article images, video frames, course slides, or social cards.
- Clear enough for readers who are not in a meeting and may skim quickly.

Recommended structure:

1. Hook / core question: why this topic matters now.
2. Big idea: one clean thesis.
3. Framework: 3-5 part mental model.
4. Examples / cases: concrete before/after, screenshots, workflows, or comparisons.
5. Practical steps: checklist, method, prompt, workflow, or template.
6. Common mistakes: what not to do.
7. Summary: memorable sentence and next action.
8. Optional social snippets: slide/card variants for publishing.

Visual style:

- Editorial knowledge style: clean, warm, branded, more expressive than product decks but still controlled.
- Use title cards, framework diagrams, quote/callout blocks, step cards, comparison grids, annotated screenshots, knowledge cards.
- Allow tasteful brand/IP accents: small character mark, column color, signature footer, recurring motif.
- Avoid over-designed poster pages that make text hard to edit or reuse.
- SVG can provide simple motifs, icons, dividers, badges, and framework diagrams.
- HTML preview can help produce article-like longform slides or social-card variants, but final PPT should preserve editable text when practical.

Quality gates:

- Each slide should teach one idea or support one content beat.
- The deck should be easy to repurpose into article images or short video frames.
- Avoid generic AI buzzword slides; include examples, workflows, or original framing.
- Maintain brand consistency without burying the knowledge content.

## Consulting-Style Visual Baseline

Use this baseline for McKinsey-style, strategy, business, report, or client-facing decks.

- Slide title states the takeaway, not just the topic.
- One primary message per slide.
- Use restrained color: dark text, light background, one accent, occasional muted support colors.
- Use a strong grid: title band, body grid, optional footer/source line.
- Prefer tables, issue trees, 2x2 matrices, process flows, waterfalls, bar/line charts, and comparison cards over decorative graphics.
- Use whitespace intentionally; dense does not mean cramped.
- Avoid gradients, glows, excessive shadows, stock-photo hero pages, and decorative icons unless they carry meaning.
- Use small, consistent labels and source notes.
- Keep text within boxes; no clipped text, tiny labels, or overlapping legends.

## Privacy And Cloud Export Gate

Local PPTX export is the safer default for sensitive drafts, PRDs, internal metrics, automation designs, and unpublished content.

Feishu/Lark Slides export sends source content, generated slide text, and relevant metadata to the Feishu/Lark cloud environment. Only use Feishu/Lark upload or sharing when the user explicitly asks for cloud delivery and the content is appropriate for that service.

Before any Feishu/Lark upload:

1. Summarize what content and metadata will leave the local environment.
2. Confirm the intended destination or sharing boundary.
3. Prefer local PPTX output if the user has not clearly requested cloud delivery.
4. Do not silently upload sensitive drafts, internal PRDs, metrics, automation designs, or unpublished content.

## Route Selection

Classify the user's request into one primary route:

| Route | Use When | Primary Output | Key Risk |
| --- | --- | --- | --- |
| `article-to-deck` | Source is an article, Markdown draft, report, WeChat post, or structured text | Storyboard + editable PPTX / dynamic PPTX / Feishu Slides | weak storyline or unverifiable claims |
| `design-spec-to-deck` | User provides a visual spec, brand spec, layout schema, or asks for a template/system | `design_spec.json` / `theme.json` + PPTX + render report | text overlap, unstable bbox, over-designed template |
| `image-to-editable-rebuild` | User provides slide screenshots, design images, image-only PPT pages, or PDF page images and wants editable PPT | editable PPTX rebuilt from text/shapes/charts/images | flattening into screenshots or overclaiming editability |
| `deck-qa-repair` | User has an existing PPTX that needs verification, repair, visual QA, readback, or polish | repair report + patched PPTX | missing render/readback or hidden overflow |
| `consulting-grade-deck` | Client-facing, strategy, McKinsey-style, high-stakes, paid, or public deck | gated PPTX + manifest + verification | skipping evidence/story/density gates |

If multiple routes apply, choose the route that controls the hardest failure mode. Example: a screenshot of a consulting-style deck that must become editable should use `image-to-editable-rebuild` plus selected `consulting-grade-deck` gates.

## Spec / SVG / HTML Rendering Policy

When a deck is based on a desired look, a visual reference, or a generated UI/slide image, prefer an explicit intermediate spec over relying on a raster image.

Stable path:

```text
intent / source -> persona + visual_design_brief -> design_spec.json or slide_manifest.json -> PPTX/PNG render -> visual QA -> spec correction -> final PPTX
```

Use the simplest code-backed visual route that produces reliable output:

- Use native PPT objects for standard text, shapes, tables, diagrams, and simple charts.
- Use SVG as a blueprint or asset when the effect is simple, geometric, and scalable: issue trees, icons, line diagrams, badges, dividers, simple decorative marks.
- Use HTML/CSS as a preview or rendering surface when it helps test layout, typography, tables, dashboards, longform editorial pages, or dense technical diagrams before rebuilding/exporting to PPTX.
- Do not use HTML screenshots as the final deck unless the user accepts low editability.
- If HTML/SVG is used for style exploration, keep the authoritative deck model in `design_spec.json`, `slide_manifest.json`, or PPTX object generation code.
- If a generated visual is needed, treat it as a reference image, not as the authoritative layer model.

Do not assume image generation can return true PPT layers, bbox, z-index, font, or asset sidecars.

## Image-To-Editable Rebuild Contract

Use when the user asks to turn slide images, design screenshots, image-only PDFs, or flattened PPT pages into editable PowerPoint.

Default strategy:

- Do not use a full-page screenshot background unless the user explicitly accepts a low-editability deck.
- Rebuild core text as editable text boxes.
- Rebuild simple cards, tables, diagrams, process flows, callouts, dividers, and chart shapes as native PPT objects.
- Keep complex illustrations, photos, watercolor figures, portraits, and hard-to-segment art as separate movable image layers.
- For charts, rebuild simple bars/lines/labels as editable shapes when data can be inferred safely; label inferred data as reconstructed.
- For consulting-style screenshots, rebuild layout grid, title hierarchy, section numbers, cards, tables, and axes natively.
- Maintain a quality report with object counts, text counts, media counts, and failures.

Honest reporting language:

- `Editable rebuild`: core text/layout rebuilt as editable PPT objects; complex art remains image layers.
- `Partially editable`: some visual elements remain images due to complexity or rights/segmentation limits.
- `Screenshot deck`: full-slide images only; use only when requested or accepted.

## Asset Decomposition Optional Path

For complex source images, especially polished slide designs with embedded assets, a future or advanced route may use asset decomposition before PPTX export.

Suggested pipeline:

```text
source image -> model proposes layers -> user/model confirms regions -> segmentation / cutout -> assets.json + layout.json -> PPTX export -> render comparison -> repair loop
```

Use this only when the user specifically needs high-fidelity editable reconstruction and the environment has suitable segmentation/cutout tools. Otherwise, use a pragmatic editable rebuild with complex assets preserved as image layers.

## Office / Render QA Gate

A PPTX is not final just because it exists. Before final handoff, run the strongest available verification route:

1. Inspect package structure: expected slide count, media files, notes, and transition XML if dynamic.
2. Count editable text and media objects when possible.
3. Render with QuickLook, LibreOffice, PowerPoint, Keynote, OfficeCLI, or another available route.
4. Inspect at least representative screenshots: cover, dense content, diagram/table/chart slide, and closing slide.
5. Check for blank slides, clipped text, overlapping labels, missing images, incorrect aspect ratio, and private local paths in visible text.
6. Revise the spec or PPT generation code and re-render if issues are found.
7. Write a verification report for non-trivial decks.

Final status must distinguish:

- `Created`: PPTX/file was generated.
- `Rendered`: visual render or screenshot was produced.
- `Read back`: slide contents or platform contents were inspected after export.
- `Final`: required checks passed or remaining limits were explicitly accepted.

## Consulting-Grade Quality Gates

Use these gates for high-value, strategy, McKinsey-style, client-facing, or paid deliverables.

- Evidence gate: every important claim traces to source, calculation, or clearly labeled reconstruction.
- Story gate: the deck has a narrative arc, not a pile of slides.
- Density gate: each slide carries one primary message and does not become a poster of tiny text.
- Editability gate: core text, diagrams, tables, and simple charts are editable where practical.
- Visual gate: grid, typography, spacing, footer, section labels, and captions are consistent.
- Persona-fit gate: structure, proof style, and visual language match the primary user audience.
- Overflow gate: rendered output shows no clipped text or incoherent overlap.
- Handoff gate: exactly one main deliverable path/link is reported, with verification status and known limits.

Do not force full consulting-grade ceremony on quick drafts. Apply the gates proportionally to risk and user intent.

## Route-Specific Deliverables

For non-trivial PPT work, create a durable work directory. Recommended files by route:

`article-to-deck`:

- `storyboard.md`
- `content_lock.md`
- `slide_manifest.json`
- `deck.pptx`
- `verification_report.json` or `verification-report.md`

`design-spec-to-deck`:

- `visual_design_brief.md`
- `theme.json`
- `design_spec.json` or `slide_manifest.json`
- `deck.pptx`
- rendered preview image(s)
- `verification_report.json`

`image-to-editable-rebuild`:

- `source_manifest.json`
- `assets.json` when assets are extracted
- `layout.json` when layout is modeled
- `deck-editable-rebuild.pptx`
- `quality_report.json`
- preview/contact sheet when useful

`deck-qa-repair`:

- `qa_report.md`
- rendered screenshots
- `deck-repaired.pptx` if changes are made

`consulting-grade-deck`:

- content lock
- manifest
- verification report
- final handoff summary

## Default Recommendation For Future PPT Work

When the user asks for a new PPT from content, start with `article-to-deck` plus standard QA.

When the user provides a visual design/spec/template, use `design-spec-to-deck`.

When the user provides images and asks for editable PPT, use `image-to-editable-rebuild`.

When the user asks for McKinsey-style or consulting-style PPT, use `consulting-grade-deck` gates proportionally, but keep the visual style restrained and editable.

When the user is a product owner or product reporter, default to a business/product report deck with executive summary, decision ask, metrics, roadmap, risks, and next steps.

When the user is an agent engineer or automation developer, default to a technical blueprint deck with workflow, architecture, failure modes, implementation plan, and ROI.

When the user is a self-media author or knowledge blogger, default to an editorial knowledge deck with hook, framework, examples, practical steps, and reusable social/content cards.

When the user asks “which PPT skill/tool should we use,” answer in terms of persona, delivery route, and failure mode, not a generic leaderboard.

---

## Optional Reference File To Add

Create `references/ppt-skill-synthesis.md` for examples and deeper notes. Keep `SKILL.md` concise; load the reference only when the user asks for route selection, image-to-editable rebuilds, consulting-grade PPT QA, or persona-specific deck defaults.

Suggested reference contents:

- route examples from recent work
- persona-specific slide templates
- language for editability labels
- sample `quality_report.json` fields
- sample `design_spec.json` fields
- quick comparison of EditableImage2PPTSkill, PPT Master, OfficeCLI, and CyberPPT as workflow influences
- examples of when to use native PPT, SVG, HTML preview, or raster images

## Acceptance Criteria

The updated skill should enable a future agent to:

1. Choose the correct PPT workflow route before implementation.
2. Identify or infer the primary PPT user persona.
3. Produce decks optimized for minimal user rework.
4. Produce persona-fit decks for product owners/reporters, agent engineers/automation developers, and self-media authors/knowledge bloggers.
5. Avoid flattening editable rebuilds into screenshots.
6. Use design specs/manifests as the stable intermediate layer when appropriate.
7. Use SVG/HTML/code-rendered previews pragmatically without sacrificing editability.
8. Verify PPTX artifacts with render/readback checks before claiming final status.
9. Apply consulting-grade gates proportionally for high-stakes decks.
10. Report final deliverables with honest `Created / Rendered / Read back / Final` status.

## Proposed Follow-Up Test Prompts

After applying the proposal, test with:

1. “我是产品负责人，把这个 PRD 和数据做成给老板汇报的 PPT。”
2. “我是 Agent 工程师，把这个 OpenClaw 自动化方案做成技术评审 PPT。”
3. “我是知识博主，把这篇公众号文章做成适合课程/小红书切片的 PPT。”
4. “把这 10 张咨询风 PPT 设计图转成可编辑 PPT。”
5. “做一套麦肯锡风格但不要过度设计的业务汇报 PPT。”
