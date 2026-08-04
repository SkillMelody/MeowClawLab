# PPTSmith P0 implementation handoff

## Scope and branch

- Worktree: `pptsmith-prd-p0-implementation`
- Branch: `feat/pptsmith-prd-p0-implementation-internal`
- Scope completed: product PRD direct-evidence routing, source-labelled native `product_ui_overview` and `interaction_storyboard` renderers, the task-route schema compatibility repair, and the visual FAIL rework below.

## Visual FAIL rework

- `product_ui_overview` now renders a native, editable, fixed `16:10` placeholder named `Placeholder:product_ui_overview:application_screenshot`. It is explicitly labelled `待替换：应用截图`, records that the asset is missing, and asks for a real PNG/JPG plus source. It is an outline/text shape, not an image or a fabricated UI screenshot.
- Design evidence now records `coverage_matrix.application_screenshot`: requirement, asset status, consumer object, aspect ratio, target page and target region. The current PRD resolves this to `missing`, `S02`, and `product_ui_overview.primary_visual`.
- PRD injections replace inherited generic acceptance cards on S02/S03 with the direct product evidence page, avoiding overlap and preserving an answer-first judgment required by the delivery validator.
- `interaction_storyboard` now has differentiated native state affordances for supplied async/Diff/decision evidence. The current PRD only supplies `select`, so S03 explicitly says that later states were not given and were not fabricated.

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
- Final deck SHA-256: `7a0ea7dc5b75d49373fa536da19dc18f9b05f921acc8a8fc108a4d63d3d9d0c2`.

Detailed run evidence remains under `P0-product-workbench-real-deck-work/` and the packaged delivery is under `P0-product-workbench-real-deck-delivery/`.

## Builder-contract rework (second commit)

Two component types (`product_ui_overview`, `interaction_storyboard`) are full native implementations for `python_pptx` only. The following were added to enforce this:

- `selector.py`: new `BUILDER_COMPONENT_UNSUPPORTED` blocking code — when a forced pptxgenjs builder is given a product PRD with required native-only components, `resolve_delivery` fails with the explicit code rather than a generic unsupported error.
- Integration test: verifies that `--builder pptxgenjs` with a product PRD content-analysis stops at `resolve_delivery` with `BUILDER_COMPONENT_UNSUPPORTED` in stderr.
- Integration test: verifies that `--builder auto` with product PRD selects `python_pptx`.
- Generic visual-narrative regression still uses `pptxgenjs` and legally rejects `product_prd`.

## Screenshot placeholder rework

`product_ui_overview` now renders:
- Native, editable `Placeholder:product_ui_overview:application_screenshot` with fixed `16:10` aspect ratio, labelled `待替换：应用截图`.
- Screenshot is a **secondary zone**; the main body is a native editable workspace sketch with:
  - Readable TopBar (horizontal bar with menu items)
  - Central Canvas with three node boxes (文章节点, AI 建议, 导出选区) connected by thin-line connectors
  - Sub-labels below each node with source references (§5, §8.2, §11)
  - Inspector panel (右侧属性面板)
  - Dock bar at bottom
- No AI-fabricated UI, no image/raster.
- Design evidence records `coverage_matrix.application_screenshot` with asset_status, aspect_ratio, page/region.

## Interaction storyboard rework

`interaction_storyboard` now renders:
- Continuous native state frames: action (entry trigger) → async_state (AI feedback/streaming) → result (Diff preview) → decision (accept/undo)
- Error/CONFLICT branch: `error` kind steps are rendered as a separate flow below the main flow, connected from the last main step with a warning-colored connector, showing the error label and action options (重试 / 重新生成 / 查看差异).
- S03 judgment updated to reflect that the PRD has documented the full interaction flow.

## Design evidence coverage

- `coverage_matrix.application_screenshot`: required=true, asset_status=missing, consumed=true, consumer_object_ids, placeholder with aspect_ratio 16:10, page_id=S02, region=product_ui_overview.primary_visual.
- `coverage_matrix.product_ui_overview`: required=true, consumed=true, with default workspace zone injection for richer rendering.
- `coverage_matrix.interaction_storyboard`: required=true when interactions present, consumed=true, steps carry kind/action information.

## Final real-deck generation

Same PRD inputs with updated content-analysis containing richer space/interaction evidence.

Command:
```text
python3 Skills/article-html-to-ppt/scripts/run_pipeline.py \
  --requirements P0-product-workbench-real-deck-work/contracts/requirements.json \
  --ppt-ir P0-product-workbench-real-deck-work/contracts/ppt-ir.json \
  --style P0-product-workbench-real-deck-work/contracts/style-contract.json \
  --content-analysis P0-product-workbench-content-analysis.json \
  --storyline P0-product-workbench-storyline.json \
  --builder auto --profile standard \
  --work-dir P0-product-workbench-real-deck-work \
  --output-dir P0-product-workbench-real-deck-delivery --json-output
```

Result: `ok: true`, state `verified`, 9 slides.

- LibreOffice 26.2.4.2: **9/9** slides rendered, zero warnings/errors.
- Structural QA: zero errors, zero fatals.
- `native_text_ratio`: 1.0, `editable_core_ratio`: 1.0, `media_count`: 0, `whole_slide_raster_count`: 0, `rasterized_area_ratio`: 0.0.
- Readback: one `product_ui_overview` and one `interaction_storyboard` native component present with source labels.
- Connector count: 6 (3 main-flow + 3 canvas-internal).
- Delivery manifest updated with `commit_sha: 40bc3d3`.
- Deck SHA-256: `7a0ea7dc5b75d49373fa536da19dc18f9b05f921acc8a8fc108a4d63d3d9d0c2`.
- Detailed run evidence: `P0-product-workbench-real-deck-work/` (untracked, reproducible).
- Packaged delivery: `P0-product-workbench-real-deck-delivery/`.

## Model evidence

- Requested: `volcengine-agent-plan/deepseek-v4-pro`
- Actual: `volcengine-agent-plan/deepseek-v4-pro`
- Fallback used: `false`
- Gateway response: `ok: true`, `attempts: []`

## Final regression

Command:
```text
python3 -m pytest -vv --cache-clear \
  tests/unit/test_product_prd_native_prototypes.py \
  tests/unit/test_design_evidence.py \
  tests/unit/test_task_router.py \
  tests/integration/test_visual_narrative_phase1.py
```

Result: **22 passed** — all unit + integration tests. `pytest lastfailed` cache absent.

## Known boundary

This proves the recorded `python_pptx` + LibreOffice route. Native Microsoft PowerPoint / Keynote pixel parity has not been run and is not claimed.
