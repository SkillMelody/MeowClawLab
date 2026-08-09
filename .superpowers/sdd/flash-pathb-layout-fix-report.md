# Flash Path B Layout Fix Report

## Scope

Targeted PPTSmith Path B layout fix for the State of AI sparse deck regression in the registered worktree `feat/pptsmith-path-b-quality-floor`.

## What Changed

### PptxGenJS runtime

- Replaced the fixed single-row object placement with semantics-aware content frames.
- Added sidebar treatment for generated same-slide support (`provenance.derivation == "same_slide_evidence_augmenter"` or interpretation-role support) so support no longer consumes an equal primary column.
- Expanded single-object and two-object slides to use the available content canvas instead of a shallow upper band.
- Added a dedicated presentation-scale cover composition instead of the normal title strip.
- Suppressed internal slide-id labels such as `slide-001` / `S01` from becoming visible title text while preserving object metadata via `objectName`.
- Marked `typography.title_sizes_pt.cover` as a supported style input in the runtime.

### Python adapter

- Extended the existing dominant-primary layout rule into a general sidebar layout for generated same-slide support.
- For slides with two primary objects plus generated support, the primary area now stacks inside a dominant main zone while the support card stays in a readable sidebar.
- Kept support text visually secondary by avoiding large "hero" text sizing for interpretation/support cards that are only large because of the sidebar frame.

## Tests Added/Updated

- `test_two_primary_objects_stack_in_main_zone_when_generated_support_is_present`
- `test_generated_same_slide_support_uses_sidebar_layout_for_data_slides` (python-pptx)
- `test_generated_same_slide_support_uses_sidebar_layout_for_data_slides` (PptxGenJS)
- `test_cover_uses_presentation_scale_layout` (PptxGenJS)
- `test_internal_slide_id_is_not_rendered_as_visible_header_text`
- Updated the PptxGenJS style-support warning assertion for `title_sizes_pt.cover`

## Verification

Command:

```bash
python3 -m pytest Skills/article-html-to-ppt/tests/unit/test_python_pptx_layout.py Skills/article-html-to-ppt/tests/unit/test_python_pptx_builder.py Skills/article-html-to-ppt/tests/unit/test_pptxgenjs_builder.py
```

Output:

```text
============================== 32 passed in 6.78s ==============================
```

Command:

```bash
python3 -m pytest Skills/article-html-to-ppt/tests/unit/test_state_ai_sparse_ir_regression.py
```

Output:

```text
============================== 1 passed in 0.05s ===============================
```

## Notes

- `experiments/` and `quality-floor-state-ai-contact-sheet.png` were left untouched.
