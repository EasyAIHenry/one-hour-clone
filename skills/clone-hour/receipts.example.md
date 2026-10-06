# Receipts

Start: 2026-10-07T01:10:00Z

Assumptions: none, questions were answered.

## Size  T+4 min
Commands:
  (web search) site:example-recorder.app help
  (web search) site:example-recorder.app pricing
  (web search) site:apps.apple.com example recorder
Result: S for the slice "record my screen and get a share link". Cannot rebuild: their CDN, viewer analytics, team workspaces.

## Map  T+13 min
Commands:
  (browser, own account) walked the record flow, 7 screens
  wrote clone/map.md, clone/features.csv
Result: 7 screens, 3 flows (6, 4 and 3 clicks), 22 matrix rows: 6 must, 9 should, 4 could, 2 skip, 1 n/a.

## Plan  T+18 min
Commands:
  node --version   (v22.14.0, so node:sqlite)
  wrote clone/plan.md
Result: 2 tables (recording, view), 5 routes, 4 parts that bite.

## Build  T+49 min
Commands:
  npx create-next-app@16 quietcapture --typescript --app --no-tailwind --eslint --src-dir=false --import-alias "@/*"
  npm pkg set devDependencies.@types/node="^22" && npm install
  npm run build
  npm run dev &
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/
  curl -s -X POST http://localhost:3000/api/recordings -H "content-type: application/json" -d '{"title":"test","duration_s":12}'
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/r/abc12345
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/api/recordings/abc12345/file
Build compiled: yes
Routes answered: GET / 200, POST /api/recordings 201, GET /r/[slug] 200, GET /api/recordings/[id]/file 200, DELETE /api/recordings/[id] 204
Result: slice done (record, list, share page). Screens S05 trim and S06 settings not started. 31 min, over budget by 1.

## Reviews  T+54 min
Commands:
  python3 ~/.claude/skills/clone-reviews/tools/appstore_reviews.py --app-id 000000000 --country us --pages 2 --out clone/reviews_appstore.csv
  python3 ~/.claude/skills/clone-reviews/tools/hn_comments.py --query "example recorder" --pages 1 --out clone/reviews_hn.csv
  python3 ~/.claude/skills/clone-reviews/tools/themes.py clone/reviews.csv --preset video --top 5
Result: 100 App Store reviews (2 pages, us) and 14 Hacker News comments. Top theme "export and quality", 23 reviews, 2 sources. Apple feed links all rows to the listing page, so no per-review links.

## Score  T+57 min
Commands:
  python3 ~/.claude/skills/clone-score/tools/parity.py clone/features.csv
PARITY 63% | must 5/6 | should 4/9 | could 1/4 | skipped 2 | n/a 1 | not shippable yet

## Finish  T+58 min
Total: 58 min (under the hour by 2)
Parity: PARITY 63% | must 5/6 | should 4/9 | could 1/4 | skipped 2 | n/a 1 | not shippable yet

## What a person still has to do
- Click the real screen picker in Chrome and confirm a recording lands in data/files
- Walk record, stop, copy link with the keyboard only
- Open every screen at 390 px wide in device mode
- Read every sentence of copy once, out loud
- [must] Pick a window (capture, partial): the picker records the whole screen only
- [should] Trim clip (edit, missing)
- [should] Thumbnail on the share page (share, missing)
- Type in ten Google Play reviews by hand into clone/reviews_manual.csv

## Not rebuilt, by choice
- Team workspace: needs their network of users
- Viewer analytics by location: needs their CDN logs
