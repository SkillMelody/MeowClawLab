# Expression Mode Gate

Use this gate before `slide_manifest.json` is finalized. It decides whether each slide should be text-first, card-first, table-first, data-first, relationship-visual, conceptual-scene, or hybrid-panel.

## Core Question

What must the audience understand or decide after this slide?

- If they must believe a conclusion, use `textual_argument`.
- If they must compare parallel items, use `structured_cards` or `table_matrix`.
- If they must understand magnitude, trend, ranking, or composition, use `data_visual`.
- If they must understand how parts connect, influence, route, depend, govern, loop, or exchange value, use `relationship_visual`.
- If they must remember or feel an abstract idea, use `conceptual_scene`.
- If they need both a visual relationship and short interpretation, use `hybrid_panel`.

## Relationship-Visual Strong Triggers

Classify as `relationship_visual` when the source contains one strong trigger:

1. Many-to-many relationships.
2. Directional flow.
3. System, ownership, or trust boundaries.
4. Feedback loops or flywheels.
5. Ecosystem or stakeholder structure.
6. Causal chains.
7. Architecture or operating model.
8. Spatial metaphor carrying meaning.

## Relationship-Visual Medium Triggers

Classify as `relationship_visual` when two or more are true:

1. Relationship verbs dominate: connects, routes, depends, triggers, loops, governs, orchestrates, integrates.
2. Prose repeats `A affects B`, `B depends on C`, or `actor -> action -> system` patterns.
3. The same entities recur across multiple paragraphs with changing roles.
4. Prose needs several sentences before the relationship is understandable.
5. A table hides the main insight because interaction matters more than cell values.
6. Cards would falsely imply the items are parallel.
7. A reader would ask how things connect, who controls what, or where data goes.
8. Risk, security, control, ownership, or trust boundaries are essential.

## Anti-Misclassification Rules

Do not choose `textual_argument` merely because the source is prose. Articles often encode relationships in paragraphs.

Do not choose `structured_cards` merely because there are 4-8 named items. If those items depend on, route to, control, reinforce, or constrain each other, use `relationship_visual` or `hybrid_panel`.

Do not choose `table_matrix` merely because attributes repeat. If the point is interaction or flow, the table is secondary evidence, not the primary anchor.

Do not choose `relationship_visual` for decorative diagrams. If the audience can understand faster through a two-column contrast, chart, or card group, use the simpler editable structure.

## Visual Component Plan

Slides with `relationship_visual`, `conceptual_scene`, or visual-heavy `hybrid_panel` must define:

- `component_type`
- `audience_question`
- `primary_entities`
- `relationship_types`
- `simplification_strategy`
- `editable_core`
- `visual_component_delivery`
- `raster_acceptance_reason` when using generated or raster output

## Delivery Priority

1. Use editable PPT when the relationship can be simplified into a clean lane, group, layer, issue tree, or simple architecture map.
2. Use SVG/HTML render for deterministic complex diagrams.
3. Use generated or rasterized localized components for complex ecosystems, soft boundaries, conceptual scenes, dense architecture murals, or spatial metaphors.
4. If image generation is unavailable, split the slide or simplify into editable groups.

## Native PPT Stop Conditions

Stop forcing native PPT connectors when any condition holds:

- more than 8 primary nodes
- more than 9 meaningful connectors
- more than 2 relationship types
- 3 or more connector crossings
- labels below 10 pt
- nested regions or soft boundaries required
- fragile micro-positioning required
- output resembles a wireframe, whiteboard, or workflow-tool screenshot

## Verification

The verification report must list relationship/conceptual/hybrid slides and confirm planned delivery route, editable core, bounded raster use, and why simpler editable alternatives were used or rejected.
