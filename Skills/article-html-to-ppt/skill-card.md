## Description: <br>
Convert articles, Markdown drafts, HTML pages, WeChat drafts, and review-approved manuscripts into formal, brand-consistent slide decks with direct PPTX, native dynamic PPTX, and Feishu Slides export routing. <br>

This skill is ready for commercial/non-commercial use. <br>

## Owner
SkillMelody <br>

### License/Terms of Use: <br>
MIT-0 <br>

## Use Case: <br>
Editors, operators, educators, and content teams who need to turn long-form written material into structured presentation decks without losing source boundaries, brand consistency, or verification discipline. <br>

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

## Reference(s): <br>
- [Visual Design Archetypes](references/visual-design-archetypes.md) <br>
- [Visual Systems Reference](references/visual-systems.md) <br>
- [Export Pipelines Reference](references/export-pipelines.md) <br>
- [Storyboard Template](templates/storyboard-template.md) <br>
- [Content Lock Template](templates/content-lock-template.md) <br>
- [Slide Manifest Template](templates/slide-manifest-template.json) <br>
- [Visual QA Gate Template](templates/visual-qa-gate-template.json) <br>

## Skill Output: <br>
**Output Type(s):** [Storyboard, HTML preview, static PPTX, native dynamic PPTX, Feishu Slides, Verification report] <br>
**Output Format:** [Markdown plans, HTML previews, .pptx files, Feishu Slides links, structured handoff] <br>
**Output Parameters:** [source rights, export target, dynamic mode, audience, brand system, verification state] <br>
**Other Properties Related to Output:** [Supports formal-light and hybrid-formal deck modes, direct PPTX export, and progressive-build dynamic PPTX for MeowClawLab-style work] <br>

## Evaluation Metrics Used: <br>
- Security: Checks that private paths, account names, tokens, and raw review trails are not included in public decks. <br>
- Rights discipline: Checks whether external sources and reconstructed visuals are labeled correctly. <br>
- Brand consistency: Checks whether the deck feels like one professional product from one owner. <br>
- Readability: Checks title hierarchy, slide density, and text overflow risks. <br>
- Dynamic PPT behavior: Checks logical slide count, build-step slide count, transitions, and rendered preview when possible. <br>
- Verification honesty: Checks whether the final handoff clearly distinguishes generated, rendered, read-back, and final states. <br>

## Skill Version(s): <br>
1.0.3 <br>

## Ethical Considerations: <br>
This skill should not be used to repackage copyrighted third-party articles or images as owned public content without permission. It is designed to make transformation boundaries explicit and to prevent synthetic or reconstructed visuals from being presented as factual historical screenshots. <br>
