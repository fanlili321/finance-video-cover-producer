#!/usr/bin/env python3
"""Initialize, accept, audit and ZIP only this job's individually reviewed covers."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import os
import zipfile

from validate_cover import TARGETS, png_dimensions, verify_png


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            result.update(block)
    return result.hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    os.replace(temp, path)


def load(path):
    job = json.loads(path.read_text(encoding="utf-8"))
    if job.get("schema_version") != 1:
        raise ValueError("unsupported manifest version")
    expected = {(title, ratio) for title in job["titles"] for ratio in job["ratios"]}
    actual = [(item["title"], item["ratio"]) for item in job["items"]]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("manifest items do not exactly cover title × ratio")
    return job


def technical(path, title, ratio):
    width, height, suffix = TARGETS[ratio]
    if path.name != f"{title} {suffix}.png":
        raise ValueError(f"incorrect delivery name: {path.name}")
    if png_dimensions(path) != (width, height):
        raise ValueError(f"incorrect dimensions: {path.name}")
    verify_png(path)


def audit(job, root):
    errors, allowed = [], []
    for item in job["items"]:
        try:
            if item.get("status") != "accepted" or item.get("visual_pass") is not True:
                raise ValueError("pending / not visually accepted")
            relative = Path(item["file"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("unsafe relative file path")
            path = (root / relative).resolve()
            if not path.is_relative_to(root):
                raise ValueError("file outside job directory")
            technical(path, item["title"], item["ratio"])
            if path.stat().st_size != item["size"] or digest(path) != item["sha256"]:
                raise ValueError("file changed since visual acceptance; review again")
            allowed.append({"title": item["title"], "ratio": item["ratio"], "file": str(path), "name": path.name, "size": item["size"], "sha256": item["sha256"]})
        except (ValueError, KeyError, OSError) as exc:
            errors.append(f"{item['title']} [{item['ratio']}]: {exc}")
    return errors, allowed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "accept", "check", "zip"):
        command = sub.add_parser(name)
        command.add_argument("--manifest", type=Path, required=True)
        if name == "init":
            command.add_argument("--titles", type=Path, required=True)
            command.add_argument("--ratios", nargs="+", choices=TARGETS, default=["9:16", "4:3", "16:9"])
        elif name == "accept":
            command.add_argument("--title", required=True)
            command.add_argument("--ratio", choices=TARGETS, required=True)
            command.add_argument("--file", type=Path, required=True)
            command.add_argument("--visual-pass", action="store_true", required=True)
        elif name == "zip":
            command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = args.manifest.expanduser().resolve()
    try:
        if args.command == "init":
            if manifest.exists():
                raise ValueError("manifest already exists; resume it instead of overwriting")
            raw = json.loads(args.titles.read_text(encoding="utf-8"))
            raw = raw["selected"] if isinstance(raw, dict) else raw
            titles = [item["title"] if isinstance(item, dict) else item for item in raw]
            if not titles or any(not isinstance(title, str) or not title.strip() or "/" in title or "\\" in title or any(ord(char) < 32 for char in title) for title in titles):
                raise ValueError("titles must be non-empty single-line filename-safe exact text")
            if len(titles) != len(set(titles)) or len(args.ratios) != len(set(args.ratios)):
                raise ValueError("duplicate titles/ratios: resolve explicitly first")
            job = {"schema_version": 1, "titles": titles, "ratios": args.ratios, "items": [{"title": title, "ratio": ratio, "status": "pending"} for title in titles for ratio in args.ratios]}
            save(manifest, job)
            print(f"Initialized {len(job['items'])} pending covers")
            return 0
        job = load(manifest)
        if args.command == "accept":
            path = args.file.expanduser().resolve()
            if not path.is_relative_to(manifest.parent):
                raise ValueError("delivery file must be inside the job directory")
            item = next((item for item in job["items"] if item["title"] == args.title and item["ratio"] == args.ratio), None)
            if item is None:
                raise ValueError("title/ratio is not part of this job")
            technical(path, args.title, args.ratio)
            new_size, new_hash = path.stat().st_size, digest(path)
            if item.get("status") == "accepted" and item.get("visual_pass") is True:
                old_path = (manifest.parent / item.get("file", "")).resolve()
                if (old_path.is_relative_to(manifest.parent) and old_path.is_file()
                        and old_path.stat().st_size == item.get("size")
                        and digest(old_path) == item.get("sha256")
                        and old_path == path and new_size == item.get("size")
                        and new_hash == item.get("sha256")):
                    raise ValueError("already accepted and unchanged; refusing duplicate acceptance")
            item.update(status="accepted", visual_pass=True, file=str(path.relative_to(manifest.parent)), size=path.stat().st_size, sha256=digest(path), accepted_at=datetime.now(timezone.utc).isoformat())
            save(manifest, job)
            print(f"Accepted: {path.name}")
            return 0
        errors, allowed = audit(job, manifest.parent)
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
            return 1
        if args.command == "zip":
            output = args.output.expanduser().resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_STORED) as archive:
                for item in allowed:
                    archive.write(item["file"], arcname=item["name"])
            print(output)
        else:
            print(json.dumps({"ok": True, "count": len(allowed), "upload_allowlist": allowed}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
