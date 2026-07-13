# Style Palette Options

Each style has 2-3 pre-defined palette options. The user picks one style and one palette at the start of a deck (see Gate 3: Visual Direction Confirmation in SKILL.md). DO NOT generate colors outside this list unless the user explicitly provides new hex values. Words like "restrained", "modern", "premium", or "tech" are NOT color instructions — always resolve to a concrete palette id below.

Token meaning:
- `primary`: dominant brand/structure color (titles, key bars, headers).
- `accent`: emphasis color (callouts, key figures, active states).
- `background`: page base color.
- `text`: primary body/text color on the background.
- `secondary`: supporting/secondary accent (dividers, tags, muted labels, chart series 2).

Write the chosen palette id and its exact hex tokens into `style_contract.json`.

---

## consulting-light

### palette-cl-mckinsey (麦肯锡强蓝)
- primary: #051C2C
- accent: #2251FF
- background: #FFFFFF
- text: #1F2937
- secondary: #00A9F4

### palette-cl-bcg (BCG深绿)
- primary: #004C2F
- accent: #00823B
- background: #F9F9F9
- text: #1F2937
- secondary: #6B7280

---

## product-report

### palette-pr-linear (Linear 风 — deep slate + electric purple)
- primary: #1A1A2E
- accent: #7B68EE
- background: #F7F7FB
- text: #1F2937
- secondary: #5E6AD2

### palette-pr-stripe (Stripe 风 — near-black + electric blue)
- primary: #0F0F0F
- accent: #0055FF
- background: #FAFAFA
- text: #1A1A1A
- secondary: #6B6E73

---

## technical-blueprint

### palette-tb-ibm-whitepaper (IBM 白皮书 — light engineering, print-friendly)
- primary: #005A9E
- accent: #005A9E
- background: #FAFAFA
- text: #1F2937
- secondary: #374151

Note: accent = primary here. Use neutral `#374151` as second-tier emphasis for secondary nodes. Rely on weight and spatial isolation for hierarchy, not a second hue.

---

## consulting-blueprint-hybrid

### palette-cbh-deep-amber (深蓝 + 琥珀金)
- primary: #1B2A4A
- accent: #E8A838
- background: #F9FAFB
- text: #2D3748
- secondary: #4A5568

Use accent sparingly — a highlight rule, a number underline, a single labeled arrow. Never as a large fill.

---

## editorial-knowledge

### palette-ek-warm-paper (暖棕纸质感)
- primary: #2D2926
- accent: #E8633A
- background: #FAF7F2
- text: #4A4540
- secondary: #7A736D
