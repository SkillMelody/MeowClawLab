# Content Density Playbook for McKinsey-Class Slide Decks

## Principle

**Information density is about using the available space fully, not about cramming more data points.**
A slide with 2 bars can be visually dense if the bars are annotated, compared, and contextualized. A slide with 10 bars is sparse if they're tiny and unlabeled.

## Slide Canvas Budget

The usable area per slide (after margins) is approximately:
- **Width**: 12.2 inches (13.333 − 2 × 0.55 margin)
- **Height**: 6.8 inches (7.5 − 0.35 title − 0.35 footer)
- **Total canvas**: ~83 sq inches

## Per-Element Space Budget

| Element | Typical Height | Notes |
|---|---|---|
| Title (1 line) | 0.55–0.65" | 22–26pt, one line preferred |
| Title (2 lines) | 0.75–0.90" | 20–22pt, for compound titles |
| Subtitle/lead-in | 0.40–0.50" | 10–13pt, 1–2 sentences max |
| Chart area | 4.0–5.0" | Fills remaining vertical space |
| Table area | 3.5–5.0" | Depends on row count |
| Footer | 0.24" | Source + page number |

## Content Rules Per Object Type

### Bar / Column Chart
- **Minimum**: 3 categories with meaningful labels (not "A/B/C")
- **Optimal**: 5–8 categories — this is the McKinsey sweet spot
- **Maximum**: 10 categories (more → consider horizontal bars or split slides)
- **Multi-series**: 2 series ideal for comparison (e.g. "High performers" vs "Others")
- **Axis labels**: Keep category labels under 15 characters; abbreviate if needed
- **Data labels**: Always show values on bars

### Table
- **Minimum**: 3–4 data rows with meaningful comparisons
- **Optimal**: 4–8 rows, 2–4 columns
- **Column constraint**: Narrowest column ≥ 1.2" at minimum font
- **Row height**: Allow 0.35–0.45" per row at 10pt
- **Cell text**: Keep under 30 characters per cell; use abbreviations

### Cards / Metrics
- **Layout**: 3–4 cards per row, max 2 rows (6–8 total)
- **Content per card**: 1 metric value (large) + 1 short label (≤10 chars)
- **Never**: use cards when a bar chart would show the same data more clearly

## Anti-Patterns

| Pattern | Problem | Fix |
|---|---|---|
| 2-bar chart | Wasted space | Add annotation box, or merge into a comparison slide |
| Single-series with 3 categories | Underwhelming | Add a second series (e.g. "Previous year" or "Industry average") |
| 2×2 table | Reads as a list, not data | Convert to 4 metric cards or a structured text layout |
| Empty chart area >40% | Wasted canvas | Enlarge chart, add insight callout, or reduce slide count |
| Same chart type 5 slides in a row | Monotonous | Alternate bar/column/stacked/waterfall |

## Source Extraction Check

Before writing the IR, verify:
1. **Are the 3–5 most important numbers from the source document present?**
2. **Does each chart answer one clear question?** (not "here's some data")
3. **Are comparisons explicit?** (not "X is 20%" but "X is 20% vs Y's 12%")
4. **Is every data point sourced?** (source_refs on every object)
