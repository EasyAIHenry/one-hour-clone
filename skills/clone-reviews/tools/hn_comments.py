#!/usr/bin/env python3
"""Pull Hacker News comments that mention an app from the Algolia search API into a CSV.

Standard library only. Python 3.9 or newer.

Usage:
    python3 hn_comments.py --query "app name" --pages 3 --out clone/hn.csv

Each row links to the exact comment on news.ycombinator.com. Hacker News has no
star rating, so the rating column is left blank.

CSV columns: source,url,date,rating,text
"""
import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SOURCE = "hackernews"
HITS_PER_PAGE = 100
COLUMNS = ["source", "url", "date", "rating", "text"]
_TAG = re.compile(r"<[^>]+>")


def build_url(query, page=0, hits_per_page=HITS_PER_PAGE):
    """Return the Algolia search URL for one page of comments."""
    params = urllib.parse.urlencode(
        {"query": query, "tags": "comment", "page": int(page), "hitsPerPage": int(hits_per_page)}
    )
    return "https://hn.algolia.com/api/v1/search?" + params


def clean_text(raw):
    """Strip HTML tags and entities, collapse whitespace."""
    if not raw:
        return ""
    text = _TAG.sub(" ", str(raw).replace("<p>", " "))
    text = html.unescape(text)
    return " ".join(text.split())


def parse_hits(data):
    """Turn one page of Algolia JSON into a list of CSV row dicts."""
    hits = data.get("hits", []) if isinstance(data, dict) else []
    rows = []
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        text = clean_text(hit.get("comment_text"))
        if not text:
            continue
        object_id = str(hit.get("objectID", "")).strip()
        rows.append(
            {
                "source": SOURCE,
                "url": "https://news.ycombinator.com/item?id={}".format(object_id) if object_id else "",
                "date": str(hit.get("created_at", ""))[:10],
                "rating": "",
                "text": text,
            }
        )
    return rows


def fetch_json(url, timeout=20):
    request = urllib.request.Request(url, headers={"User-Agent": "one-hour-clone/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def collect(query, pages=1, fetch=fetch_json, pause=0.5):
    """Fetch pages 0..pages-1 and return all comment rows. Stops when the API says it is out of pages."""
    pages = max(1, int(pages))
    rows = []
    for page in range(pages):
        url = build_url(query, page)
        try:
            data = fetch(url)
        except urllib.error.HTTPError as err:
            print("page {}: HTTP {}. Stopping.".format(page, err.code), file=sys.stderr)
            break
        except (urllib.error.URLError, ValueError) as err:
            print("page {}: {}. Stopping.".format(page, err), file=sys.stderr)
            break
        page_rows = parse_hits(data)
        rows.extend(page_rows)
        nb_pages = data.get("nbPages", 0) if isinstance(data, dict) else 0
        if not page_rows or page + 1 >= int(nb_pages or 0):
            break
        if pause:
            time.sleep(pause)
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in COLUMNS})


def summarise(rows, query):
    if not rows:
        return "0 comments found for {!r}. Try the app name on its own, without the company name.".format(query)
    return "{} comments collected for {!r}. Comments mention the app; they are not reviews of it, so read before you trust a theme.".format(
        len(rows), query
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--query", required=True, help="search text, usually the app name in quotes")
    parser.add_argument("--pages", type=int, default=1, help="pages of 100 to fetch, default 1")
    parser.add_argument("--out", default="hn.csv", help="CSV path to write")
    args = parser.parse_args(argv)

    rows = collect(args.query, args.pages)
    write_csv(rows, args.out)
    print(summarise(rows, args.query))
    print("Wrote {}".format(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
