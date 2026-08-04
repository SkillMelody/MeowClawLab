# PPTSmith P0 implementation handoff

## Scope and branch

- Worktree: `pptsmith-prd-p0-implementation`
- Branch: `feat/pptsmith-prd-p0-implementation-internal`
- Scope completed: product PRD direct-evidence routing, source-labelled native `product_ui_overview` and `interaction_storyboard` renderers, and the task-route schema compatibility repair.

## Acceptance repair

Independent acceptance found that a valid consulting/general route emits `product_prd` in `rejected_routes`, while `task-route.schema.json` omitted `product_prd` from that array's enum.

- RED: `python3 -m pytest -q tests/unit/test_task_router.py::test_product_prd_can_be_a_rejected_route_under_the_task_route_contract`
  failed with `ValidationError: 'product_prd' is not one of [...]` for `rejected_routes[3]`.
- GREEN: added `product_prd` to `rejected_routes.items.enum`; the contract test and `test_visual_narrative_stages_run_before_delivery_resolution` passed (`2 passed`).
- Regression contract: the test validates the actual `route_task()` result against the JSON Schema whenever a non-PRD route rejects `product_prd`.

## Builder-selection contract repair

The two product PRD renderers are full native implementations for `python_pptx` only. `pptxgenjs` remains unsupported for these component types; it must never silently omit, raster-fallback, or misrepresent them.

- A generic visual-narrative run still requests and uses `pptxgenjs`; it selects `research_report` and legally lists `product_prd` in `rejected_routes`.
- A PRD run with required `product_ui_overview` and `interaction_storyboard` components requests `auto` and the planner selects canonical `python_pptx`.
- A PRD run forced to `pptxgenjs` stops at `resolve_delivery` with the explicit `BUILDER_COMPONENT_UNSUPPORTED` code.
- RED evidence: the forced-builder test initially failed because the prior result contained only generic `BUILDER_ROUTE_UNSUPPORTED` / native-required codes. Adding the component-specific error contract brought it to GREEN.

## Final regression evidence

Command:

```text
python3 -m pytest -q --cache-clear \
  tests/unit/test_product_prd_native_prototypes.py \
  tests/integration/test_visual_narrative_phase1.py \
  tests/unit/test_task_router.py
```

Result: **18 passed**. The post-run pytest `lastfailed` cache was absent.

## Model evidence

- Requested model: `volcengine-agent-plan/deepseek-v4-pro`
- Actual model: `volcengine-agent-plan/deepseek-v4-pro`
- Fallback used: `false`
- Basis: gateway JSON response reported `ok: true`, `provider: volcengine-agent-plan`, `model: deepseek-v4-pro`, and `attempts: []`.
- Evidence: `P0-model-evidence.json`, `P0-model-evidence-manifest.json`.

## Real PRD deck evidence

Inputs: `P0-product-workbench-content-analysis.json` and `P0-product-workbench-storyline.json`.

The final run used the canonical `python_pptx` native builder and completed every pipeline stage through `package_delivery`.

- Delivery: `P0-product-workbench-real-deck-delivery/deck.pptx`
- LibreOffice 26.2.4.2: `passed`, **9/9** slides rendered, no warnings or errors; PDF preview is included with delivery.
- Structural inspection: `passed`, zero issues, 9 slides, native-text ratio `1.0`, zero media objects, zero whole-slide rasters.
- Editability readback: one native `product_ui_overview` space component and one native `interaction_storyboard` step component are present, with both source labels preserved.
- Final deck SHA-256: `4691ccec9b1d28b736bac226ddd1290735faaf4e6f05620c0c01fba293bb95af`.

Detailed run evidence remains under `P0-product-workbench-real-deck-work/` and the packaged delivery is under `P0-product-workbench-real-deck-delivery/`.

## Known boundary

This proves the recorded `python_pptx` + LibreOffice route. Native Microsoft PowerPoint / Keynote pixel parity has not been run and is not claimed.
