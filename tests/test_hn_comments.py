import csv
import os
import tempfile
import unittest
import urllib.error

import _paths  # noqa: F401
import hn_comments as tool


def hit(object_id, text, created="2026-08-01T12:00:00.000Z"):
    return {"objectID": str(object_id), "created_at": created, "comment_text": text, "author": "a"}


class BuildUrlTest(unittest.TestCase):
    def test_url_has_query_tags_and_paging(self):
        url = tool.build_url("my app", page=2)
        self.assertTrue(url.startswith("https://hn.algolia.com/api/v1/search?"))
        self.assertIn("query=my+app", url)
        self.assertIn("tags=comment", url)
        self.assertIn("page=2", url)
        self.assertIn("hitsPerPage=100", url)


class CleanTextTest(unittest.TestCase):
    def test_strips_tags_and_entities(self):
        self.assertEqual(tool.clean_text("<p>Too <i>slow</i> &amp; it&#x27;s broken</p>"), "Too slow & it's broken")

    def test_empty(self):
        self.assertEqual(tool.clean_text(None), "")
        self.assertEqual(tool.clean_text(""), "")


class ParseHitsTest(unittest.TestCase):
    def test_rows_link_to_exact_comment_and_have_blank_rating(self):
        rows = tool.parse_hits({"hits": [hit(42, "<p>sync is broken</p>")], "nbPages": 1})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source"], "hackernews")
        self.assertEqual(rows[0]["url"], "https://news.ycombinator.com/item?id=42")
        self.assertEqual(rows[0]["date"], "2026-08-01")
        self.assertEqual(rows[0]["rating"], "")
        self.assertEqual(rows[0]["text"], "sync is broken")

    def test_skips_empty_comments(self):
        rows = tool.parse_hits({"hits": [hit(1, ""), hit(2, None), hit(3, "ok")]})
        self.assertEqual([r["url"] for r in rows], ["https://news.ycombinator.com/item?id=3"])

    def test_bad_shapes(self):
        self.assertEqual(tool.parse_hits({}), [])
        self.assertEqual(tool.parse_hits([]), [])


class CollectTest(unittest.TestCase):
    def test_respects_nb_pages(self):
        calls = []

        def fake_fetch(url):
            calls.append(url)
            page = int(url.split("page=")[1].split("&")[0])
            return {"hits": [hit(page, "comment {}".format(page))], "nbPages": 2}

        rows = tool.collect("x", pages=5, fetch=fake_fetch, pause=0)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(calls), 2)

    def test_network_error_stops_quietly(self):
        def fake_fetch(url):
            raise urllib.error.URLError("offline")

        self.assertEqual(tool.collect("x", pages=3, fetch=fake_fetch, pause=0), [])


class WriteTest(unittest.TestCase):
    def test_csv_columns(self):
        rows = tool.parse_hits({"hits": [hit(1, "a"), hit(2, "b")]})
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "hn.csv")
            tool.write_csv(rows, path)
            with open(path, newline="", encoding="utf-8") as handle:
                data = list(csv.DictReader(handle))
        self.assertEqual(list(data[0].keys()), ["source", "url", "date", "rating", "text"])
        self.assertEqual(len(data), 2)

    def test_summary_wording(self):
        self.assertIn("0 comments", tool.summarise([], "x"))
        self.assertIn("not reviews", tool.summarise([{"text": "a"}], "x"))


if __name__ == "__main__":
    unittest.main()
