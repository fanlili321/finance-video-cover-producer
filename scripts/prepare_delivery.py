#!/usr/bin/env python3
"""Center-crop, resize and name a generated cover for delivery."""

from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path


TARGETS = {"9:16": (1080, 1920, "9-16"), "16:9": (1920, 1080, "16-9")}


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("source is not a valid PNG")
    return struct.unpack(">II", header[16:24])


def resize_with_pillow(source: Path, destination: Path, target: tuple[int, int]) -> bool:
    try:
        from PIL import Image
    except ImportError:
        return False
    target_width, target_height = target
    with Image.open(source) as image:
        image = image.convert("RGBA")
        source_width, source_height = image.size
        target_ratio = target_width / target_height
        source_ratio = source_width / source_height
        if source_ratio > target_ratio:
            crop_width = round(source_height * target_ratio)
            left = (source_width - crop_width) // 2
            box = (left, 0, left + crop_width, source_height)
        else:
            crop_height = round(source_width / target_ratio)
            top = (source_height - crop_height) // 2
            box = (0, top, source_width, top + crop_height)
        image = image.crop(box).resize((target_width, target_height), Image.Resampling.LANCZOS)
        image.save(destination, format="PNG", optimize=False)
    return True


def resize_with_sips(source: Path, destination: Path, target: tuple[int, int]) -> bool:
    sips = shutil.which("sips")
    if not sips:
        return False
    source_width, source_height = png_dimensions(source)
    target_width, target_height = target
    target_ratio = target_width / target_height
    source_ratio = source_width / source_height
    if source_ratio > target_ratio:
        crop_width, crop_height = round(source_height * target_ratio), source_height
    else:
        crop_width, crop_height = source_width, round(source_width / target_ratio)
    with tempfile.TemporaryDirectory(prefix="cover-delivery-") as temp_dir:
        cropped = Path(temp_dir) / "cropped.png"
        subprocess.run(
            [sips, "-c", str(crop_height), str(crop_width), str(source), "--out", str(cropped)],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [sips, "-z", str(target_height), str(target_width), str(cropped), "--out", str(destination)],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--ratio", required=True, choices=TARGETS)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not source.is_file():
        print(f"FAIL: missing source: {source}", file=sys.stderr)
        return 1
    if source.suffix.lower() != ".png":
        print("FAIL: source must be a PNG", file=sys.stderr)
        return 1

    title = unicodedata.normalize("NFC", args.title).strip()
    if not title or "/" in title or "\\" in title:
        print("FAIL: title is empty or contains a path separator", file=sys.stderr)
        return 1

    target_width, target_height, suffix = TARGETS[args.ratio]
    try:
        source_width, source_height = png_dimensions(source)
    except (ValueError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    source_ratio = source_width / source_height if source_height else 0
    target_ratio = target_width / target_height
    if source_ratio <= 0 or abs(source_ratio / target_ratio - 1) > 0.10:
        print("FAIL: source orientation/aspect ratio differs from target; check the source mapping or regenerate, do not force-crop.", file=sys.stderr)
        return 1
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{title} {suffix}.png"
    if destination.exists():
        print(f"REFUSED: delivery exists: {destination}; keep it or use a new reviewed output directory.", file=sys.stderr)
        return 1

    if (source_width, source_height) == (target_width, target_height):
        shutil.copy2(source, destination)
        print(destination)
        return 0

    if not resize_with_pillow(source, destination, (target_width, target_height)):
        if not resize_with_sips(source, destination, (target_width, target_height)):
            print("FAIL: install Pillow or run on macOS with sips available", file=sys.stderr)
            return 1

    width, height = png_dimensions(destination)
    if (width, height) != (target_width, target_height):
        print(f"FAIL: produced {width}x{height}, expected {target_width}x{target_height}", file=sys.stderr)
        return 1
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
