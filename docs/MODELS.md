# Model assets

RealRoom does not commit large model weights to GitHub. The backend follows the upstream `InteriorDesign-for-ComfyUI` model layout.

## Required categories

1. Base diffusion checkpoint compatible with the selected upstream workflow.
2. Depth Anything V2 model used by `ComfyUI-DepthAnythingV2`.
3. StableDesign depth ControlNet weights.
4. StableDesign segmentation ControlNet weights.
5. Reference-image conditioning assets when reference conditioning is enabled.
6. CLIP vision encoder required by the chosen reference adapter.

## Recommended folders

Inside your ComfyUI installation:

```text
ComfyUI/
  models/
    checkpoints/
    controlnet/
      depth/
      segmentation/
    clip_vision/
    ipadapter/
```

## Important compatibility note

The upstream workflow currently documents `ComfyUI_IPAdapter_plus` and explicitly notes that repository is unmaintained. RealRoom therefore does not auto-install it by default. If you intentionally choose the upstream legacy path, run the installer with:

```bash
INSTALL_LEGACY_IPADAPTER=1 bash scripts/install.sh
```

For a production deployment, prefer a maintained compatible reference-conditioning implementation and update the workflow bindings accordingly.

## Why models are not auto-downloaded

Large model files can be many gigabytes, may have different licenses, and upstream download locations can change. Keeping downloads explicit prevents silently accepting a model license or filling disk space unexpectedly.
