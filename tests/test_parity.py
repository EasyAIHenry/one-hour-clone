import contextlib
import csv
import io
import os
import tempfile
import unittest

import _paths  # noqa: F401
import parity as tool

COLUMNS = ["feature", "area", "priority", "original", "clone", "notes"]


def r(feature, area, priority, original, clone, notes=""):
    return dict(zip(COLUMNS, [feature, area, priority, original, clone, notes]))


MATRIX = [
    r("Record screen", "capture", "must", "yes", "yes"),
    r("Pick a window", "capture", "must", "yes", "partial", "whole screen only"),
    r("Trim clip", "edit", "should", "yes", "no"),
    r("Share link", "share", "must", "yes", "yes"),
    r("Team workspace", "share", "could", "yes", "skip", "needs their user network"),
    r("Push notification", "share", "could", "yes", "n/a", "browser does it"),
    r("Dark mode", "ui", "could", "yes", "yes"),
    r("AI summary", "edit", "should", "no", "no"),
]


class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.result = tool.score(MATRIX)

    def test_points_and_percent(self):
        # must yes 3 + must partial 1.5 + should no 0 + must yes 3 + could yes 1 = 8.5 of 3+3+2+3+1 = 12
        self.assertEqual(self.result["available"], 12)
        self.assertAlmostEqual(self.result["earned"], 8.5)
        self.assertEqual(self.result["percent"], 70)

    def test_excluded_rows_reported_not_scored(self):
        self.assertEqual([f for f, _ in self.result["skipped"]], ["Team workspace"])
        self.assertEqual([f for f, _ in self.result["not_applicable"]], ["Push notification"])
        self.assertEqual(self.result["original_lacks"], ["AI summary"])

    def test_must_haves_and_shippable(self):
        must = self.result["by_priority"]["must"]
        self.assertEqual((must["done"], must["partial"], must["total"]), (2, 1, 3))
        self.assertFalse(self.result["shippable"])

    def test_missing_list_in_build_order(self):
        names = [item["feature"] for item in self.result["missing"]]
        self.assertEqual(names, ["Pick a window", "Trim clip"])

    def test_weakest_area_first(self):
        self.assertEqual(self.result["areas"][0]["area"], "edit")
        self.assertEqual(self.result["areas"][0]["percent"], 0)

    def test_parity_line_verbatim(self):
        self.assertEqual(
            tool.parity_line(self.result),
            "PARITY 70% | must 2/3 | should 0/1 | could 1/1 | skipped 1 | n/a 1 | not shippable yet",
        )


class EdgeCaseTest(unittest.TestCase):
    def test_all_must_done_is_shippable(self):
        result = tool.score([r("A", "x", "must", "yes", "yes"), r("B", "x", "could", "yes", "no")])
        self.assertTrue(result["shippable"])
        self.assertIn("shippable slice", tool.parity_line(result))
        self.assertEqual(result["percent"], 75)

    def test_unknown_values_warn_and_default(self):
        result = tool.score([r("A", "x", "urgent", "yes", "maybe"), r("B", "x", "must", "yes", "yes")])
        self.assertEqual(len(result["warnings"]), 2)
        self.assertEqual(result["percent"], 75)  # must yes 3 of (3 + could 1)

    def test_no_must_rows_warns_and_is_not_shippable(self):
        result = tool.score([r("A", "x", "could", "yes", "yes")])
        self.assertFalse(result["shippable"])
        self.assertTrue(any("no must rows" in w for w in result["warnings"]))

    def test_empty_matrix(self):
        result = tool.score([])
        self.assertEqual(result["percent"], 0)
        self.assertFalse(result["shippable"])

    def test_case_and_whitespace_are_forgiven(self):
        result = tool.score([r("A", "x", " MUST ", "Yes", " yes "), r("B", "x", "Could", "yes", "N/A")])
        self.assertEqual(result["percent"], 100)
        self.assertEqual(len(result["not_applicable"]), 1)


class MainTest(unittest.TestCase):
    def test_reads_csv_and_prints_parity_line_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "features.csv")
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=COLUMNS)
                writer.writeheader()
                for row in MATRIX:
                    writer.writerow(row)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = tool.main([path])
        self.assertEqual(code, 0)
        lines = out.getvalue().strip().splitlines()
        self.assertTrue(lines[-1].startswith("PARITY 70%"))
        self.assertIn("Not shippable yet", out.getvalue())

    def test_missing_columns_fail_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("feature,clone\nA,yes\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = tool.main([path])
        self.assertEqual(code, 1)
        self.assertIn("missing columns", err.getvalue())


if __name__ == "__main__":
    unittest.main()
