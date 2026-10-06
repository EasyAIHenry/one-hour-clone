---
name: clone-map
description: Map one feature of an app before rebuilding it. Use after clone-size, when the user says "map it", "what screens does X have", "how does X work", "reverse engineer the flow", "list the features", or asks for a feature matrix. Produces clone/map.md (screens, flows with click counts, components, inferred data model with evidence and confidence) and clone/features.csv. Public sources and the user's own account only.
---

# clone-map

Recon of ONE feature. Not the whole app. The output is a map a builder can work from
and a feature matrix the scorer can read.

## Inputs

- `clone/size.md` from clone-size. If it is missing, run clone-size first.
- The user's own account in the app, if they have one and a browser tool is attached.
- Public pages: help centre, pricing, App Store or Play listing, public demo videos.

## Step 1. Screens

Walk the feature in the user's own account, or from help centre screenshots and listing
screenshots when no account is available. Number each screen `S01`, `S02`, ...

For each screen record: id, name, what the user does there, what it shows, what it leads to.

Screenshots you take are reference only. Save them under `clone/screens/` and keep that
folder out of the shipped repo (the pack's `.gitignore` already ignores `clone/`). Never copy
a screenshot, icon, illustration or line of copy into the build.

### When no browser tool is attached

Say so in the first line of `clone/map.md`. List the screens you can infer from the help
centre and the store listing and mark each one `unseen`. Set confidence to `low` for every
inferred screen. Do not invent a screen you have no source for; write "unknown" instead.

## Step 2. Flows with click counts

A flow is a path from intent to result. Count every click, tap and keypress the user makes.

```
F1 Record and share: S01 -> S02 -> S03 -> S05. 6 clicks. Ends with a link in the clipboard.
```

Three to five flows is normal for one feature. If you have more, the slice is too big.
Go back to clone-size.

## Step 3. Components

List the reusable pieces you saw: top bar, picker, timer, progress bar, link card, empty
state, error toast. For each, one line: name, where it appears, what it does.
This is a list of behaviours, not a style guide. Colours and names are not recorded.

## Step 4. Inferred data model

Write what the data must look like for the screens to work, with evidence and confidence.

```
Recording: id, title, duration_s, created_at, share_slug, thumbnail
  evidence: S03 shows title, duration and date; the share link has a short slug
  confidence: high
Viewer: ip hash, viewed_at
  evidence: pricing page says "view counts" on the paid tier; never seen the table
  confidence: low
```

Confidence is `high` (seen on a screen), `medium` (described in help docs), `low` (guessed).

## Step 5. Feature matrix

Write `clone/features.csv` with this exact header:

```
feature,area,priority,original,clone,notes
```

- `priority`: `must`, `should` or `could`. Must is what the slice cannot ship without.
- `original`: `yes`, `partial` or `no`. `no` means the app does not have it and you want it.
- `clone`: starts as `no` for every row. The build flips it to `yes` or `partial`.
- Use `skip` in `clone` for anything in size.md's "cannot be rebuilt" list, with the reason in `notes`.
- Use `n/a` in `clone` when the browser or OS provides it (file picker, notifications, screen capture permission).
- `area` groups rows: capture, edit, share, settings, and so on. The scorer reports the weakest area.

Fifteen to thirty rows is normal. Every row needs a source: a screen id or a URL in `notes`.

## Step 6. Write clone/map.md

```markdown
# Map: <app>, <feature>
Browser tool: attached | not attached (screens marked unseen)
Sources: <urls and "own account">

## Screens
## Flows
## Components
## Data model
## Feature matrix
See clone/features.csv. <n> rows: <m> must, <s> should, <c> could, <k> skip, <a> n/a.
```

End with: "Map done. <n> screens, <f> flows, <r> rows. Next: clone-plan."

## Rules

- Public sources and the user's own account. No JavaScript bundles, no network tab, no other people's accounts.
- Screenshots are reference, never shipped.
- No guessing dressed as fact. Every row and every entity carries a source or a confidence.
- One feature. If the map grows past five flows, stop and re-size.
