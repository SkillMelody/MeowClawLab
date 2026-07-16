# Migration v1.1 to v1.2

Canonical migration guide: `docs/migration-v1.1-to-v1.2.md`.

This reference is retained as a short compatibility pointer for existing links.

## Field Mapping

| v1.1 field | v1.2 field |
| --- | --- |
| `judgment_title` | `title` with `title_role=judgment` |
| `expression_mode` | `primary_expression` |
| `hybrid_panel` | primary expression + `supporting_expressions` |
| `visual_component_plan` | typed `objects[]` + `delivery_contract` |
| `source_labels` | `source_refs[]` |
| `style_system` + `palette_name` | `style_contract_ref` plus full Style Contract v2 |
| `score` | QA/rubric evidence in `qa-report.json` |

## Title Roles

Use `judgment` for answer-first content slides. Use non-judgment roles for cover, agenda, section, reference, instruction, and closing slides.

## Production Profiles

Use `fast`, `standard`, or `premium` instead of one fixed artifact list.

## Deprecated Templates

`templates/slide-manifest-template.json` and `templates/design-language-schema.json` remain for one compatibility cycle. New work should use PPT IR and Style Contract v2 examples.

## Palette Aliases

Keep existing palette names working, but document neutral internal names:

- `mckinsey` / `palette-cl-mckinsey` -> `navy-consulting`
- `bcg` / `palette-cl-bcg` -> `forest-consulting`
- `linear` / `palette-pr-linear` -> `graphite-lavender`
- `stripe` / `palette-pr-stripe` -> `graphite-steel`
- `ibm-whitepaper` / `palette-tb-ibm-whitepaper` -> `engineering-blue`

## Status

Do not report `final` unless Premium hard gates pass. A created PPTX is only `created` until rendered/read back/verified.
