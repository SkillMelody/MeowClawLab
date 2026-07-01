# article-html-to-ppt

Turn articles, Markdown drafts, HTML pages, WeChat drafts, and review-approved manuscripts into formal, brand-consistent slide decks.

This skill is designed for article-to-presentation workflows where the output must be more than a quick template conversion. It helps an agent derive a storyboard, choose a content-fit but brand-consistent visual direction, generate editable PPTX files when possible, create native dynamic PPTX decks for presentation mode, upload to Feishu Slides when requested, and report verification status honestly.

## When To Use

Use this skill when you need to:

- Convert long-form writing into a slide deck.
- Turn a WeChat article, Markdown draft, HTML article, or report into a presentation.
- Generate a local `.pptx` file that can be opened in PowerPoint, Keynote, LibreOffice Impress, or imported into Google Slides.
- Generate a dynamic PPTX that reveals content step by step during presentation.
- Create or upload a Feishu Slides deck for online collaboration and sharing.
- Preserve source-rights boundaries and attribution.
- Keep a deck professional, readable, and brand-consistent.
- Distinguish generated, rendered, read-back, and final delivery states.

## How To Use

Give the agent the source article and the desired export target:

```text
Use article-html-to-ppt to turn this article into an editable PPTX:
https://example.com/article
Audience: internal product review
Style: formal, readable, MeowClawLab
Slides: around 8-12
```

For native dynamic PPTX:

```text
Use article-html-to-ppt to create a dynamic PPTX.
The exported PPT should reveal bullets step by step during presentation.
Also include speaker notes and a verification report.
```

For Feishu Slides:

```text
Use article-html-to-ppt to turn this article into Feishu Slides
and send me the shareable Feishu Slides link.
```

## Export Behavior

The skill chooses the export route from the user's wording and available capabilities.

### Generates a PPTX file

The skill should generate a local PPTX file when the user asks for:

- `PPT`, `PPTX`, `PowerPoint`, `Keynote`, or an editable deck file
- direct export
- a file that can be sent, archived, opened locally, or imported elsewhere
- dynamic PPT / animated PPT that must work in presentation mode
- both a local deck and a cloud upload

Typical outputs:

- `deck.pptx` for a static editable deck
- `deck-dynamic-native.pptx` for a native dynamic deck
- `pptx-build-report.json` or `native-dynamic-pptx-report.json`
- `verification-report.md`

### Generates a native dynamic PPTX

When the user asks for dynamic PPT, the default is **native dynamic PPTX**, not HTML.

The stable implementation is progressive-build slides:

- one logical slide may become multiple physical PPTX slides
- each physical slide reveals the next bullet, diagram part, or emphasis
- PowerPoint/Keynote presentation mode advances through these build steps
- optional native fade transitions make the reveal feel smoother

The handoff should report both:

- logical slide count
- native build-step slide count

Example: a 10-slide logical deck may become a 30-slide dynamic PPTX if each logical slide has 3 reveal steps.

### Uploads or creates Feishu Slides

The skill should create or upload to Feishu Slides when the user asks for:

- `Feishu Slides`, `飞书幻灯片`, `Lark Slides`, or an online slide deck
- a shareable cloud link
- collaborative editing in Feishu
- direct upload to a specific Feishu location
- final delivery as a Feishu document rather than a local file

Feishu delivery depends on the current environment's Feishu/Lark authorization and API capability. Creation/upload is not the same as final verification: when possible, the agent should read back or screenshot the Feishu Slides result before calling it final.

### Generates both PPTX and Feishu Slides

The skill should deliver both when the user asks for both an editable file and Feishu upload, or when a local PPTX is needed as the source artifact before cloud delivery.

In that case the handoff should include:

- local PPTX path or attached file
- Feishu Slides link
- which artifact was rendered or read back
- any remaining manual checks

### Generates HTML

HTML is useful for review previews and web-native presentations, but it is not a replacement for dynamic PPTX when the user asks for a PPT.

Typical HTML outputs:

- `slides-preview.html` for design/content review
- `dynamic-deck.html` only when the user asks for a web presentation or when HTML is a companion artifact

## Core Safeguards

- Source rights are classified before export.
- External articles and reconstructed visuals are not presented as owned evidence.
- Visual design is derived from article content, but constrained by the brand system.
- Formal brand consistency is the default for publishable or client-facing decks.
- Platform capability gaps are reported instead of hidden.
- Dynamic PPT requests are answered with native PPTX progressive-build decks unless the user explicitly asks for web-only output.
- A handoff must separate `Created`, `Rendered`, `Read back`, and `Final`.

## Files

- [`SKILL.md`](./SKILL.md) - the actual OpenClaw skill document.
- [`skill-card.md`](./skill-card.md) - public-facing skill card metadata.
- [`references/export-pipelines.md`](./references/export-pipelines.md) - export routing for PPTX, dynamic PPTX, Feishu Slides, and HTML.
- [`references/visual-design-archetypes.md`](./references/visual-design-archetypes.md) - visual direction archetypes.
- [`references/visual-systems.md`](./references/visual-systems.md) - reusable visual system constraints.
- [`templates/storyboard-template.md`](./templates/storyboard-template.md) - storyboard and verification template.

## Publishing Note

This skill is intended to be reusable and GitHub-friendly. It should not contain local secrets, user-specific credentials, private paths, raw chat logs, or platform tokens.
