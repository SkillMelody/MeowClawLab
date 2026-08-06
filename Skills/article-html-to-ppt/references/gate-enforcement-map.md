# Gate Enforcement Map

Every rule PPTSmith calls a **hard gate** must name the detector, status rule, or
test that enforces it. A rule with no enforcement is a **review checklist** item:
useful guidance, but not a machine guarantee, and it must not be described as a
gate.

This distinction exists because the doctrine ran ahead of the code. Several rules
in `production-profiles.md` and `production-readiness-gates.md` were written as
hard gates while nothing in the pipeline checked them, so a deck that violated
them still reached `verified`. Anything below marked `review checklist` is
honestly labelled as such rather than implied to be automatic.

## Legend

- **Enforced** — a detector, status rule, or test fails when the rule is violated.
- **Partial** — enforced for some cases only; the gap is stated.
- **Review checklist** — human or agent judgment; no automatic check exists.

## Structural and package gates

| Gate | Status | Enforced by |
|---|---|---|
| PPTX opens and is a readable package | Enforced | `ppt_qa/package_inspector.py`; `package_delivery.pptx_readable` |
| No object out of slide bounds | Enforced | `PPTX_TEXT_OUT_OF_BOUNDS`, `GEOMETRY_OBJECT_OUT_OF_BOUNDS` |
| No blank slide | Enforced | `PPTX_BLANK_SLIDE`; render-side `RENDER_NEAR_BLANK_SLIDE` |
| Expected source text present | Enforced | `PPTX_EXPECTED_TEXT_MISSING` |
| No whole-slide raster | Enforced | `PPTX_WHOLE_SLIDE_RASTER`; `whole_slide_raster_count` in the status rule |
| Undeclared raster route rejected | Enforced | `PPTX_RASTER_ROUTE_UNDECLARED` |
| Native table/chart where required | Enforced | `PPTX_TABLE_NOT_NATIVE`, `PPTX_CHART_NOT_NATIVE` |
| Missing media detected | Enforced | `ppt_qa/package_inspector.py` relationship checks |
| No orphan solid-colour block | Partial | `PPTX_ORPHAN_SOLID_COLOR_BLOCK` fires on unnamed empty fills. It does **not** verify that a declared `Material:`/`Decoration:` layer is genuinely non-semantic, so the naming convention can still be used to silence it. Tightening this is optimisation-plan item T2.3. |

## Style contract gates

| Gate | Status | Enforced by |
|---|---|---|
| Font family within contract stacks | Partial | `PPTX_FONT_NOT_IN_CONTRACT`, warning severity only |
| Minimum body font size | Enforced | `PPTX_FONT_SIZE_BELOW_MINIMUM` measured against `typography.minimum_body_size_pt` |
| Minimum footnote font size | Enforced | Same code, measured against `typography.minimum_footnote_size_pt` for text whose shape name declares a footnote role (`Footnote:`, `Source:`, `Caption:`). Before this split, a footer built exactly to contract failed the contract's own gate; `tests/unit/test_visual_regressions.py` asserts both directions. |
| Colour within contract palette | Partial | `STYLE_COLOR_DRIFT`, warning severity, and it inspects shape fill/line only. Chart part colours in `ppt/charts/chart*.xml` are **not** inspected, so a default-palette chart passes. Planned as `PPTX_CHART_COLOR_DRIFT`, optimisation-plan item T1.3. |
| Card, table, chart, diagram, grid, spacing tokens applied | Partial | The Python Builder now applies all five component token groups plus grid zones, safe zones, and spacing rules; `tests/unit/test_python_pptx_builder.py` asserts both application and the absence of false "ignored" reports. What is still missing is a *gate*: a token the Builder cannot apply is reported in `build-manifest.known_limitations` but does not fail QA. Planned as `PPTX_STYLE_TOKEN_IGNORED`, optimisation-plan item T1.3. |
| Ignored-token report distinguishes gaps from metadata | Enforced | `_unsupported_style_warnings` classifies contract metadata (not reported), tokens another stage owns (reported with the owner named), and genuine Builder gaps; asserted in `tests/unit/test_python_pptx_builder.py`. Before this, all three shared one message and the list was unusable as a quality signal. |
| Title and body visually separated | Enforced (build side) | The Builder draws a title rule from `shape_tokens.divider_width_pt` on every slide. No detector verifies separation on an arbitrary deck. |

## Connector and diagram gates

| Gate | Status | Enforced by |
|---|---|---|
| Connector does not cross an unrelated node | Enforced | `PPTX_CONNECTOR_THROUGH_NODE` |
| Primary connectors do not cross | Enforced | `PPTX_CONNECTOR_CROSSING` |
| Arrowhead belongs to the connector line | Partial | `builders/python_pptx_adapter._add_routed_connector` emits `a:tailEnd` and `tests/unit/test_connector_routing.py` asserts it. No detector scans an arbitrary deck for simulated arrowheads. |
| Both endpoints bound to shapes | Review checklist | Asserted for the Python Builder in `tests/unit/test_connector_routing.py` (`stCxn`/`endCxn`). **No production code checks endpoint binding in a finished deck**, and `inspect_pptx.py`'s `native_connector_count` does not distinguish bound from unbound. Planned as `PPTX_CONNECTOR_ENDPOINT_UNBOUND`, optimisation-plan item T1.3. |
| Diagram IR valid before layout | Enforced | `scripts/validate_diagram_ir.py`, `schemas/diagram-ir.schema.json` |

## Information-design gates

| Gate | Status | Enforced by |
|---|---|---|
| Requested diagram not replaced by one text box | Review checklist | Expression-mode intent is not machine-checkable from the package alone |
| Title and body visually separated | Partial | The Python Builder always draws a title rule from `shape_tokens.divider_width_pt`; no detector checks an arbitrary deck. |
| Lower canvas is not accidental empty space | Review checklist | Planned as `PPTX_LOWER_CANVAS_EMPTY` at **warning** severity first, to calibrate false positives before it becomes an error. Optimisation-plan item T1.3. Measured on a real deck, card pages used only ~23% of the canvas, so this gate matters. |
| Text fits inside its shape | Review checklist | Cards are sized from a deliberately pessimistic content estimate (`_card_height`) and `tests/unit/test_visual_regressions.py` locks it, but nothing inspects an arbitrary deck for text overflowing a shape. Planned as `PPTX_TEXT_OVERFLOW_SHAPE`: this defect passed structural inspection on a real build. |
| Chart reads in the authored order | Enforced (build side) | Horizontal bar charts reverse the category axis rather than the series, so IR order is both the data order and the reading order; asserted in `tests/unit/test_visual_regressions.py`. |
| One unit per chart scale | Review checklist | A real build mixed percentages and counts on one axis and passed every check. No detector; the authoring rule lives in the expression-mode gate. |
| Low-content tables do not use tiny text | Partial | `PPTX_FONT_SIZE_BELOW_MINIMUM` catches absolute size, not the density judgment |
| Formal slide does not look like a wireframe | Review checklist | Rubric scoring at Premium only, with a supplied reference rubric |
| Excessive object count / fragmentation | Enforced | `PPTX_EXCESSIVE_OBJECT_COUNT`, `PPTX_OBJECT_FRAGMENTATION`, `PPTX_TEXT_FRAGMENTATION`, `PPTX_TINY_OBJECT_OVERLOAD` |

## Delivery status gates

| Gate | Status | Enforced by |
|---|---|---|
| `verified` requires real render evidence (Standard, Premium) | Enforced | `package_delivery.calculate_delivery_status`; `tests/unit/test_standard_render_gate.py` |
| Standard performs a representative render when available | Enforced | `run_pipeline.Pipeline.verify` passes `--render` for Standard and Premium; asserted in `tests/unit/test_standard_render_gate.py` |
| Missing renderer is reported, never fabricated | Enforced | `RENDER_ENGINE_UNAVAILABLE` preserved; status caps at `read_back`; manifest carries `provisional_reason` |
| `final` requires an explicit reference rubric (Premium) | Enforced | `run_pipeline.Pipeline.score` raises `PREMIUM_RUBRIC_REQUIRED`; rubric binding checked in `package_delivery._rubric_binding_matches` |
| Zero QA errors before delivery | Enforced | `calculate_delivery_status` returns `failed` on any error or fatal |
| Editable-core ratio meets the profile threshold | Enforced | `PROFILE_EDITABLE_THRESHOLDS` in `package_delivery.py` |
| No private path or secret in the delivery package | Enforced | `package_delivery.PRIVATE_PATTERNS` (`DELIVERY_PRIVATE_PATH_LEAK`, `DELIVERY_SECRET_LEAK`) |
| Builders and agents never handwrite `final` | Enforced | Status is computed, not read from input; `tests/integration/test_v2_pipeline.py` premium cases |

## Bundle integrity gates

| Gate | Status | Enforced by |
|---|---|---|
| No excluded path in a distributed archive | Enforced | `scripts/audit_bundle.py --mode archive`; `packaging/bundle-exclude.txt` |
| No recorded local absolute path | Enforced | `BUNDLE_ABSOLUTE_PATH_LEAK`; fix with `scripts/normalize_bundle_paths.py` |
| No secret or secret-shaped file | Enforced | `BUNDLE_SECRET_LEAK`, `BUNDLE_SECRET_SHAPED_FILE`, `BUNDLE_HIGH_ENTROPY_STRING` |
| Every audit exception states a reason | Enforced | `tests/unit/test_skill_metadata.py::test_every_audit_allowlist_entry_states_a_reason` |
| One identity across all documents | Enforced | `scripts/check_identity.py`; `tests/unit/test_skill_metadata.py` |
| Templates are copyable and schema-valid | Enforced | `tests/schemas/test_templates_validate.py` |
| The distributed archive passes its own suite | Enforced | `packaging/build_archive.sh` validates the unpacked copy, not the working tree |

## Maintaining this map

When adding a gate, add its row here in the same change. When adding a detector,
move the affected row from `review checklist` to `enforced` and name the code.
`tests/unit/test_gate_enforcement_map.py` asserts that every issue code cited
here actually exists, so a stale reference fails the suite rather than misleading
a reader.
