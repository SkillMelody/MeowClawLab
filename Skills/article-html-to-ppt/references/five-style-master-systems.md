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
