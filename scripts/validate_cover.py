#!/usr/bin/env python3
"""Validate final PNG dimensions and exact delivery filename."""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path


TARGETS = {"9:16": (1080, 1920, "9-16"), "16:9": (1920, 1080, "16-9")}


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("file is not a valid PNG")
    return struct.unpack(">II", header[16:24])


def verify_png(path: Path) -> None:
    """Stream structural/CRC validation; visual acceptance remains a separate gate."""
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError("invalid PNG signature")
        seen_header = seen_data = False
        while True:
            header = handle.read(8)
            if len(header) != 8:
                raise ValueError("truncated PNG / missing IEND")
            size, kind = struct.unpack(">I4s", header)
            if not seen_header:
                if kind != b"IHDR" or size != 13:
                    raise ValueError("invalid first IHDR chunk")
                seen_header = True
            crc = zlib.crc32(kind)
            remaining = size
            while remaining:
                block = handle.read(min(remaining, 65536))
                if not block:
                    raise ValueError("truncated PNG chunk")
                crc = zlib.crc32(block, crc)
                remaining -= len(block)
            stored = handle.read(4)
            if len(stored) != 4 or struct.unpack(">I", stored)[0] != crc & 0xffffffff:
                raise ValueError("PNG CRC mismatch")
            seen_data |= kind == b"IDAT"
            if kind == b"IEND":
                if size or not seen_data or handle.read(1):
                    raise ValueError("invalid PNG ending")
                return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--ratio", required=True, choices=TARGETS)
    args = parser.parse_args()

    path = args.file.expanduser().resolve()
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"missing file: {path}")
    elif path.stat().st_size == 0:
        errors.append("file is empty")

    width = height = 0
    if not errors:
        try:
            width, height = png_dimensions(path)
            verify_png(path)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))

    target_width, target_height, suffix = TARGETS[args.ratio]
    expected_name = f"{args.title} {suffix}.png"
    if path.name != expected_name:
        errors.append(f"filename mismatch: expected {expected_name!r}, got {path.name!r}")
    if (width, height) != (target_width, target_height):
        errors.append(
            f"dimension mismatch: expected {target_width}x{target_height}, got {width}x{height}"
        )

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {path.name} — {width}x{height} PNG")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
