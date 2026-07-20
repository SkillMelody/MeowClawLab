# PPTSmith v2.0 Canonical Acceptance Package

This is the single committed acceptance package for MeowClaw PPTSmith v2.0. It contains one canonical production deck and one clearly secondary portability deck.

## Readiness claim

- **Accepted:** engineering-complete and **Standard production-ready on this verified environment**.
- **Canonical primary:** `decks/pptsmith-v2-standard-canonical-python_pptx.pptx`, built by `python_pptx` 1.0.2.
- **Portability evidence only:** `decks/pptsmith-v2-standard-portability-pptxgenjs.pptx`, built by PptxGenJS 4.0.1 from byte-identical source semantic contracts.
- **Not accepted:** Premium final readiness. This host has no verified PowerPoint/LibreOffice renderer. The fresh Premium run exited 2, stopped at `verify`, recorded `RENDER_ENGINE_UNAVAILABLE`, and created no user-facing delivery package.

The installed technical route and directory remain `article-html-to-ppt` for compatibility. The public identity is MeowClaw PPTSmith (`meowclaw-pptsmith`).

## Reproducibility contract

Both Standard runs consumed byte-identical copies of:

- `contracts/ppt-ir.json` — SHA-256 `044d9990071393f8f33dcbe141d070c5a466457fd24645a59ea8ba222b6992c6`
- `contracts/style-contract.json` — SHA-256 `d53ea191bc4bb97b39deaf6d36878043024bcab123dc89ec170d394830678f48`
- `contracts/requirements-standard.json` — SHA-256 `c862ad017a706691780494f274ac318d56d1caa47bfd5733e6f1e41bd6b03ea9`
- `contracts/delivery-plan-shared.json` — SHA-256 `9967d19cb525e3e426d049b19c1fa1cc624c64bfba7912e2a0838e10fec538d5`

The shared Delivery Plan file is a builder-neutral source semantic contract: its object and route semantics are shared across Builders. Each forced run resolved a fresh authoritative Delivery Plan, and every object has the same resolved `selected_route` value in both plans. Capability-sensitive resolver metadata is not identical: for Python, S05 `coverage-chart` retains `selected_route: "native_chart"` but records `decision: "fallback"` because support is partial, with reason codes `DELIVERY_BUILDER_PARTIAL_SUPPORT` and `DELIVERY_FALLBACK_SELECTED`; the Python Delivery Plan summary therefore has `fallback_count: 1`. PptxGenJS records that object as `decision: "selected"` and its Delivery Plan has `fallback_count: 0`. Compare each `evidence/<builder>/consumed-*.json` with `contracts/` and inspect `evidence/<builder>/delivery-plan.json`.

Source provenance:

- repository revision before Task 6 artifacts/docs: `704176e1216c5b4242126a4dd947176c95559a31`
- source commit timestamp: `2026-07-19T14:46:40+08:00`
- host: macOS 26.3.1 x64
- Python: 3.9.6
- Node: 26.4.0
- npm: 11.17.0
- pinned runtime dependencies: PptxGenJS 4.0.1 and JSZip 3.10.1
- isolated run root recorded inside unmodified generated evidence: `/private/tmp/pptsmith-task6.F1Rx5h` (the equivalent `/tmp` path refers to the same macOS location)

## Exact build commands

Run from the repository root; `$RUNROOT` must be a new empty temporary directory.

```bash
RUNROOT="$(mktemp -d /tmp/pptsmith-task6.XXXXXX)"
FIX="skills/article-html-to-ppt/tests/fixtures/v2-acceptance"

python3 skills/article-html-to-ppt/scripts/run_pipeline.py \
  --requirements "$FIX/requirements-standard.json" \
  --ppt-ir "$FIX/ppt-ir.json" \
  --style "$FIX/style-contract-editorial.json" \
  --builder python_pptx --profile standard \
  --work-dir "$RUNROOT/python_pptx/.ppt-work" \
  --output-dir "$RUNROOT/python_pptx/delivery" --json-output

python3 skills/article-html-to-ppt/scripts/run_pipeline.py \
  --requirements "$FIX/requirements-standard.json" \
  --ppt-ir "$FIX/ppt-ir.json" \
  --style "$FIX/style-contract-editorial.json" \
  --builder pptxgenjs --profile standard \
  --work-dir "$RUNROOT/pptxgenjs/.ppt-work" \
  --output-dir "$RUNROOT/pptxgenjs/delivery" --json-output

python3 skills/article-html-to-ppt/scripts/run_pipeline.py \
  --requirements "$FIX/requirements-premium.json" \
  --ppt-ir "$FIX/ppt-ir.json" \
  --style "$FIX/style-contract-editorial.json" \
  --builder pptxgenjs --profile premium \
  --work-dir "$RUNROOT/premium/.ppt-work" \
  --output-dir "$RUNROOT/premium/delivery" --json-output
```

Direct inspection was then run against each delivered PPTX with the same source contracts plus that run's resolved Delivery Plan and Build Manifest:

```bash
python3 skills/article-html-to-ppt/scripts/inspect_pptx.py "$DECK" \
  --ppt-ir "$FIX/ppt-ir.json" \
  --style "$FIX/style-contract-editorial.json" \
  --delivery "$WORK/contracts/delivery-plan.json" \
  --build "$WORK/contracts/build-manifest.json" \
  --output "$DIRECT_INSPECTION" --json-output
unzip -t "$DECK"
```

## Fresh run results

| Evidence | Canonical `python_pptx` | Portability `pptxgenjs` |
|---|---:|---:|
| Pipeline exit / state | 0 / completed | 0 / completed |
| PPTX bytes | 45,317 | 42,574 |
| PPTX SHA-256 | `136e08979d69be38823bf039fd24163328ba4f52f602c4bd1a9615ecec19bb21` | `13bcd9b81bd1c15042da3baaf1aed7d865043e9f8f5c9246d4839543acb852b8` |
| ZIP package test | valid, no bad entry | valid, no bad entry |
| OOXML entries / slide XML parts | 57 / 9 | 74 / 9 |
| Slide count | 9 | 9 |
| Source semantic objects | 9 | 9 |
| Native text / editable-core ratio | 1.0 / 1.0 | 1.0 / 1.0 |
| Native tables / charts | 1 / 1 | 1 / 1 |
| Process evidence | 3 editable nodes + 2 native connectors | 3 editable nodes + 2 arrow shapes; inspector connector count 0 |
| Rasterized area / whole-slide raster | 0.0 / 0 | 0.0 / 0 |
| Delivery Plan resolver fallback decisions | 1 (S05 `coverage-chart`; selected route remains `native_chart`) | 0 |
| Build Manifest/runtime fallbacks | 0 | 0 |
| Built route for S05 `coverage-chart` | `native_chart` | `native_chart` |
| QA | pass; 0 errors, 0 warnings | warning; 0 errors, 11 warnings |
| Trusted delivery / Delivery Manifest | verified / verified | verified / verified |
| Final PPTX count in isolated output | exactly 1 | exactly 1 |

The PptxGenJS warnings are retained, not suppressed: they are `PPTX_EMPTY_TEXT_BOX` findings on decorative shape primitives. Message-bearing text, table, chart, and process labels remain editable. Python's resolver-level fallback decision is fully disclosed above; it did not become an actual build fallback. Both runtime executions and Build Manifests report zero actual build fallbacks, and both decks built S05 as `native_chart`.

## Direct package inspection

The package was not accepted from manifests alone. Each actual `.pptx` was opened as ZIP/OOXML, tested with `unzip -t`, inventoried, and analyzed by `inspect_pptx.py`. The direct reports are `evidence/<builder>/direct-inspection.json`; raw package inventories are the two `evidence/*-zip-inventory.txt` files.

Native-chart evidence is present as one OOXML chart part in each package and as `native_chart_count: 1` in direct inspection. The process slide is S06. Python uses native connectors; PptxGenJS uses editable arrow shape primitives, so its generic inspector reports zero connector objects while preserving the three editable process labels and no fallback.

## Gates

Fresh Task 6 gates are captured verbatim in `gate-results.txt`:

- 243 tracked JSON files parsed.
- 65 tracked Python files compiled.
- Node runtime syntax check passed.
- PptxGenJS unit/runtime tests: 8 passed.
- Shared two-Builder acceptance tests: 2 passed.
- Profile/Builder pipeline matrix: 12 passed.
- Full skill suite: 137 passed.
- `git diff --check`: passed.
- Both Standard builds: exit 0, exactly one nonempty PPTX each.
- Fresh Premium no-renderer run: exit 2, blocked at verify, no delivery directory.

## Package map

- `decks/`: one canonical PPTX plus one explicitly labeled portability PPTX.
- `contracts/`: immutable source semantic contracts required to reproduce the Standard runs.
- `evidence/python_pptx/` and `evidence/pptxgenjs/`: unmodified generated manifests, QA, direct/pipeline inspections, consumed contracts, capability/profile/state evidence, and ZIP tests.
- `evidence/premium-blocked/`: fresh renderer-unavailable proof; no final deck.
- `SHA256SUMS`: hashes for every other file in this package.

`SHA256SUMS` uses repository-root-relative paths. Verify all entries by running the following exact command **from the repository root**:

```bash
shasum -a 256 -c deliverables/pptsmith-v2-acceptance/SHA256SUMS
```

## Limitations

1. **Premium is not final.** A verified PowerPoint/LibreOffice renderer is unavailable; there is no render/readback/rubric evidence and no Premium package.
2. Standard acceptance is structural and contract-based on this verified environment, not a claim of visual parity across Office implementations.
3. PptxGenJS has 11 disclosed warning-only decorative empty-text-box findings.
4. Capability evidence reports required style fonts missing on this host; generated decks may substitute fonts when opened elsewhere.
5. `officecli` and `html_svg` are not part of this two-Builder acceptance claim.
