#!/usr/bin/env python3
"""Pull App Store customer reviews from Apple's public RSS JSON feed into a CSV.

Standard library only. Python 3.9 or newer.

Usage:
    python3 appstore_reviews.py --app-id 123456789 --country us --pages 10 --out clone/reviews.csv

The feed gives at most 50 reviews a page and at most 10 pages, so 500 reviews
is the ceiling. Every row in the feed links to the same App Store page, so the
url column is the same for every review. The tool says so when it finishes.

CSV columns: source,url,date,rating,text
"""
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request

SOURCE = "appstore"
MAX_PAGES = 10
COLUMNS = ["source", "url", "date", "rating", "text"]


def build_url(app_id, country="us", page=1):
    """Return the feed URL for one page of reviews, most recent first."""
    return (
        "https://itunes.apple.com/{country}/rss/customerreviews/"
        "page={page}/id={app_id}/sortBy=mostRecent/json"
    ).format(country=country, page=page, app_id=app_id)


def _label(node, key):
    """Read feed['entry'][i][key]['label'] safely. Returns '' when missing."""
    value = node.get(key)
    if isinstance(value, dict):
        return str(value.get("label", "")).strip()
    if value is None:
        return ""
    return str(value).strip()


def parse_feed(data):
    """Turn one page of feed JSON into a list of CSV row dicts.

    The feed puts a single review in a dict instead of a list, and leaves the
    key out when a page is empty. Both are handled here.
    """
    feed = data.get("feed", {}) if isinstance(data, dict) else {}
    entries = feed.get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]
    rows = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rating = _label(entry, "im:rating")
        if not rating:
            # The first entry on some pages is the app itself, not a review.
            continue
        title = _label(entry, "title")
        body = _label(entry, "content")
        text = ". ".join(part for part in (title, body) if part)
        link = entry.get("link", {})
        url = ""
        if isinstance(link, dict):
            url = str(link.get("attributes", {}).get("href", "")).strip()
        rows.append(
            {
                "source": SOURCE,
                "url": url,
                "date": _label(entry, "updated")[:10],
                "rating": rating,
                "text": " ".join(text.split()),
            }
        )
    return rows


def fetch_json(url, timeout=20):
    """GET a URL and parse it as JSON. Raises on network or parse errors."""
    request = urllib.request.Request(url, headers={"User-Agent": "one-hour-clone/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def collect(app_id, country="us", pages=MAX_PAGES, fetch=fetch_json, pause=0.5):
    """Fetch pages 1..pages and return all review rows. Stops at the first empty page."""
    pages = max(1, min(int(pages), MAX_PAGES))
    rows = []
    for page in range(1, pages + 1):
        url = build_url(app_id, country, page)
        try:
            data = fetch(url)
        except urllib.error.HTTPError as err:
            print("page {}: HTTP {}. Stopping.".format(page, err.code), file=sys.stderr)
            break
        except (urllib.error.URLError, ValueError) as err:
            print("page {}: {}. Stopping.".format(page, err), file=sys.stderr)
            break
        page_rows = parse_feed(data)
        if not page_rows:
            break
        rows.extend(page_rows)
        if page < pages and pause:
            time.sleep(pause)
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in COLUMNS})


def summarise(rows):
    """Return a short plain-text summary for the terminal."""
    if not rows:
        return "0 reviews collected. Check the app id and country code."
    urls = {row["url"] for row in rows}
    lines = ["{} reviews collected from the {} feed.".format(len(rows), SOURCE)]
    if len(urls) == 1:
        lines.append(
            "Every review links to the same App Store page, so a link to the exact review is not possible from this feed."
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--app-id", required=True, help="numeric App Store id, the digits after id in the store URL")
    parser.add_argument("--country", default="us", help="two letter store country code, default us")
    parser.add_argument("--pages", type=int, default=MAX_PAGES, help="pages to fetch, 1 to 10, default 10")
    parser.add_argument("--out", default="reviews.csv", help="CSV path to write")
    args = parser.parse_args(argv)

    rows = collect(args.app_id, args.country, args.pages)
    write_csv(rows, args.out)
    print(summarise(rows))
    print("Wrote {}".format(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
