# ComfyUI backend plan

## Base workflow

Start from `RodrigoSKohl/InteriorDesign-for-ComfyUI`, which provides an interior-design pipeline using semantic segmentation, Depth Anything V2, ControlNet and IP-Adapter-style reference conditioning.

Do not treat the upstream workflow as sufficient for strict real-room editing by itself. RealRoom adds a preservation layer around it.

## RealRoom extensions

### A. Protected-region mask

Create two masks:

- `EDIT_MASK`: only pixels/regions explicitly authorized for change.
- `PROTECT_MASK`: inverse of edit mask, including architecture and all unrequested objects.

For strict edits, generation must be confined to `EDIT_MASK`. Composite the protected source region back after generation when possible.

### B. Geometry lock

Generate depth from the original room photo, not from a previous render. Feed the original-source depth map to ControlNet at high strength.

Generate semantic segmentation from the original room photo. Use it to preserve wall/floor/window/door boundaries.

### C. Reference object/style

If a furniture or design reference is provided, use reference-image conditioning only on the relevant edit region. Do not allow the reference image's architecture or camera composition to influence the room geometry.

The upstream repository currently references `ComfyUI_IPAdapter_plus`, which its own documentation notes is unmaintained. For a production setup, use a maintained compatible reference-conditioning implementation where available; otherwise pin a known working version rather than silently upgrading.

### D. Local edit path

For commands such as “only rotate the bed 90 degrees” or “add cushions”, use an inpainting/local-edit path rather than full-frame regeneration.

Suggested flow:

`Load source -> Depth -> Segmentation -> Edit mask -> Reference conditioning (optional) -> ControlNet depth/seg -> Inpaint sampler -> Composite protected pixels -> Validate -> Save`

### E. Multi-angle path

Each camera angle is processed independently from its own original photograph. Feed the same approved design reference and same material/object settings to each run. Never use one rendered angle as the geometry source for another angle.

## Model assets

The upstream workflow documents custom depth and segmentation ControlNet weights originating from the StableDesign pipeline, plus Depth Anything V2 and IP-Adapter/CLIP vision assets. Follow upstream model licenses and download instructions. Model weights are intentionally not committed to this repository.

## Validation

A successful render must pass the checklist in `SKILL.md`. Structural fidelity outranks aesthetics. If validation fails, restart from the original source photo with a tighter mask or stronger structural control.
