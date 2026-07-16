# Benchmark Report

This document records the intended Phase 7 benchmark output format and current fixture scope.

## Current Fixture Scope

The repository includes ten small benchmark cases across five categories:

- `editorial_article`
- `product_report`
- `technical_agent`
- `design_spec`
- `anti_regression`

At least three categories include real PPTX baseline files generated from deterministic test fixtures. These baselines are intentionally small and are suitable for tests that run without Office or LibreOffice.

## Local Run

Use:

```bash
python3 scripts/benchmark.py --use-reference-rubric --run-id local-phase-7
```

The harness writes JSON and Markdown reports under `.ppt-work/benchmark/<run-id>/` unless explicit output paths are supplied.

## Limitations

The default harness does not generate new decks and does not fake visual rendering. It verifies existing baseline artifacts when present. If rendering is requested and no renderer is installed, the existing Stage 6 verifier reports renderer unavailability through QA evidence rather than fabricating screenshots.
