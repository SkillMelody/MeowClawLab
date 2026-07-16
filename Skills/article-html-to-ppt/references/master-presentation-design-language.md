# Master Presentation Design Language

Use this as the shared design language for serious decks. It is a hierarchy system, not decoration.

## Order Of Design Decisions

1. Content truth.
2. Audience decision.
3. Expression mode.
4. Page archetype.
5. Primary anchor.
6. Visual priority and deletion.
7. Style contract.
8. Delivery route.

## Professional Slide Principles

- One slide, one decision or understanding shift.
- The title states the judgment, not the topic.
- The primary anchor should be recognizable within three seconds.
- Supporting units should explain, prove, or qualify the anchor.
- Visual accents must lower cognitive load, not fill space.
- Design systems are complete languages: typography, spacing, color, component grammar, proof style, and density rules.
- Builders must read visual parameters from `style-contract.json`; they should not invent colors, type sizes, spacing, radius, table styling, chart colors, connector widths, image crop rules, or footer styling.

## Hierarchy Rules

Use size, weight, contrast, position, and grouping before adding decoration.

Prefer:

- fewer stronger elements
- clear sectioning
- restrained color
- consistent component geometry
- explicit source and assumption notes

Avoid:

- equal-size boxes for unequal ideas
- decorative icons that repeat labels
- high-contrast grids behind dense content
- connector webs
- tables used as storage bins
- full-slide screenshots unless explicitly approved
- raw hex values, ad hoc font sizes, arbitrary spacing, or one-off component styling outside the style contract

## Hybrid Editable Delivery

Default final decks are hybrid editable: titles, interpretation lines, source notes, labels, cards, tables, simple charts, and ordinary diagrams remain editable. Raster/SVG/generated material may be used for bounded visual components, rich backgrounds, photos, illustrations, complex spatial maps, or atmospheric layers.
