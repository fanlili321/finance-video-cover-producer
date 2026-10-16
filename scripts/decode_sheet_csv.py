#!/usr/bin/env python3
"""Decode a complete lark-cli +csv-get JSON stdout snapshot, preserving real rows."""
import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path


def decode(envelope):
    if envelope.get("ok") is not True or envelope.get("identity") != "user":
        raise ValueError("expected a successful user-identity CLI envelope")
    data = envelope["data"]
    if data.get("has_more") or data.get("truncated"):
        raise ValueError("range is truncated; read smaller/remaining windows first")
    stream = io.StringIO(data["annotated_csv"], newline="")
    rows = []
    while True:
        first = stream.readline()
        if not first:
            break
        match = re.match(r"^\[row=(\d+)\] ?", first)
        if not match:
            raise ValueError("missing real-row prefix at logical record start")
        def lines():
            yield first[match.end():]
            while True:
                following = stream.readline()
                if not following:
                    return
                yield following
        cells = next(csv.reader(lines(), strict=True))
        # lark-cli represents an entirely blank row as an empty CSV record.
        # Preserve the requested rectangular range by padding that row to its
        # declared width instead of rejecting an otherwise complete snapshot.
        if not cells and data.get("col_indices"):
            cells = [""] * len(data["col_indices"])
        rows.append({"row": int(match.group(1)), "cells": cells})
    indices = data.get("row_indices")
    if indices is not None and indices != [item["row"] for item in rows]:
        raise ValueError("row_indices and logical CSV row prefixes disagree")
    if len({item["row"] for item in rows}) != len(rows):
        raise ValueError("duplicate real-row prefixes")
    columns = data.get("col_indices", [])
    if columns and any(len(item["cells"]) != len(columns) for item in rows):
        raise ValueError("column count does not match col_indices")
    return {"warning_message": data.get("warning_message"), "actual_range": data.get("actual_range"), "columns": columns, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        result = decode(json.loads(args.snapshot.read_text(encoding="utf-8")))
    except (ValueError, KeyError, OSError, csv.Error) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
