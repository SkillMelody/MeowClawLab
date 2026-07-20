## Public Name: <br>
MeowClaw 夜猫 PPT 工坊 / MeowClaw PPTSmith <br>

## ClawHub / Installed Slug: <br>
article-html-to-ppt <br>

## Brand Alias(es): <br>
meowclaw-pptsmith, meowclaw-decksmith <br>

## Description: <br>
MeowClaw PPTSmith converts articles, Markdown drafts, HTML pages, WeChat drafts, PRDs, automation plans, knowledge posts, and review-approved manuscripts into low-rework, persona-fit slide decks with direct PPTX, native dynamic PPTX, and Feishu Slides export routing. <br>

Version 2.0.0 is engineering-complete and **Standard production-ready on the verified acceptance environment** for commercial/non-commercial use. `python_pptx` is the canonical production Builder; PptxGenJS is portability evidence. **Premium is not final on this host** because no verified PowerPoint/LibreOffice renderer is available. <br>

## Owner
SkillMelody <br>

### License/Terms of Use: <br>
MIT-0 <br>

## Use Case: <br>
Product owners, product reporters, Agent engineers, automation developers, self-media authors, knowledge bloggers, editors, educators, and content teams who need to turn source material into structured presentation decks without losing source boundaries, audience fit, editability, or verification discipline. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: External articles or third-party images may not be licensed for public redistribution. <br>
Mitigation: The skill requires source-rights classification and preserves attribution before export. <br>

Risk: Slide creation can be mistaken for final delivery even when platform readback or rendering was not verified. <br>
Mitigation: The skill separates Created, Rendered, Read back, and Final states in the handoff. <br>

Risk: Users may ask for dynamic PPT and receive only an HTML presentation. <br>
Mitigation: The skill now defaults dynamic PPT requests to native PPTX progressive-build slides, with HTML only as an optional companion. <br>

Risk: Article-specific visual metaphors can fragment a deck and weaken brand trust. <br>
Mitigation: The skill defaults to formal brand-consistent design and uses motifs only inside a stable visual system. <br>

Risk: A single consulting-style template may not fit product reporting, technical architecture, and knowledge creator decks equally well. <br>
Mitigation: The skill now selects persona-specific deck defaults for product owners/reporters, Agent engineers/automation developers, and self-media authors/knowledge bloggers. <br>

Risk: Premium profile can be overused for ordinary decks, increasing cost and blocking delivery on missing renderers. <br>
Mitigation: The skill resolves fast/standard/premium from explicit request, audience risk, brand demand, delivery value, and diagram complexity; Premium is reserved for public, high-value, template, complex, or explicitly full-validation work. <br>

Risk: Feishu/Lark Slides export sends source content, generated slide text, and related metadata to a cloud service. <br>
Mitigation: The skill defaults sensitive work to local PPTX output and requires explicit user intent plus a pre-upload summary before Feishu/Lark cloud delivery. <br>

## Reference(s): <br>
- [Visual Design Archetypes](references/visual-design-archetypes.md) <br>
- [Visual Systems Reference](references/visual-systems.md) <br>
- [Export Pipelines Reference](references/export-pipelines.md) <br>
- [v1.5 / v2.0 Closeout Checklist](docs/v1.5-v2.0-closeout-checklist.md) <br>
- [v2.0 Acceptance Report](docs/v2.0-acceptance-report.md) <br>
- [Storyboard Template](templates/storyboard-template.md) <br>
- [Content Lock Template](templates/content-lock-template.md) <br>
- [Slide Manifest Template](templates/slide-manifest-template.json) <br>
- [Visual QA Gate Template](templates/visual-qa-gate-template.json) <br>

## Skill Output: <br>
**Output Type(s):** [Storyboard, HTML preview, static PPTX, native dynamic PPTX, Feishu Slides, Verification report] <br>
**Output Format:** [Markdown plans, HTML previews, .pptx files, Feishu Slides links, structured handoff] <br>
**Output Parameters:** [source rights, export target, dynamic mode, audience/persona, brand system, verification state] <br>
**Other Properties Related to Output:** [Supports low-rework persona-fit decks, consulting-style baselines, technical blueprint decks, editorial knowledge decks, SVG/HTML preview policy, direct PPTX export, and progressive-build dynamic PPTX for MeowClawLab-style work] <br>

## Evaluation Metrics Used: <br>
- Security: Checks that private paths, account names, tokens, and raw review trails are not included in public decks. <br>
- Rights discipline: Checks whether external sources and reconstructed visuals are labeled correctly. <br>
- Brand consistency: Checks whether the deck feels like one professional product from one owner. <br>
- Persona fit: Checks whether product/reporting, technical/automation, or knowledge-creator decks use the right structure, proof style, and visual language. <br>
- Readability: Checks title hierarchy, slide density, and text overflow risks. <br>
- Dynamic PPT behavior: Checks logical slide count, build-step slide count, transitions, and rendered preview when possible. <br>
- Verification honesty: Checks whether the final handoff clearly distinguishes generated, rendered, read-back, and final states. <br>

## Skill Version(s): <br>
2.0.0 <br>

Readiness scope: Standard production on the verified acceptance environment. Premium final readiness remains externally blocked pending real renderer, render/readback, zero-error QA, rubric, and fallback evidence. <br>

## Ethical Considerations: <br>
This skill should not be used to repackage copyrighted third-party articles or images as owned public content without permission. It is designed to make transformation boundaries explicit and to prevent synthetic or reconstructed visuals from being presented as factual historical screenshots. <br>
