#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def load_rgb(path: Path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0


def load_mask(path: Path, size):
    img = Image.open(path).convert("L").resize(size, Image.Resampling.NEAREST)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return arr >= 0.5


def main():
    p = argparse.ArgumentParser(description="Validate that protected pixels were not changed excessively")
    p.add_argument("source", type=Path)
    p.add_argument("render", type=Path)
    p.add_argument("protect_mask", type=Path, help="white=protected, black=editable")
    p.add_argument("--mean-threshold", type=float, default=0.035)
    p.add_argument("--p95-threshold", type=float, default=0.12)
    args = p.parse_args()

    src_img = Image.open(args.source).convert("RGB")
    out_img = Image.open(args.render).convert("RGB")
    if src_img.size != out_img.size:
        out_img = out_img.resize(src_img.size, Image.Resampling.LANCZOS)

    src = np.asarray(src_img, dtype=np.float32) / 255.0
    out = np.asarray(out_img, dtype=np.float32) / 255.0
    mask = load_mask(args.protect_mask, src_img.size)

    diff = np.mean(np.abs(src - out), axis=2)
    protected = diff[mask]
    if protected.size == 0:
        raise SystemExit("protect mask contains no protected pixels")

    mean_diff = float(protected.mean())
    p95_diff = float(np.percentile(protected, 95))
    passed = mean_diff <= args.mean_threshold and p95_diff <= args.p95_threshold

    print(f"protected_mean_diff={mean_diff:.5f}")
    print(f"protected_p95_diff={p95_diff:.5f}")
    print("PASS" if passed else "FAIL")
    raise SystemExit(0 if passed else 2)


if __name__ == "__main__":
    main()
