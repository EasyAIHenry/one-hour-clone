#!/usr/bin/env python3
"""Group a reviews CSV into themes using keyword lists, then print a ranked table and quotes.

Standard library only. Python 3.9 or newer.

Usage:
    python3 themes.py clone/reviews.csv --preset video --top 8 --quotes 3

Input CSV columns: source,url,date,rating,text (the output of appstore_reviews.py or
hn_comments.py, or a file you typed in by hand from a browser).

How ranking works:
  Each review that matches a theme adds a weight to that theme.
  Weight = rating weight x recency weight.
  Rating 1 star counts 2.0, 2 stars 1.6, 3 stars 1.2, 4 stars 0.8, 5 stars 0.6, no rating 1.0.
  Recency: last 90 days 1.5, last 365 days 1.2, older or unknown 1.0.
  So a one-star review from last month counts five times a five-star review from years ago.

A theme is marked thin when it has fewer than 3 reviews or comes from a single source.
When every row has the same URL the tool says so, because that means the file came from a
feed that cannot link to the exact review.

Exit code is 0 for every data condition, including an empty file. Only a missing file
or bad arguments return non-zero.
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_THEMES = os.path.join(HERE, "themes.json")
THIN_MIN_REVIEWS = 3
RATING_WEIGHTS = {1: 2.0, 2: 1.6, 3: 1.2, 4: 0.8, 5: 0.6}


def load_presets(path=DEFAULT_THEMES):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data.get("presets", {})


def pick_themes(presets, preset_name="general"):
    """Return {theme: [keywords]} for general plus the chosen preset."""
    if preset_name not in presets:
        raise KeyError("unknown preset {!r}. Choose from: {}".format(preset_name, ", ".join(sorted(presets))))
    themes = {}
    for name in ("general", preset_name):
        for theme, words in presets.get(name, {}).items():
            themes.setdefault(theme, [])
            themes[theme].extend(words)
    return themes


def compile_themes(themes):
    """Turn keyword lists into one regex per theme. Whole-word, case-insensitive."""
    compiled = {}
    for theme, words in themes.items():
        parts = [r"\b" + re.escape(word.strip().lower()) + r"\b" for word in words if word.strip()]
        if parts:
            compiled[theme] = re.compile("|".join(parts), re.IGNORECASE)
    return compiled


def read_rows(path):
    with open(path, "r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for raw in reader:
            rows.append({key: (value or "").strip() for key, value in raw.items() if key})
    return rows


def rating_weight(value):
    try:
        rating = int(float(value))
    except (TypeError, ValueError):
        return 1.0
    return RATING_WEIGHTS.get(rating, 1.0)


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value[:10])
    except ValueError:
        return None


def recency_weight(value, today):
    day = parse_date(value)
    if day is None:
        return 1.0
    age = (today - day).days
    if age <= 90:
        return 1.5
    if age <= 365:
        return 1.2
    return 1.0


def group(rows, compiled, today=None):
    """Return a list of theme dicts sorted by weight, highest first."""
    today = today or datetime.date.today()
    buckets = {theme: {"theme": theme, "reviews": [], "weight": 0.0, "sources": set()} for theme in compiled}
    for row in rows:
        text = row.get("text", "")
        if not text:
            continue
        weight = rating_weight(row.get("rating")) * recency_weight(row.get("date"), today)
        for theme, pattern in compiled.items():
            if pattern.search(text):
                bucket = buckets[theme]
                bucket["reviews"].append((weight, row))
                bucket["weight"] += weight
                bucket["sources"].add(row.get("source", "") or "unknown")
    results = []
    for bucket in buckets.values():
        count = len(bucket["reviews"])
        if count == 0:
            continue
        bucket["reviews"].sort(key=lambda item: item[0], reverse=True)
        bucket["count"] = count
        bucket["thin"] = count < THIN_MIN_REVIEWS or len(bucket["sources"]) < 2
        results.append(bucket)
    results.sort(key=lambda item: (-item["weight"], -item["count"], item["theme"]))
    return results


def all_urls_identical(rows):
    urls = {row.get("url", "") for row in rows}
    return len(rows) > 1 and len(urls) == 1


def render(results, rows, top=8, quotes=3):
    lines = []
    lines.append("Sample: {} reviews from {} source(s).".format(len(rows), len({r.get("source", "") for r in rows})))
    if all_urls_identical(rows):
        lines.append("Note: every row has the same URL. This came from a feed that cannot link to the exact review.")
    if not results:
        lines.append("No theme matched. Try another --preset or add keywords to themes.json.")
        return "\n".join(lines)
    lines.append("")
    lines.append("{:<4}{:<28}{:>8}{:>9}{:>9}  {}".format("#", "theme", "reviews", "sources", "weight", "flag"))
    for index, item in enumerate(results[:top], start=1):
        flag = "thin" if item["thin"] else ""
        lines.append(
            "{:<4}{:<28}{:>8}{:>9}{:>9.1f}  {}".format(
                index, item["theme"][:27], item["count"], len(item["sources"]), item["weight"], flag
            )
        )
    lines.append("")
    lines.append("thin = fewer than {} reviews or a single source. Treat as a hint, not a finding.".format(THIN_MIN_REVIEWS))
    for item in results[:top]:
        lines.append("")
        lines.append("## {} ({} reviews)".format(item["theme"], item["count"]))
        for weight, row in item["reviews"][:quotes]:
            text = row.get("text", "")
            if len(text) > 200:
                text = text[:197].rstrip() + "..."
            meta = " | ".join(part for part in (row.get("source", ""), row.get("date", ""), ("{} star".format(row["rating"]) if row.get("rating") else "")) if part)
            lines.append("- \"{}\" ({})".format(text, meta))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("csv_path", help="reviews CSV with columns source,url,date,rating,text")
    parser.add_argument("--themes", default=DEFAULT_THEMES, help="path to themes.json")
    parser.add_argument("--preset", default="general", help="general, video, scheduling, notes or finance")
    parser.add_argument("--top", type=int, default=8, help="how many themes to print")
    parser.add_argument("--quotes", type=int, default=3, help="quotes per theme")
    parser.add_argument("--today", default=None, help="YYYY-MM-DD, for repeatable output in tests")
    args = parser.parse_args(argv)

    if not os.path.exists(args.csv_path):
        print("No such file: {}".format(args.csv_path), file=sys.stderr)
        return 1
    try:
        themes = pick_themes(load_presets(args.themes), args.preset)
    except KeyError as err:
        print(str(err), file=sys.stderr)
        return 1
    today = parse_date(args.today) if args.today else None
    rows = read_rows(args.csv_path)
    results = group(rows, compile_themes(themes), today=today)
    print(render(results, rows, top=args.top, quotes=args.quotes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
