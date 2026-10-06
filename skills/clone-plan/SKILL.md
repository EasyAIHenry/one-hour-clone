---
name: clone-plan
description: Pick the stack and write the schema for a one-feature rebuild. Use after clone-map, when the user says "plan it", "what stack", "design the database", "write the schema", "which routes do I need", or "what should I build first". Produces clone/plan.md with two columns (local this hour, and when it leaves your machine), SQL with constraints and indexes, a routes table, a parts-that-bite list and a build order.
---

# clone-plan

Turn the map into a plan a person can build in an hour, with the honest version of what
changes when real people use it.

## Inputs

- `clone/map.md` and `clone/features.csv` from clone-map.
- `clone/size.md` for the "cannot be rebuilt" list.

## Step 1. Two columns

Every decision goes in a table with these two columns. Do not mix them.

| Concern | Local, this hour | When it leaves your machine |
| --- | --- | --- |
| Framework | Next.js + TypeScript (`npx create-next-app@16`) | same |
| Database | `node:sqlite` (Node 22.13+) or a JSON file under `data/` | Postgres on a managed host |
| Files | `data/files/` on disk | object storage (S3 compatible) |
| Auth | none, single local user | Auth.js, email or OAuth |
| Payments | none | Stripe, one price, one webhook |
| Secrets | none | `.env` on the host, never in git |
| Background work | none, do it in the request | a queue or a cron on the host |

Check Node first: `node --version`. Below 22.13 means the JSON file store, not `node:sqlite`.

## Step 2. Schema

Write real SQL even if the hour uses a JSON file. The JSON store mirrors the tables.

Rules for every table:
- `id TEXT PRIMARY KEY` (use `crypto.randomUUID()`), not autoincrement.
- Times are `TEXT` in ISO 8601 UTC, `created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))`.
- `NOT NULL` on everything you will read without a null check.
- `CHECK` constraints for enums: `status TEXT NOT NULL CHECK (status IN ('draft','ready','failed'))`.
- `UNIQUE` on anything used in a URL (slugs).
- An index on every column you filter or sort by. Name them `idx_<table>_<column>`.
- Foreign keys with `ON DELETE CASCADE` where a child cannot exist without its parent.

Example shape:

```sql
CREATE TABLE recording (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  duration_s INTEGER NOT NULL CHECK (duration_s >= 0),
  share_slug TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL CHECK (status IN ('ready','failed')),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX idx_recording_created_at ON recording(created_at);
```

## Step 3. Access rules, written down

One line per table: who may read, who may write, in both columns.

```
recording: local = anyone on this machine. Hosted = owner reads and writes, share link reads one row by slug, no listing.
```

If a rule needs a column that does not exist (owner_id), add the column now and leave it null locally.

## Step 4. Routes table

| Method | Path | Flow | Reads | Writes | Returns |
| --- | --- | --- | --- | --- | --- |
| GET | /  | F1 | recording list | | page |
| POST | /api/recordings | F1 | | recording, file | 201 + json |
| GET | /r/[slug] | F1 | recording by slug | | page |

Every route maps to a flow id from the map. A route with no flow is cut.

## Step 5. Parts that bite

List the things that cost more than they look, with the local workaround and the hosted answer.

- Browser screen capture needs a user gesture and https (localhost counts). Hosted: https only.
- Large uploads: 50 MB in one POST is fine locally, not on a serverless host. Hosted: signed upload URL straight to storage.
- Time zones: store UTC, format in the browser.
- Slugs: 8 characters from a 32 letter alphabet is enough locally; add a collision retry.
- `node:sqlite` is synchronous: fine for one user, wrong for a hosted process with many.

## Step 6. Build order

Vertical slice first. One flow, end to end, ugly, working:

1. Schema and store module (`lib/db.ts`), with a seed script.
2. The one POST route and the one GET route the main flow needs.
3. The one screen that calls them. No styling beyond tokens.
4. `npm run build` passes. Routes answer to curl.
5. Then, and only then, the next screen from the map in flow order.

## Output

Write `clone/plan.md` with the six sections above in order. End with:
"Plan done. <t> tables, <r> routes, <b> parts that bite. Next: clone-build."
