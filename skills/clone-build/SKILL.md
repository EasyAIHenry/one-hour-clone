---
name: clone-build
description: Build the vertical slice of a one-feature rebuild from clone/plan.md. Use when the user says "build it", "start building", "build the slice", "build screen S03", "make it work locally", or after clone-plan finishes. Fresh code and fresh copy only, never the original's name, logo, colours, copy or assets. Ends with npm run build passing and routes answering to curl.
---

# clone-build

Build one flow end to end, then one screen at a time. Working beats pretty. Fresh beats copied.

## Inputs

- `clone/plan.md` (stack, schema, routes, build order).
- `clone/map.md` and `clone/features.csv` (screens, states, the rows to flip).

## Hard rules

1. Every line of code and copy is written here. No code, markup, styles, images, icons or
   sentences from the original. Not even the product name. Call the clone something plain.
2. Nothing from the original's brand: no logo, no colour values, no font choice copied from it.
3. Tokens file first (`app/tokens.css`): colours, spacing, radius, type scale, as CSS variables.
   If no design pass has happened, write a temporary grey-and-one-accent set and say it is temporary.
4. Every screen handles every state: empty, loading, error, long content, and 390 px wide.
5. One commit per vertical slice, then one commit per screen.
6. `npm run build` must pass before any commit.
7. Check every route with curl before calling it done.

## Step 1. Scaffold

```
npx create-next-app@16 <plain-name> --typescript --app --no-tailwind --eslint --src-dir=false --import-alias "@/*"
cd <plain-name>
node --version        # 22.13 or newer for node:sqlite, else use the JSON store
npm pkg set devDependencies.@types/node="^22"
npm install
git init && git add -A && git commit -m "Scaffold"
```

## Step 2. Tokens and shell

- Write `app/tokens.css` and import it in `app/layout.tsx`.
- Remove the Google Fonts import the scaffold ships (it needs network at build time). Use `font-family: system-ui, sans-serif`.
- Layout: one header with the plain name, one `main` with `max-width` and `padding: 16px`.

## Step 3. Store

`lib/db.ts` with the tables from the plan.

- With `node:sqlite`: `import { DatabaseSync } from "node:sqlite"`, open `data/app.db`, run the schema with `CREATE TABLE IF NOT EXISTS`.
- Without it: `lib/store.ts` reading and writing `data/app.json` with the same shape, one function per table.
- Add `data/` to `.gitignore`. Add `npm run seed` that inserts two rows.

## Step 4. The slice

Build the main flow from the plan in this order: store, API route, page. Then:

```
npm run build
npm run dev &
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/
curl -s -X POST http://localhost:3000/api/<resource> -H "content-type: application/json" -d '{"title":"test"}'
curl -s http://localhost:3000/api/<resource> | head -c 300
```

Every route in the plan's table gets a curl line. Record the status codes in the chat.
Flip the matrix rows this slice completed from `no` to `yes` or `partial`. Commit.

## Step 5. Screens

For each remaining screen in flow order: build it, cover the five states, run the build,
curl its route, flip its rows, commit. Stop when the hour is up. The matrix records where you stopped.

## Known gotchas

- `create-next-app` ships Next.js 16. `params` in pages and route handlers is a Promise:
  `const { slug } = await params;` and type it `{ params: Promise<{ slug: string }> }`.
- The scaffold's Google Fonts import (`next/font/google`) fetches at build time. Offline builds fail. Remove it.
- `node:sqlite` rows have a null prototype. Spread them before passing to a client component:
  `rows.map((r) => ({ ...r }))`. Otherwise the serialiser complains about a non-plain object.
- `@types/node` must be 22 or newer for `node:sqlite` types to exist. Check `package.json`.
- A 7 column CSS grid (week views, calendars) needs `min-width: 0` on its children, or
  chips with `white-space: nowrap` push the grid wider than the screen at 390 px.
- Route handlers return `Response.json(data, { status: 201 })`. `NextResponse` works too; pick one.
- Files on disk: write to `data/files/<id>` and serve through a route that sets `content-type`, not from `public/`.

## Definition of done

### Automatable (do these, print the results)
- `npm run build` exits 0.
- Every route in the plan answers curl with the expected status.
- `clone/features.csv` has no `no` left on a must row that the slice claimed.
- Each screen renders the empty state with an empty store (`rm -rf data && npm run seed -- --empty`).

### A person does this (list them, do not tick them)
- Click a real screen picker or file picker and confirm the file lands.
- Walk the main flow with the keyboard only, Tab and Enter, no mouse.
- Open it at 390 px wide in the browser's device mode and look at every screen.
- Read every sentence of copy once, out loud.

Print both lists at the end, with the automatable ones marked pass or fail. Next: clone-reviews, then clone-score.
