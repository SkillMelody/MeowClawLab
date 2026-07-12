# Component Raster Fallback

Use localized raster/image generation only when a specific slide component expresses a visual relationship that native PPT objects are likely to make confusing, ugly, or overly fragile.

## Default Principle

Do not rasterize an entire slide unless the user explicitly asks for image-only delivery. The default final deck remains hybrid editable: titles, explanatory text, labels, sources, cards, tables, simple charts, and ordinary diagrams should be editable PPT objects.

Localized component images are a fallback for relationship complexity, not a generic fallback for style polish.

## Good Candidates For Localized Image Components

Use a generated or rendered image for a bounded component when the component is primarily visual and hard to reconstruct cleanly with PowerPoint primitives:

- complex relationship maps with many cross-links
- ecosystem maps or stakeholder networks
- capability landscapes with nested regions and soft boundaries
- conceptual metaphors or abstract spatial structures
- dense architecture murals where precise editability is less important than visual comprehension
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

For these, improve the native PPT construction: reduce text, group objects, remove connector webs, use stronger hierarchy, and preserve editability.

## Decision Test

Before choosing localized raster fallback, answer:

1. Is the component's value mainly the spatial relationship, visual metaphor, or complex visual texture?
2. Would native PPT reconstruction require many fragile connectors, nested shapes, masks, or effects?
3. Would a user reasonably accept that this component is less editable if the slide title, explanatory labels, source notes, and surrounding text remain editable?
4. Have simpler editable alternatives been tried first, such as a card grid, lane diagram, grouped modules, issue tree, or split slide?

Use localized image fallback only when the answer to 1-3 is yes, and 4 has been attempted or rejected for a clear reason.

## Implementation Contract

When using localized raster fallback:

- crop the image to the component region, not the full slide
- keep slide title, short interpretation, source note, and page footer native/editable
- preferably overlay key labels or section tags as editable PPT text if they may need later editing
- store the prompt and image path in the project directory
- disclose the rasterized component in `verification-report.md`
- count media objects and confirm only intended components are rasterized

## Prompt Requirements

The prompt must describe the component, not the whole slide. Include:

- canvas aspect ratio and white/transparent background requirement
- exact conceptual structure and number of groups/nodes
- visual style tokens from the active style system
- explicit instruction to avoid slide title, footer, page number, logos, watermarks, and tiny unreadable text
- whether text should be omitted, minimal, or placeholder-safe

## Slide 08 Lesson

The McKinsey AI 2025 Slide 08 experiment showed the boundary clearly:

- original tangled six-practice relationship diagram: candidate for restructuring or localized image fallback
- revised 2x3 six-practice card arrangement: poor candidate for image fallback, because it is now stable, clear, and editable as PPT objects

Rule: once a complex diagram has been simplified into a clean card/matrix layout, preserve editability unless the user explicitly asks for image styling.
