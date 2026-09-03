#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMFY_DIR="${COMFYUI_DIR:-$HOME/ComfyUI}"
CUSTOM_DIR="$COMFY_DIR/custom_nodes"

if [ ! -d "$COMFY_DIR" ]; then
  echo "ComfyUI directory not found at $COMFY_DIR"
  echo "Set COMFYUI_DIR=/path/to/ComfyUI and run again."
  exit 1
fi

mkdir -p "$CUSTOM_DIR"

clone_or_update() {
  local url="$1"
  local name="$2"
  local dest="$CUSTOM_DIR/$name"
  if [ -d "$dest/.git" ]; then
    echo "Updating $name"
    git -C "$dest" pull --ff-only || true
  else
    echo "Installing $name"
    git clone "$url" "$dest"
  fi
}

clone_or_update "https://github.com/RodrigoSKohl/InteriorDesign-for-ComfyUI.git" "InteriorDesign-for-ComfyUI"
clone_or_update "https://github.com/kijai/ComfyUI-DepthAnythingV2.git" "ComfyUI-DepthAnythingV2"
clone_or_update "https://github.com/evanspearman/ComfyMath.git" "ComfyMath"

# Upstream currently relies on ComfyUI_IPAdapter_plus. Keep it optional and explicit
# because upstream notes that it is unmaintained.
if [ "${INSTALL_LEGACY_IPADAPTER:-0}" = "1" ]; then
  clone_or_update "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git" "ComfyUI_IPAdapter_plus"
else
  echo "Skipping legacy ComfyUI_IPAdapter_plus by default."
  echo "Set INSTALL_LEGACY_IPADAPTER=1 only if you accept the pinned legacy dependency."
fi

python3 -m pip install -r "$ROOT_DIR/requirements.txt"

if [ -f "$CUSTOM_DIR/InteriorDesign-for-ComfyUI/requirements.txt" ]; then
  python3 -m pip install -r "$CUSTOM_DIR/InteriorDesign-for-ComfyUI/requirements.txt"
fi
if [ -f "$CUSTOM_DIR/ComfyUI-DepthAnythingV2/requirements.txt" ]; then
  python3 -m pip install -r "$CUSTOM_DIR/ComfyUI-DepthAnythingV2/requirements.txt"
fi

echo
echo "RealRoom code and custom nodes are installed."
echo "Model weights are NOT downloaded automatically."
echo "Follow docs/MODELS.md, then restart ComfyUI."
