---
name: clone-hour
description: Run the whole one-hour rebuild with a clock, chaining clone-size, clone-map, clone-plan, clone-build, clone-reviews and clone-score, and write clone/receipts.md with the time at each stage, the commands run, the parity line and what a person still has to do. Use when the user says "one hour clone", "rebuild X in an hour", "run the hour", "do the full run", "start the timer", or wants the whole pack run end to end.
---

# clone-hour

The runbook. Six stages, one clock, one receipts file. The hour is a budget, not a promise.

## Before you install any skill pack, including this one

```
skillspector scan --no-llm <path-or-git-url>
```

Read the finding behind any HIGH before you trust it or dismiss it. A word list in a lint tool
(for example `themes.json` in clone-reviews) can trigger a pattern match. Say what the finding
is, not just its label, and let the user decide.

## Step 0. Start the clock

```
mkdir -p clone
date +%s > clone/.start
printf '# Receipts\n\nStart: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > clone/receipts.md
```

Stamp helper, run before each stage line:

```
echo "T+$(( ($(date +%s) - $(cat clone/.start)) / 60 )) min"
```

## Budget

| Stage | Skill | Budget | Receipt line |
| --- | --- | --- | --- |
| 1 | clone-size | 5 min | size letter and one reason |
| 2 | clone-map | 10 min | screens, flows, matrix rows |
| 3 | clone-plan | 5 min | tables, routes |
| 4 | clone-build | 30 min | build compiled (yes/no), routes answered (codes) |
| 5 | clone-reviews | 5 min | sample size, top theme |
| 6 | clone-score | 5 min | parity line verbatim |

If a stage runs past its budget by half, write "over budget" in the receipt and move on.
Build is the only stage allowed to borrow time, and only from reviews.

## Step 1 to 6. Run each skill

Run them in order. After each one, append to `clone/receipts.md`:

```
## <stage>  T+<n> min
Commands:
  <the commands you actually ran, one per line>
Result: <one line>
```

Stage 4 appends two lines, "Build compiled: yes" (or the first error) and
"Routes answered: GET / 200, POST /api/x 201, ..." from the curl checks.
Stage 6 appends the parity line exactly as printed, starting with `PARITY`.

## Step 7. Close the receipts

```
## Finish  T+<n> min
Total: <n> min (<over or under> the hour by <m>)
Parity: <the PARITY line again>

## What a person still has to do
- <the "a person does this" list from clone-build>
- <top three missing rows from clone-score, in build order>
- <reviews read by hand that are still to type in>

## Not rebuilt, by choice
- <skip rows from the matrix, with reasons>
```

Then print the whole receipts file in the chat. The user should not have to open it.

## Non-interactive mode

If nobody answers a question within a turn, each skill proposes the answer, writes the
assumption down and continues. clone-hour collects every assumption under a heading
"Assumptions" at the top of the receipts so they are the first thing a reader sees.

## Rules

- The clock is wall time, not effort. If you waited on a download, that counted.
- Receipts record what happened, not what was planned. Commands that failed go in too.
- The parity line is copied, never retyped.
- Over an hour is fine. Say so in the Total line. Hiding it is not fine.
- Nothing in receipts.md names the original app's brand assets, only its name and the public URLs read.

See `receipts.example.md` next to this file for a filled example.
