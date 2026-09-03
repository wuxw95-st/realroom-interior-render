# RealRoom Interior Render

A practical skill/workflow specification for generating interior-design renders from real room photos while preserving the original architecture and camera geometry.

## Goals

- Keep walls, doors, windows, ceiling, room envelope, and camera viewpoint unchanged unless explicitly requested.
- Support strict local edits such as flooring replacement, sofa-cover changes, furniture rotation, and furniture insertion.
- Accept reference furniture images and real-world dimensions.
- Produce separate outputs for multiple source angles while keeping design choices consistent.
- Validate each result before delivery and reject outputs with unauthorized structural changes.

## Recommended engine

The default generation backend is based on the public `RodrigoSKohl/InteriorDesign-for-ComfyUI` workflow, extended with local-mask editing, reference-object guidance, and validation rules.

Core controls:

- Depth Anything V2 for geometry/depth preservation.
- Semantic segmentation for walls/floor/windows/doors and editable regions.
- ControlNet depth + segmentation guidance.
- IP-Adapter/reference-image conditioning for style or furniture appearance.
- Inpainting/masked editing for strict local edits.

## Modes

1. `strict_edit` — modify only the named object or region.
2. `material_replace` — replace floor/wall/material inside an explicit mask only.
3. `furniture_place` — place a referenced furniture item with dimension and position constraints.
4. `full_restyle` — restyle the room while keeping architecture and camera pose fixed.

See `SKILL.md` for the complete operating rules and `config/defaults.yaml` for default tolerances.
