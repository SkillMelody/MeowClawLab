# Benchmark Methodology

Phase 7 adds a calibrated benchmark harness around the production rubric. The benchmark is not a renderer, not a deck generator, and not a substitute for expert review. It collects fixed cases, baseline artifacts, QA evidence, automatic metrics, and reference scorecards so future changes can be compared against stable examples.

## Benchmark Inputs

Each case lives under `tests/fixtures/benchmark/<case-id>/` and declares source files, requirements, expected contracts, a reference rubric, anti-patterns, expected automatic metrics, and optional baseline artifacts.

Cases may be partial. If no baseline PPTX or renderer is available, the harness must report that state honestly as `baseline_available=false`, `verification_status=unavailable`, or `manual_review_required=true`.

## Scoring Layers

Hard gates and rubric scores are separate:

- QA `fatal` or `error` issues fail the hard gate even when a reference score is high.
- Rubric score below `14/18` fails quality even when QA reports no errors.
- Any zero dimension fails quality.
- Automatic metrics are evidence and calibration signals, not final human judgment.

When no model or human scorer is configured, `scripts/score_deck.py` emits `manual_review_required=true` and nullable final dimension scores. Provisional scores remain available for triage, but they are not treated as final rubric judgment.

## Automatic Evidence Map

- `title_role_and_message_quality`: judgment-title specificity, role validity, unsupported judgments.
- `content_fidelity`: source coverage, unknown references, assumptions, missing required sections.
- `expression_architecture`: primary expression presence, supporting-expression overload, competing anchors, relationship-to-cards regressions.
- `page_composition`: overflow, out-of-bounds objects, blank slides, object density.
- `component_craft`: color drift, tiny-object overload, rasterized table/chart regressions.
- `editability_hygiene`: native text/editable-core ratio, whole-slide raster, render success, QA errors/fatals.

## Running

```bash
python3 scripts/benchmark.py --use-reference-rubric --run-id local-phase-7
```

Compare two runs:

```bash
python3 scripts/compare_benchmark_runs.py \
  --baseline .ppt-work/benchmark/baseline/benchmark-report.json \
  --candidate .ppt-work/benchmark/candidate/benchmark-report.json \
  --output .ppt-work/benchmark/comparison.json \
  --markdown .ppt-work/benchmark/comparison.md
```

## Interpreting Results

The first question is whether the hard gate passed. The second question is whether the rubric quality passed. A deck is not production-ready unless both are acceptable or a human explicitly waives known limitations.

Use benchmark trends to find regressions, not to claim universal quality. The fixed fixture set should grow when a real production failure appears.
