# article-html-to-ppt

Turn articles, Markdown drafts, HTML pages, WeChat drafts, and review-approved manuscripts into formal, brand-consistent slide decks.

This skill is designed for article-to-presentation workflows where the output must be more than a quick template conversion. It helps an agent derive a storyboard, choose a content-fit but brand-consistent visual direction, export to HTML/PPTX/Feishu Slides when available, and report verification status honestly.

## When To Use

Use this skill when you need to:

- Convert long-form writing into a slide deck.
- Turn a WeChat article, Markdown draft, or HTML article into a presentation.
- Create a Feishu Slides draft from article content.
- Preserve source-rights boundaries and attribution.
- Keep a deck professional, readable, and brand-consistent.
- Distinguish generated, rendered, read-back, and final delivery states.

## Core Safeguards

- Source rights are classified before export.
- External articles and reconstructed visuals are not presented as owned evidence.
- Visual design is derived from article content, but constrained by the brand system.
- Formal brand consistency is the default for publishable or client-facing decks.
- Platform capability gaps are reported instead of hidden.
- A handoff must separate `Created`, `Rendered`, `Read back`, and `Final`.

## Files

- [`SKILL.md`](./SKILL.md) — the actual OpenClaw skill document.
- [`skill-card.md`](./skill-card.md) — public-facing skill card metadata.
- [`references/visual-design-archetypes.md`](./references/visual-design-archetypes.md) — visual direction archetypes.
- [`references/visual-systems.md`](./references/visual-systems.md) — reusable visual system constraints.
- [`templates/storyboard-template.md`](./templates/storyboard-template.md) — storyboard and verification template.

## Publishing Note

This skill is intended to be reusable and GitHub-friendly. It should not contain local secrets, user-specific credentials, private paths, raw chat logs, or platform tokens.
