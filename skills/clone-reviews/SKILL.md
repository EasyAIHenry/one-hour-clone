---
name: clone-reviews
description: Find what the original app's users complain about, from sources a machine may fetch (Apple App Store review feed, Hacker News comments) plus notes a person types in from other sites. Use when the user says "what do people hate about X", "pull the reviews", "read the complaints", "find the pain points", or during clone-hour. Ships three tools (appstore_reviews.py, hn_comments.py, themes.py) and prints ranked themes with quotes and sample sizes.
---

# clone-reviews

Learn what paying users dislike, so the slice fixes one real thing instead of copying everything.

## Tools (standard library Python, no installs)

All paths are relative to this skill folder. Run them from anywhere with the full path.

| Tool | Does | Output |
| --- | --- | --- |
| `tools/appstore_reviews.py` | Apple's public RSS JSON, up to 10 pages of 50, most recent first | CSV |
| `tools/hn_comments.py` | Hacker News Algolia search, comments that mention the app | CSV |
| `tools/themes.py` | Groups a CSV into themes from keyword lists, ranks them, prints quotes | text |

CSV columns are always `source,url,date,rating,text`.

## Step 1. Find the App Store id

Search `site:apps.apple.com <app name>`. The id is the digits after `id` in the URL.
Never guess an id. If the app has no App Store listing, skip to Step 3.

## Step 2. Fetch by machine

```
mkdir -p clone
python3 ~/.claude/skills/clone-reviews/tools/appstore_reviews.py --app-id <ID> --country us --pages 10 --out clone/reviews_appstore.csv
python3 ~/.claude/skills/clone-reviews/tools/hn_comments.py --query "<app name>" --pages 2 --out clone/reviews_hn.csv
```

Try a second country if the first returns few rows: `--country gb`. Each page is a separate
request with a short pause, so 10 pages takes about ten seconds.

The Apple feed links every review to the same App Store page. The tool prints this when it
happens. So "linked to the exact review" is not possible from the feed; say so in your write-up.
Hacker News rows link to the exact comment.

## Step 3. Read by a person, type in by hand

Google Play, G2, Capterra, Trustpilot and Reddit are read in a browser by a person and typed
into a CSV with the same five columns. Never scrape them. Ten rows typed by hand are worth more
than a scraper that breaks the site's terms.

```
source,url,date,rating,text
googleplay,https://play.google.com/store/apps/details?id=...,2026-09-12,2,"Export fails on long clips"
reddit,https://www.reddit.com/r/.../comments/...,2026-08-30,,"Price doubled and the free tier lost sharing"
```

Save as `clone/reviews_manual.csv`. Rating blank where the site has none.

## Step 4. Combine and group

```
python3 - <<'EOF'
import csv, glob
rows = []
for path in sorted(glob.glob("clone/reviews_*.csv")):
    with open(path, newline="", encoding="utf-8") as f:
        rows.extend(csv.DictReader(f))
with open("clone/reviews.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["source", "url", "date", "rating", "text"])
    w.writeheader()
    w.writerows({k: r.get(k, "") for k in w.fieldnames} for r in rows)
print(len(rows), "rows")
EOF
python3 ~/.claude/skills/clone-reviews/tools/themes.py clone/reviews.csv --preset video --top 8 --quotes 3
```

Presets: `general` (always on), plus one of `video`, `scheduling`, `notes`, `finance`.
Add words to `tools/themes.json` when a theme you can see in the quotes is not being caught.
It is a word list, not a model. Expect some wrong matches and read the quotes.

How ranking works: low ratings and recent dates weigh more. A one star review from last month
counts about five times a five star review from years ago. The tool prints the formula with `--help`.

## Step 5. Write clone/reviews.md

```markdown
# Reviews: <app>

Sample: <n> reviews. appstore <a> (us, 10 pages), hackernews <h>, manual <m>.
Apple feed: all rows link to the listing page, not to individual reviews.

## Top themes
1. <theme>: <count> reviews, <sources> sources. <one sentence>. Thin: yes/no.
   - "<quote>" (source, date, rating)

## What this changes in the slice
- <one feature row to add or raise to must, with the theme that justifies it>
```

## Rules

- Never invent a review, a quote, a count or a date. Quotes come from the CSV, cut with "..." when long.
- State the sample size every time you state a theme.
- A theme is thin when it has under 3 reviews or comes from one source. Say "thin" next to it.
- Machine fetch only from the two feeds above. Everything else is a person reading in a browser.
- Reviews describe the original. They are not evidence about your clone.
