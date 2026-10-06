# one-hour-clone

You pay for an app because of one feature. This pack helps you rebuild that one feature, on your own machine, in about an hour.
It sizes the job first, so you know before you start whether an hour is honest.
Seven Claude Code skills, three small Python tools, no installs beyond Node for the build.

## Install

```
git clone https://github.com/EasyAIHenry/one-hour-clone.git
skillspector scan --no-llm one-hour-clone          # optional, scans any skill pack before you trust it
cp -r one-hour-clone/skills/* ~/.claude/skills/
```

Then in Claude Code: "one hour clone: rebuild the share link from my screen recorder".

Python 3.9 or newer for the tools. Node 22.13 or newer if you want SQLite without installing anything; otherwise the build uses a JSON file.

## The seven skills

Run them in this order, or say "run the hour" and `clone-hour` chains them with a clock.

| Skill | What it does | Writes |
| --- | --- | --- |
| `clone-size` | Names the one feature, finds public sources, sizes it S, M, L or XL, says why | `clone/size.md` |
| `clone-map` | Screens, flows with click counts, components, data model with evidence, feature matrix | `clone/map.md`, `clone/features.csv` |
| `clone-plan` | Stack in two columns (this hour, and when it leaves your machine), SQL, routes, parts that bite | `clone/plan.md` |
| `clone-build` | The vertical slice in Next.js and TypeScript, fresh code and copy, every state, build must pass | your app folder |
| `clone-reviews` | What the original's users dislike, from the App Store feed and Hacker News, grouped into themes | `clone/reviews.csv`, `clone/reviews.md` |
| `clone-score` | A parity percentage from the matrix. Honest, floored, with the missing list | the parity line |
| `clone-hour` | The runbook. Timer, receipts at each stage, the parity line verbatim, what a person still has to do | `clone/receipts.md` |

## How an hour goes

Say your app is a screen recorder and the feature you pay for is "record my screen and get a share link".

- 4 min. `clone-size` reads the help centre and pricing page, finds the App Store listing, and says: S for the slice. Cannot rebuild their CDN, viewer analytics or team workspaces.
- 13 min. `clone-map` walks the flow in your own account. 7 screens, 3 flows, 22 matrix rows.
- 18 min. `clone-plan` picks Next.js with `node:sqlite`, two tables, five routes, four parts that bite (the browser owns the screen picker, big uploads, slugs, time zones).
- 49 min. `clone-build` scaffolds, writes the tokens file, the store, the routes and the first screen. `npm run build` passes. Five routes answer curl. Two screens not started.
- 54 min. `clone-reviews` pulls 100 App Store reviews and 14 Hacker News comments. Top theme is export quality, 23 reviews across two sources.
- 57 min. `clone-score` prints `PARITY 63% | must 5/6 | should 4/9 | could 1/4 | skipped 2 | n/a 1 | not shippable yet`.
- 58 min. `clone-hour` closes the receipts with the list a person still has to do: click the real screen picker, keyboard walk, 390 px look, the one must-have that is partial.

That is a normal hour. A score in the 60s with "not shippable yet" is the usual honest result. See `skills/clone-hour/receipts.example.md` for the full file.

## Fine print

- This rebuilds what an app does, never what it owns. Licensed content, its network of users, partner API access, hardware and regulated licences are marked `skip` and left alone.
- Reading, not scraping. The tools fetch two public feeds that are built to be fetched. Everything else is read by you in a browser and typed in.
- Your own account only. No one else's data, no JavaScript bundles, no network tab.
- Rebrand before you ship. Fresh code, fresh copy, your own name, your own colours. Nothing of theirs.
- Check the terms of the app you are rebuilding, and of the hosts you deploy to.
- None of this is legal advice.

## Ten features worth an hour

Short list. Each one is sized in `IDEAS.md` with what you cannot rebuild and the hard part.

1. Screen recorder: record and get a share link
2. Booking link: one page where people pick a slot
3. Link-in-bio page: one page of links with click counts
4. Social post queue: write now, post later, one account
5. Habit tracker: tick a box a day, see the streak
6. Invoice generator: fill a form, get a PDF with a number
7. URL shortener with stats: short link, click count by day
8. Form builder: a few field types, a share link, a results table
9. Newsletter signup page: an email box, a list, a CSV export
10. Kanban board: three columns, drag a card, it stays

## Tests

```
python3 -m unittest discover -s tests
```

No network in tests. Feed shapes are built inline.

## Licence

MIT. See `LICENSE`.

Made by Henry Chua. https://www.instagram.com/henrychua
