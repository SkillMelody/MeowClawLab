# Path B Quality Floor — Execution Plan

## Goal

Prevent sparse or semantically incomplete Path B IR from receiving `verified`. Preserve one primary anchor per slide while requiring supporting evidence/interpretation objects and truthful visual semantics.

## Root causes

1. `compile_visual_plan.py` replaces all slide objects for compilable components.
2. PPT IR schema/validator allows object-poor non-navigation slides.
3. Builder treats one semantic object as a complete page.
4. QA measures blankness/geometry/editability, not page completeness or chart semantics.

## Delivery order

1. Add a deterministic IR quality-floor module and fixtures.
2. Add failing tests for sparse data/judgment/closing pages; allow enrichment only from an explicit, independently source-bound `supporting_evidence` item.
3. Add strict page-completeness validation before delivery resolution.
4. Preserve existing objects when compiling visual plans; add generated primary component rather than replacing evidence/support objects.
5. Add rendered-PPT completeness checks and prevent `verified` when quality-floor or visual-completeness defects exist.
6. Run State of AI sparse-IR regression plus unit/integration matrix.

## Acceptance

- Non-navigation data pages require a data-bearing primary object and at least one supporting interpretation/evidence object.
- Judgment pages require evidence support; closing pages require 2–4 actionable objects.
- A visual-plan compiler never deletes unrelated source-backed evidence objects.
- Missing source-backed evidence results in a named blocker, not fabricated cards/data.
- `verified` is impossible when completeness checks fail.
- State of AI sparse IR without explicit independent evidence fails before delivery with named blockers; a complete, source-traceable IR passes both builders.
