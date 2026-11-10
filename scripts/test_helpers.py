#!/usr/bin/env python3
"""Small sequential offline tests: no image generation, no Feishu calls."""
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib

from decode_sheet_csv import decode
from validate_cover import verify_png

ROOT = Path(__file__).resolve().parents[1]


def write_test_png(path, width, height):
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
    row = b"\x00" + b"\xff\xff\xff" * width
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(row * height)) + chunk(b"IEND", b""))


class HelperTests(unittest.TestCase):
    def test_csv_multiline_real_rows(self):
        value = {"ok": True, "identity": "user", "data": {"annotated_csv": '[row=2] "标题1：第一行\n标题2：第二行"\n[row=5] "带,逗号"\n', "row_indices": [2, 5], "col_indices": ["A"]}}
        rows = decode(value)["rows"]
        self.assertEqual(rows[0]["cells"], ["标题1：第一行\n标题2：第二行"])
        self.assertEqual(rows[1], {"row": 5, "cells": ["带,逗号"]})

    def test_csv_rejects_partial_or_bot(self):
        for value in ({"ok": True, "identity": "bot", "data": {}}, {"ok": True, "identity": "user", "data": {"has_more": True}}):
            with self.assertRaises(ValueError):
                decode(value)

    def test_png_crc_corruption(self):
        with tempfile.TemporaryDirectory(prefix="cover-test-") as folder:
            file = Path(folder) / "corrupt.png"
            shutil.copy2(ROOT / "assets/example-cover-9-16.png", file)
            verify_png(file)
            with file.open("r+b") as stream:
                stream.seek(20)
                byte = stream.read(1)
                stream.seek(20)
                stream.write(bytes([byte[0] ^ 1]))
            with self.assertRaises(ValueError):
                verify_png(file)

    def test_wrong_orientation_rejected_without_output(self):
        with tempfile.TemporaryDirectory(prefix="cover-test-") as folder:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/prepare_delivery.py"), str(ROOT / "assets/example-cover-16-9.png"), "--title", "测试，标题", "--ratio", "9:16", "--output-dir", folder], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(list(Path(folder).glob("*.png")))

    def test_prepare_4_by_3_delivery(self):
        with tempfile.TemporaryDirectory(prefix="cover-test-") as folder:
            root = Path(folder)
            source = root / "source.png"
            write_test_png(source, 720, 540)
            result = subprocess.run([sys.executable, str(ROOT / "scripts/prepare_delivery.py"), str(source), "--title", "测试，标题", "--ratio", "4:3", "--output-dir", folder], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            file = root / "测试，标题 4-3.png"
            self.assertTrue(file.is_file())
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_cover.py"), str(file), "--title", "测试，标题", "--ratio", "4:3"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_manifest_pending_accept_hash_and_unicode_zip(self):
        with tempfile.TemporaryDirectory(prefix="cover-test-") as folder:
            root = Path(folder)
            titles = root / "titles.json"
            titles.write_text(json.dumps({"selected": [{"title": "测试，标题"}]}, ensure_ascii=False), encoding="utf-8")
            manifest = root / "manifest.json"
            def run(*args):
                return subprocess.run([sys.executable, str(ROOT / "scripts/delivery_manifest.py"), *map(str, args)], capture_output=True, text=True)
            self.assertEqual(run("init", "--manifest", manifest, "--titles", titles).returncode, 0)
            self.assertNotEqual(run("check", "--manifest", manifest).returncode, 0)
            for ratio, suffix in (("9:16", "9-16"), ("4:3", "4-3"), ("16:9", "16-9")):
                file = root / f"测试，标题 {suffix}.png"
                if ratio == "4:3":
                    write_test_png(file, 1440, 1080)
                else:
                    shutil.copy2(ROOT / f"assets/example-cover-{suffix}.png", file)
                self.assertEqual(run("accept", "--manifest", manifest, "--title", "测试，标题", "--ratio", ratio, "--file", file, "--visual-pass").returncode, 0)
            self.assertEqual(run("check", "--manifest", manifest).returncode, 0)
            archive = root / "covers.zip"
            self.assertEqual(run("zip", "--manifest", manifest, "--output", archive).returncode, 0)
            with zipfile.ZipFile(archive) as pack:
                self.assertEqual(set(pack.namelist()), {"测试，标题 9-16.png", "测试，标题 4-3.png", "测试，标题 16-9.png"})
                self.assertIsNone(pack.testzip())
            with (root / "测试，标题 9-16.png").open("ab") as stream:
                stream.write(b"changed")
            self.assertNotEqual(run("check", "--manifest", manifest).returncode, 0)


if __name__ == "__main__":
    unittest.main()
