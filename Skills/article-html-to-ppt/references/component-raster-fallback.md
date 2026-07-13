# Component Raster Fallback

Use localized raster, SVG/HTML render, or generated visual components when a bounded slide component expresses relationship complexity, visual metaphor, spatial structure, or rich material treatment that native PPT objects would make confusing, ugly, brittle, or visually unfinished.

## Default Principle

Do not rasterize an entire deck unless the user explicitly asks for image-only delivery. The default final deck remains hybrid editable: titles, explanatory text, labels, sources, cards, tables, simple charts, and ordinary diagrams should be editable PPT objects.

For `relationship_visual`, `conceptual_scene`, and visual-heavy `hybrid_panel` slides, a rendered/generated bounded component is a planned delivery route, not merely late-stage rescue.

## Good Candidates

- complex relationship maps with many cross-links
- ecosystem maps or stakeholder networks
- capability landscapes with nested regions and soft boundaries
- conceptual metaphors or abstract spatial structures
- dense architecture murals where visual comprehension matters more than direct editing
- illustrated process scenes, IP illustrations, or editorial visual metaphors
- complex textures, material backgrounds, photos, or atmospheric layers

## Poor Candidates

Do not image-generate components that can be made clear and editable as native PPT objects:

- 2x2, 2x3, or 3x3 card grids
- ordinary comparison matrices
- tables and scorecards
- metric cards
- simple process lanes
- clean issue trees or dependency trees
- simple architecture diagrams with modest connector counts
- already-stabilized layouts after reducing connectors, grouping, or switching to cards

## Decision Test

Before choosing raster/generated delivery, answer:

1. Is the component's value mainly spatial relationship, visual metaphor, complex visual texture, or soft-boundary structure?
2. Would native PPT reconstruction require fragile connectors, nested shapes, masks, or effects?
3. Would the user reasonably accept reduced editability if title, interpretation, labels, source notes, and surrounding content remain editable?
4. Have simpler editable alternatives been tried or rejected for a clear reason?

Use localized image fallback only when 1-3 are yes, and 4 is documented.

## Implementation Contract

- crop the image to the component region, not the full slide
- keep title, interpretation line, source note, and footer editable
- overlay key labels as editable PPT text when later editing is likely
- store prompt and image path in the project directory
- disclose the rasterized component in `verification-report.md`
- count media objects and confirm only intended components are rasterized

## Native PPT Stop Conditions

Stop adding native PPT connectors when more than 8 nodes, more than 9 connectors, more than 2 relationship types, 3 connector crossings, labels below 10 pt, nested soft boundaries, or fragile micro-positioning are required.
