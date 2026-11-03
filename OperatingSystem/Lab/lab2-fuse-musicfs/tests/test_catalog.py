import json
import os
from pathlib import Path
import tempfile
import unittest

from musicfs.catalog import Catalog, bpm_group
from tools.make_demo import make_demo


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "audio"
        self.root.mkdir()
        (self.root / "loop.wav").write_bytes(b"audio fixture")
        self.metadata = self.base / "metadata.json"

    def load(self, records):
        self.metadata.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
        return Catalog(self.metadata, self.root)

    def record(self, **changes):
        return dict(id="a", path="loop.wav", bpm=124.5, key="A_minor", type="drum", **changes)

    def test_bpm_rounding_and_unknown(self):
        for value, expected in [(None, "unknown"), (90, "90"), (124.5, "120"),
                                (125, "130"), (128, "130"), (134.999, "130"), (135, "140")]:
            with self.subTest(value=value):
                self.assertEqual(bpm_group(value), expected)

    def test_bad_bpm(self):
        for value in [True, False, 0, -1, "120", float("nan"), float("inf"), 1e100]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                bpm_group(value)

    def test_aliases_share_inode(self):
        catalog = self.load([self.record()])
        inodes = []
        for category, group in [(b"by_bpm", b"120"), (b"by_key", b"A_minor"), (b"by_type", b"drum")]:
            parent = catalog.nodes[catalog.nodes[1].children[category]]
            directory = catalog.nodes[parent.children[group]]
            inodes.append(directory.children[b"a__loop.wav"])
        self.assertEqual(len(set(inodes)), 1)
        self.assertEqual(catalog.nodes[inodes[0]].links, 3)
        self.assertEqual(catalog.file_count, 1)

    def test_missing_categories_are_unknown(self):
        catalog = self.load([{"id": "a", "path": "loop.wav"}])
        for inode in catalog.nodes[1].children.values():
            self.assertEqual(list(catalog.nodes[inode].children), [b"unknown"])

    def test_same_basename_is_not_overwritten(self):
        (self.root / "other").mkdir()
        (self.root / "other/loop.wav").write_bytes(b"different bytes")
        second = dict(self.record(), id="b", path="other/loop.wav")
        catalog = self.load([self.record(), second])
        category = catalog.nodes[catalog.nodes[1].children[b"by_type"]]
        directory = catalog.nodes[category.children[b"drum"]]
        self.assertEqual(set(directory.children), {b"a__loop.wav", b"b__loop.wav"})

    def test_missing_source_is_skipped(self):
        with self.assertLogs(level="WARNING"):
            catalog = self.load([dict(self.record(), path="missing.wav")])
        self.assertEqual(catalog.file_count, 0)
        self.assertEqual(catalog.nodes[1].children, {})
        self.assertEqual(len(catalog.warnings), 1)

    def test_invalid_records(self):
        for record in [None, {}, dict(self.record(), id="../bad"),
                       dict(self.record(), path="../outside.wav"),
                       dict(self.record(), path="/etc/passwd"),
                       dict(self.record(), path="a\\b.wav"),
                       dict(self.record(), key="../A"),
                       dict(self.record(), type=""), dict(self.record(), type=5),
                       dict(self.record(), path="."),
                       dict(self.record(), id="x" * 65)]:
            with self.subTest(record=record), self.assertRaises(ValueError):
                self.load([record])

    def test_duplicates_are_rejected(self):
        for records in [[self.record(), self.record()],
                        [self.record(), dict(self.record(), id="b")]]:
            with self.subTest(records=records), self.assertRaises(ValueError):
                self.load(records)

    @unittest.skipIf(os.name == "nt", "Linux symlink/hardlink semantics")
    def test_links_cannot_escape_or_duplicate_sources(self):
        outside = self.base / "outside.wav"
        outside.write_bytes(b"outside")
        (self.root / "escape.wav").symlink_to(outside)
        with self.assertRaises(ValueError):
            self.load([dict(self.record(), path="escape.wav")])
        os.link(self.root / "loop.wav", self.root / "hard.wav")
        with self.assertRaises(ValueError):
            self.load([self.record(), dict(self.record(), id="b", path="hard.wav")])

    def test_bad_json_and_top_level(self):
        self.metadata.write_text("{broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            Catalog(self.metadata, self.root)
        with self.assertRaises(ValueError):
            self.load({"files": []})

    def test_valid_synthetic_wav_and_no_overwrite(self):
        import wave
        output = self.base / "demo"
        records = make_demo(output)
        for record in records:
            with wave.open(str(output / "audio" / record["path"]), "rb") as stream:
                self.assertEqual(stream.getnframes(), 22050)
        self.assertEqual(Catalog(output / "metadata.json", output / "audio").file_count, 3)
        with self.assertRaises(ValueError):
            make_demo(output)


if __name__ == "__main__":
    unittest.main()
