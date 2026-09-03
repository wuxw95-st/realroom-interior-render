#!/usr/bin/env python3
import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path

import requests
import yaml

HARD_NEGATIVE = (
    "changed architecture, moved wall, new wall, changed window, changed door, "
    "altered room proportions, different camera angle, different viewpoint, mirrored room, "
    "warped perspective, duplicated furniture, missing existing furniture, floating furniture, "
    "incorrect scale, material leakage, surreal, CGI look, text, watermark"
)

POSITIVE_SUFFIX = (
    "photorealistic interior photography, physically plausible materials, consistent perspective, "
    "preserve original room geometry, preserve original camera viewpoint, preserve all unrequested objects"
)


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_request(req):
    mode = req.get("mode")
    allowed = {"strict_edit", "material_replace", "furniture_place", "full_restyle"}
    if mode not in allowed:
        raise ValueError(f"mode must be one of {sorted(allowed)}")
    inputs = req.get("inputs") or {}
    if not inputs.get("room_source"):
        raise ValueError("inputs.room_source is required")
    out = req.get("output") or {}
    if out.get("one_image_per_source") is False:
        raise ValueError("RealRoom v1 requires one image per source by default")


def build_generation_spec(req, defaults):
    ensure_request(req)
    mode = req["mode"]
    controls = defaults["controls"]
    sampling = defaults["sampling"]
    instruction = req.get("instruction", "").strip()
    positive = ", ".join([x for x in [instruction, POSITIVE_SUFFIX] if x])
    negative = HARD_NEGATIVE
    return {
        "mode": mode,
        "room_source": req["inputs"]["room_source"],
        "design_reference": req["inputs"].get("design_reference"),
        "object_references": req["inputs"].get("object_references", []),
        "constraints": req.get("constraints", {}),
        "prompt": {"positive": positive, "negative": negative},
        "controls": {
            "depth_strength": controls["depth"]["strength"][mode],
            "segmentation_strength": controls["segmentation"]["strength"][mode],
            "reference_region_only": controls["reference_adapter"]["apply_to_edit_region_only"],
            "denoise": sampling["denoise"][mode],
        },
        "validation": defaults["validation"],
        "output": req.get("output", {"one_image_per_source": True, "no_collage": True}),
    }


def patch_workflow(template, spec):
    wf = copy.deepcopy(template)
    bindings = wf.get("realroom_bindings", {})
    payload = wf.get("prompt", wf)

    def set_input(binding_name, value):
        b = bindings.get(binding_name)
        if not b:
            return
        node_id = str(b["node_id"])
        input_name = b["input"]
        if node_id not in payload:
            raise KeyError(f"workflow binding node {node_id} missing for {binding_name}")
        payload[node_id].setdefault("inputs", {})[input_name] = value

    set_input("positive_prompt", spec["prompt"]["positive"])
    set_input("negative_prompt", spec["prompt"]["negative"])
    set_input("depth_strength", spec["controls"]["depth_strength"])
    set_input("segmentation_strength", spec["controls"]["segmentation_strength"])
    set_input("denoise", spec["controls"]["denoise"])
    set_input("room_source", spec["room_source"])
    return payload


def queue_comfy(server, prompt):
    r = requests.post(f"{server.rstrip('/')}/prompt", json={"prompt": prompt}, timeout=30)
    r.raise_for_status()
    return r.json()["prompt_id"]


def wait_history(server, prompt_id, timeout=900):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f"{server.rstrip('/')}/history/{prompt_id}", timeout=30)
        r.raise_for_status()
        data = r.json()
        if prompt_id in data:
            return data[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"ComfyUI prompt timed out after {timeout}s")


def main():
    p = argparse.ArgumentParser(description="RealRoom Interior Render runner")
    p.add_argument("request", type=Path, help="YAML request file")
    p.add_argument("--defaults", type=Path, default=Path("config/defaults.yaml"))
    p.add_argument("--workflow", type=Path, help="ComfyUI API workflow JSON with realroom_bindings")
    p.add_argument("--server", default=os.getenv("COMFYUI_URL", "http://127.0.0.1:8188"))
    p.add_argument("--dry-run", action="store_true", help="print normalized generation spec only")
    args = p.parse_args()

    req = load_yaml(args.request)
    defaults = load_yaml(args.defaults)
    spec = build_generation_spec(req, defaults)

    if args.dry_run:
        print(json.dumps(spec, ensure_ascii=False, indent=2))
        return 0

    if not args.workflow:
        print("ERROR: --workflow is required unless --dry-run is used", file=sys.stderr)
        return 2

    with args.workflow.open("r", encoding="utf-8") as f:
        template = json.load(f)
    prompt = patch_workflow(template, spec)
    prompt_id = queue_comfy(args.server, prompt)
    history = wait_history(args.server, prompt_id)
    print(json.dumps({"prompt_id": prompt_id, "history": history}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
