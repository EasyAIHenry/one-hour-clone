---
name: clone-size
description: Size an app before anyone tries to rebuild it. Run this first, before clone-map or any code, when the user says "I want to rebuild X", "clone this app", "make my own version of X", "how hard would it be to copy X", "is this a weekend project", "size this", or pastes an app URL or App Store link and wants their own. Writes clone/size.md with a size of S, M, L or XL and says the size out loud with reasons.
---

# clone-size

Decide how big the job is before spending an hour on it. Most apps are not one feature.
You are rebuilding one feature, for one kind of person, and this skill names it.

## Step 1. Three questions

Ask these in one message, not three:

1. Which app? (name and the public URL you were given)
2. Which single feature do you pay for? One sentence, a verb and a noun. "Record my screen and get a share link."
3. Who is it for? You alone, your team, or strangers on the internet.

If nobody answers within the turn, switch to non-interactive mode: pick the most likely
answer, write it under "Assumptions" in `clone/size.md`, and continue. Say so in the chat:
"non-interactive mode: assumed X, written down, continuing".

## Step 2. Find public sources

Use web search with `site:` filters. Never guess a URL and never fetch one you did not see in a result.

```
site:<app domain> help            (help centre, support docs)
site:<app domain> pricing         (pricing page: what is paid, what is capped)
site:apps.apple.com <app name>    (App Store listing, screenshots, review count)
site:play.google.com <app name>   (Play listing, if there is one)
```

Read the pricing page and the help centre pages about the one feature. Note the URLs.

Do not read the app's JavaScript bundles, network calls, API responses, or anything that sits
behind a login other than the user's own account. Public pages and the user's own account only.

## Step 3. Write clone/size.md

```
mkdir -p clone
```

Use this layout:

```markdown
# Size: <app>, <feature>

Date: <YYYY-MM-DD>
Assumptions: <only if non-interactive mode was used>

## The feature in one line
<verb + noun + for whom>

## Sources read
- <url> (what it told you)

## What the app owns that cannot be rebuilt
- Licensed content (fonts, music, stock, maps, data feeds)
- Its network of users (followers, marketplaces, shared workspaces)
- Partner API access (bank feeds, carrier accounts, platform partner tiers)
- Hardware (cameras, sensors, custom devices)
- Regulated licences (payments, health, finance, telecoms)
Keep only the lines that apply. Say why for each.

## Hard parts
- <the two or three things that take real engineering: sync, real time, media processing, permissions>

## Size
<S | M | L | XL>: <two sentences of reasons>
```

## Step 4. Sizing rules

| Size | Meaning | Signals |
| --- | --- | --- |
| S | One sitting, about an hour | one screen that matters, CRUD plus one trick, local files, no auth, no third party |
| M | A weekend | two or three flows, some media or file processing, one external API with a free tier |
| L | Weeks | real time collaboration, mobile native, offline sync, payments, heavy media pipeline |
| XL | Rescope before starting | depends on something in "cannot be rebuilt", or a regulated licence, or the feature is the network itself |

Size the slice, not the whole app. "Record screen and share a link" is S. "Be a video platform" is XL.
If the size is L or XL, propose a smaller slice that is S and ask whether that is still worth an hour.

## Step 5. Say it out loud

Before handing off, print the size and the reasons in the chat in this shape:

```
Size: S. One screen, local files, no auth. Hard part is the browser screen picker,
which the browser owns. Cannot rebuild: their CDN and their viewer analytics.
Continue to clone-map? (yes / change the slice)
```

Wait for a yes unless in non-interactive mode. Then run `clone-map`.

## Rules

- One feature. If the user lists three, size each in one line and ask them to pick.
- Public pages and the user's own account only. No scraping, no bundles, no network tab.
- Write the assumption down before acting on it.
- No hype. "S" and "about an hour" are the strongest words allowed.
