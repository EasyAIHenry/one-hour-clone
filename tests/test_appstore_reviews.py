import csv
import os
import tempfile
import unittest
import urllib.error

import _paths  # noqa: F401  (adds the tool folders to sys.path)
import appstore_reviews as tool

SAME_URL = "https://apps.apple.com/us/app/example/id1?see-all=reviews"


def entry(rating, title, body, date="2026-09-20T10:00:00-07:00", url=SAME_URL):
    return {
        "author": {"name": {"label": "someone"}},
        "updated": {"label": date},
        "im:rating": {"label": str(rating)},
        "title": {"label": title},
        "content": {"label": body},
        "link": {"attributes": {"href": url}},
    }


def feed(entries):
    return {"feed": {"entry": entries}}


class BuildUrlTest(unittest.TestCase):
    def test_url_shape(self):
        self.assertEqual(
            tool.build_url(123, "gb", 2),
            "https://itunes.apple.com/gb/rss/customerreviews/page=2/id=123/sortBy=mostRecent/json",
        )


class ParseFeedTest(unittest.TestCase):
    def test_parses_rows_and_collapses_whitespace(self):
        rows = tool.parse_feed(feed([entry(1, "Lost it", "It  crashed\n twice")]))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["source"], "appstore")
        self.assertEqual(row["url"], SAME_URL)
        self.assertEqual(row["date"], "2026-09-20")
        self.assertEqual(row["rating"], "1")
        self.assertEqual(row["text"], "Lost it. It crashed twice")

    def test_skips_app_entry_without_rating(self):
        rows = tool.parse_feed(feed([{"im:name": {"label": "Example App"}}, entry(4, "Fine", "Works")]))
        self.assertEqual([r["rating"] for r in rows], ["4"])

    def test_single_entry_dict_is_handled(self):
        rows = tool.parse_feed(feed(entry(2, "One", "Only")))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["text"], "One. Only")

    def test_empty_feed(self):
        self.assertEqual(tool.parse_feed({"feed": {}}), [])
        self.assertEqual(tool.parse_feed({}), [])
        self.assertEqual(tool.parse_feed("not json"), [])

    def test_missing_link_gives_blank_url(self):
        row = tool.parse_feed(feed([{"im:rating": {"label": "3"}, "title": {"label": "t"}, "content": {"label": "c"}}]))[0]
        self.assertEqual(row["url"], "")


class CollectTest(unittest.TestCase):
    def test_stops_at_first_empty_page_and_never_passes_ten(self):
        calls = []

        def fake_fetch(url):
            calls.append(url)
            page = int(url.split("page=")[1].split("/")[0])
            if page <= 2:
                return feed([entry(5, "p{}".format(page), "body")])
            return {"feed": {}}

        rows = tool.collect("1", "us", pages=50, fetch=fake_fetch, pause=0)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(calls), 3)
        self.assertIn("page=3/", calls[-1])

    def test_http_error_stops_quietly(self):
        def fake_fetch(url):
            raise urllib.error.HTTPError(url, 404, "nope", {}, None)

        self.assertEqual(tool.collect("1", fetch=fake_fetch, pause=0), [])


class WriteAndSummariseTest(unittest.TestCase):
    def test_writes_csv_with_expected_columns(self):
        rows = tool.parse_feed(feed([entry(1, "A", "B"), entry(5, "C", "D", date="2025-01-01T00:00:00-07:00")]))
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.csv")
            tool.write_csv(rows, path)
            with open(path, newline="", encoding="utf-8") as handle:
                data = list(csv.DictReader(handle))
        self.assertEqual(list(data[0].keys()), ["source", "url", "date", "rating", "text"])
        self.assertEqual(len(data), 2)

    def test_summary_flags_identical_urls(self):
        rows = tool.parse_feed(feed([entry(1, "A", "B"), entry(2, "C", "D")]))
        text = tool.summarise(rows)
        self.assertIn("2 reviews", text)
        self.assertIn("same App Store page", text)

    def test_summary_for_nothing(self):
        self.assertIn("0 reviews", tool.summarise([]))


if __name__ == "__main__":
    unittest.main()
