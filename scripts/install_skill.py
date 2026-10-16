#!/usr/bin/env python3
"""Install this portable skill into the current user's Codex skills directory."""

from __future__ import annotations

import shutil
import sys
import argparse
import os
from datetime import datetime
from pathlib import Path


SKILL_NAME = "finance-video-cover-producer"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destination-root",
        type=Path,
        default=Path.home() / ".agents" / "skills",
        help="Skills directory; defaults to ~/.agents/skills",
    )
    parser.add_argument("--update", action="store_true", help="Move this skill's previous installation to a timestamped backup; never delete it")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    destination_root = args.destination_root.expanduser().resolve()
    destination = destination_root / SKILL_NAME
    if source == destination or source.is_relative_to(destination):
        print("REFUSED: run the installer from a separate unpacked package, not inside its installation.", file=sys.stderr)
        return 1
    backup = None
    if destination.exists():
        if not args.update:
            print(f"REFUSED: {destination} already exists; use --update for a recoverable backup.", file=sys.stderr)
            return 1
        if destination.is_symlink() or not (destination / "SKILL.md").is_file():
            print("REFUSED: target is a symlink or not an identifiable skill folder.", file=sys.stderr)
            return 1
        backup = destination_root / ".skill-backups" / f"{SKILL_NAME}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
        backup.parent.mkdir(parents=True, exist_ok=True)
        destination.rename(backup)
    destination_root.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    except Exception:
        print(f"Installation failed; previous version is preserved at {backup}", file=sys.stderr)
        raise
    if backup:
        print(f"Previous version preserved at {backup}")
    print(f"Installed {SKILL_NAME} at {destination}")
    print("Restart Codex, then invoke $finance-video-cover-producer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
