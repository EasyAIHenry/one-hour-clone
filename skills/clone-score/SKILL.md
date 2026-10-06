---
name: clone-score
description: Score how much of the mapped feature the clone actually does, from clone/features.csv. Use when the user says "score it", "how close is it", "parity", "what is missing", "is it shippable", or at the end of clone-hour. Runs tools/parity.py and prints a parity percentage, must-haves done of total, weakest areas, the missing list in build order, and "not shippable yet" when a must-have is missing.
---

# clone-score

An honest number. The score is computed from the matrix, not from how the demo felt.

## Input

`clone/features.csv` with the header `feature,area,priority,original,clone,notes`.
If the file is missing, run clone-map. If every `clone` cell is still `no`, run clone-build.

## Run

```
python3 ~/.claude/skills/clone-score/tools/parity.py clone/features.csv
```

The last line of the output is the parity line. Copy it into `clone/receipts.md` without changes.

## How the score works

| Priority | Points |
| --- | --- |
| must | 3 |
| should | 2 |
| could | 1 |

- `clone = yes` earns full points, `partial` earns half, `no` earns none.
- `clone = skip` (cannot be rebuilt) and `clone = n/a` (browser or OS does it) are left out of the score and listed separately with their notes.
- Rows with `original = no` are left out too. You cannot have parity with something the original lacks.
- Parity = points earned divided by points available, as a percentage, rounded down.

Unknown values do not crash the tool. `priority` outside must, should, could counts as could.
`clone` outside the five values counts as no. Both print a warning with the line number.

## What it prints

```
Parity: 65% (8.5 of 13 points)
Must-haves done: 2 of 3 (1 partial)
Should-haves done: 0 of 1
Could-haves done: 1 of 2
Excluded: 1 skipped, 1 n/a, 1 the original does not have

Skipped (cannot be rebuilt, with reason):
- Team workspace: needs their user network

Weakest areas:
- edit at 0% (1 feature not done)

Missing, in build order:
- [must] Pick a window (capture, partial)
- [should] Trim clip (edit, missing)

Not shippable yet: a must-have is missing or partial.
PARITY 65% | must 2/3 | should 0/1 | could 1/2 | skipped 1 | n/a 1 | not shippable yet
```

"Shippable" here means every must row is `yes`. It does not mean a person has checked it.
The "a person does this" list from clone-build still stands.

## Reading the number

- 0 to 40: a sketch. Say so.
- 40 to 70: a working slice with holes. Normal after one hour.
- 70 to 90: usable by you. Not by strangers until the hosted column of the plan is done.
- 90 and up: check the matrix for rows that were quietly deleted. Parity this high after an hour usually means the map was too small.

Never round up in prose. The tool floors; you repeat the floored number.

## Step after the score

Write the top three missing rows, in the build order printed, into `clone/receipts.md`
under "what a person still has to do" or "next hour". That list is the plan for the next sitting.

## Rules

- Do not edit `clone/features.csv` to improve the score. Edit it to fix a wrong fact, and say what changed.
- Report skipped and n/a counts every time, so a 100% on three rows is seen for what it is.
- Quote the parity line verbatim. No paraphrase.
