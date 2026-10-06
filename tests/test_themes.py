import contextlib
import csv
import datetime
import io
import os
import tempfile
import unittest

import _paths  # noqa: F401
import themes as tool

TODAY = datetime.date(2026, 10, 7)


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "url", "date", "rating", "text"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def row(source, url, date, rating, text):
    return {"source": source, "url": url, "date": date, "rating": rating, "text": text}


class PresetTest(unittest.TestCase):
    def test_shipped_presets_load(self):
        presets = tool.load_presets()
        for name in ("general", "video", "scheduling", "notes", "finance"):
            self.assertIn(name, presets)

    def test_pick_merges_general_with_chosen(self):
        presets = {"general": {"price": ["expensive"]}, "video": {"export": ["blurry"]}}
        themes = tool.pick_themes(presets, "video")
        self.assertEqual(set(themes), {"price", "export"})

    def test_unknown_preset_raises(self):
        with self.assertRaises(KeyError):
            tool.pick_themes({"general": {}}, "nope")


class WeightTest(unittest.TestCase):
    def test_low_ratings_weigh_more(self):
        self.assertGreater(tool.rating_weight("1"), tool.rating_weight("5"))
        self.assertEqual(tool.rating_weight(""), 1.0)
        self.assertEqual(tool.rating_weight("junk"), 1.0)

    def test_recent_dates_weigh_more(self):
        self.assertEqual(tool.recency_weight("2026-09-20", TODAY), 1.5)
        self.assertEqual(tool.recency_weight("2026-01-01", TODAY), 1.2)
        self.assertEqual(tool.recency_weight("2020-01-01", TODAY), 1.0)
        self.assertEqual(tool.recency_weight("", TODAY), 1.0)
        self.assertEqual(tool.recency_weight("not a date", TODAY), 1.0)


class GroupTest(unittest.TestCase):
    def setUp(self):
        self.compiled = tool.compile_themes({"export": ["export", "blurry"], "price": ["expensive", "price"]})

    def test_whole_word_matching(self):
        rows = [row("appstore", "u", "2026-09-01", "3", "the exporter is fine")]
        self.assertEqual(tool.group(rows, self.compiled, TODAY), [])

    def test_ranking_and_thin_flag(self):
        rows = [
            row("appstore", "u1", "2026-09-20", "1", "export failed"),
            row("appstore", "u2", "2026-09-01", "2", "blurry export"),
            row("hackernews", "u3", "2026-08-01", "", "export is bad"),
            row("appstore", "u4", "2020-01-01", "5", "love the price"),
        ]
        results = tool.group(rows, self.compiled, TODAY)
        self.assertEqual(results[0]["theme"], "export")
        self.assertEqual(results[0]["count"], 3)
        self.assertFalse(results[0]["thin"])
        self.assertEqual(results[1]["theme"], "price")
        self.assertTrue(results[1]["thin"])
        self.assertAlmostEqual(results[1]["weight"], 0.6)

    def test_single_source_is_thin_even_with_many_reviews(self):
        rows = [row("appstore", "u{}".format(i), "2026-09-01", "1", "export broke") for i in range(5)]
        results = tool.group(rows, self.compiled, TODAY)
        self.assertTrue(results[0]["thin"])


class RenderAndMainTest(unittest.TestCase):
    def test_flags_identical_urls_and_exits_zero(self):
        same = "https://apps.apple.com/x"
        rows = [row("appstore", same, "2026-09-01", "1", "export broke"), row("appstore", same, "2026-09-02", "2", "export broke again")]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "r.csv")
            write_rows(path, rows)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = tool.main([path, "--preset", "video", "--today", "2026-10-07"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("every row has the same URL", text)
        self.assertIn("Sample: 2 reviews", text)
        self.assertIn("thin", text)

    def test_empty_csv_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "empty.csv")
            write_rows(path, [])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = tool.main([path])
        self.assertEqual(code, 0)
        self.assertIn("No theme matched", out.getvalue())

    def test_missing_file_is_nonzero(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = tool.main(["/no/such/file.csv"])
        self.assertEqual(code, 1)

    def test_quotes_are_truncated(self):
        long_text = "export " + ("x" * 300)
        rows = [row("appstore", "u", "2026-09-01", "1", long_text)]
        compiled = tool.compile_themes({"export": ["export"]})
        text = tool.render(tool.group(rows, compiled, TODAY), rows, top=1, quotes=1)
        self.assertIn("...", text)
        self.assertNotIn("x" * 250, text)


if __name__ == "__main__":
    unittest.main()
