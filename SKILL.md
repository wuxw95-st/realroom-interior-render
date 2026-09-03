---
name: realroom-interior-render
description: Generate or edit interior design renders from real room photographs with strict architecture, camera, object, material, and multi-angle consistency constraints.
version: 1.0.0
---

# RealRoom Interior Render Skill

## Purpose

Use real room photographs as the immutable spatial base. The requested design change is an edit to that base, not permission to invent a new room.

## Non-negotiable hierarchy

Follow constraints in this order:

1. User's explicit latest instruction.
2. Preserve architecture and camera geometry.
3. Preserve every object/material the user did not authorize changing.
4. Apply requested furniture dimensions, orientation, position and reference appearance.
5. Maintain cross-angle design consistency.
6. Improve realism and aesthetics only inside the remaining freedom.

A prettier image is a failure if it violates a higher-priority constraint.

## Default preservation lock

Unless explicitly authorized, NEVER change:

- wall positions, wall depth, wall openings or room proportions
- doors, windows, balcony openings, columns, beams or ceiling geometry
- camera position, camera height, focal perspective, crop or viewing direction
- fixed cabinetry, built-ins, radiators, AC units and visible architectural fixtures
- the identity, position, orientation or approximate scale of existing furniture

Do not add architectural features that are absent from the source photo.

## Input roles

Treat uploaded images according to their role:

- `room_source`: photograph whose geometry/camera must be preserved.
- `design_reference`: style/material/decor reference; do not copy its architecture.
- `object_reference`: exact or approximate furniture/object appearance to insert.
- `floorplan`: supplementary spatial evidence; never override a clearly visible source photo without explicit instruction.
- `previous_approved_render`: design-state reference for carrying the same scheme to another room angle.

When multiple images are provided, infer roles from the user's labels/order and latest instruction. Never silently swap the source and reference roles.

## Modes

### strict_edit

Use when the user asks for one or a few exact changes (for example: add sofa cushions, rotate the bed 90 degrees, add one wardrobe).

Rules:
- Build an edit mask around only the requested target.
- Protect the rest of the image.
- Use the lowest denoise/generation freedom that can accomplish the edit.
- Composite protected source pixels back when practical.

### material_replace

Use for flooring, wall paint, textile or finish changes.

Rules:
- Segment the target surface.
- Preserve its perspective, boundaries, occlusion and lighting.
- Never let floor replacement leak into walls, skirting, furniture or doors.
- Material scale must be physically plausible.

### furniture_place

Use when adding/replacing furniture from a reference image.

Rules:
- Respect stated dimensions in metres/centimetres.
- Use visible room dimensions, wall length, floorplan or known objects to estimate scale.
- Respect the requested wall, corner, facing direction and rotation.
- Preserve clearance for doors/windows unless the user explicitly requests otherwise.
- Reference-image identity has priority over generic style prompting.

### full_restyle

Use when the user wants a complete style transformation.

Rules:
- Architecture and camera remain locked.
- Existing furniture explicitly marked as non-replaceable must remain and may only receive authorized soft-furnishing/material edits.
- New decor must fit existing free space rather than force spatial changes.

## Multi-angle consistency

When rendering multiple photos of the same room:

- Output one independent image per source angle. Never combine them into a collage unless requested.
- Carry forward the approved design state: flooring species/pattern/tone, wall finish, sofa cover, cushions, rugs, curtains, lamps, artwork and furniture identity.
- Do not mirror or rotate the room to make angles easier.
- An object visible in two angles must retain the same material, color, dimensions and placement.
- Treat the first approved render as a design reference only; each subsequent output must still use its own real photograph as the geometry base.

## Prompt construction

Positive prompt should describe only authorized design changes plus realism. Append:

`photorealistic interior photography, physically plausible materials, consistent perspective, preserve original room geometry, preserve original camera viewpoint, preserve all unrequested objects`

Negative prompt should include:

`changed architecture, moved wall, new wall, changed window, changed door, altered room proportions, different camera angle, different viewpoint, mirrored room, warped perspective, duplicated furniture, missing existing furniture, floating furniture, incorrect scale, material leakage, surreal, CGI look, text, watermark`

## Control strategy

Recommended control stack:

1. Source image normalization.
2. Depth Anything V2 depth map from `room_source`.
3. Semantic segmentation map.
4. Protected-region/edit mask.
5. Depth ControlNet with high structural weight.
6. Segmentation ControlNet with medium/high structural weight.
7. IP-Adapter/reference conditioning for design/object references.
8. Masked inpainting or constrained img2img.
9. Source-protected-region composite.
10. Validation pass.

For strict edits, prefer stronger structural controls and lower denoise than for full restyles.

## Dimension handling

When the user supplies dimensions:

- Convert all dimensions to a common unit.
- Identify at least one scale anchor: known wall length, door width, floorplan dimension, or another stated object dimension.
- Estimate image-plane placement using perspective rather than raw pixel ratios alone.
- If an exact metric placement cannot be guaranteed from a single photograph, prioritize visual scale consistency and state the limitation only when it materially affects the requested result.

## Validation gate

Before accepting an output, compare it against `room_source` and the instruction.

Reject/regenerate if any of these occur:

- wall/window/door/ceiling geometry changed without permission
- camera angle or perspective materially changed
- protected furniture disappeared, moved or changed identity
- requested furniture is on the wrong wall, wrong orientation or obviously wrong scale
- material edit leaks outside its target surface
- a multi-angle output uses a different design scheme
- sofa cushions/covers or other explicitly requested details are missing
- output is a collage when separate files were requested

## User-language interpretation

Treat phrases such as these as hard constraints:

- “其他什么都别动” = strict_edit; everything except named target is protected.
- “不要乱动墙体和格局” = architecture lock at maximum strength.
- “按这张的装饰输出到后面的图” = first image is design reference; later images remain their own geometry sources.
- “分别输出/不要合并” = one result per source image.
- “只要旋转90度” = rotation is the sole permitted semantic change.

## Failure recovery

If a generated result violates constraints, do not compound the error by editing the bad render repeatedly. Return to the original `room_source`, retain only approved design references, tighten the mask/control strength, and regenerate.
