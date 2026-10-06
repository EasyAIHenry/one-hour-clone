# Ten features worth an hour

Each of these is one feature people pay a monthly fee for, cut to a slice that fits one sitting.
No brand names. The size is for the slice as written, not for the app it came from.
"Cannot rebuild" is what the original owns and you leave alone. "Hard part" is where the hour goes.

## 1. Screen recorder: record and get a share link

- Rebuild: press record, pick a screen or window, stop, land on a page with a link you can send.
- Size: S.
- Cannot rebuild: their CDN and video processing at scale, viewer analytics, team libraries.
- Hard part: the browser owns the screen picker and needs a user gesture. Large files in one POST are fine locally and wrong on a serverless host.

## 2. Booking link: one page where people pick a slot

- Rebuild: you set weekly availability, visitors see open slots in their time zone, pick one, both of you get a confirmation.
- Size: S for one calendar you type in. M once it reads your real calendar.
- Cannot rebuild: calendar provider integrations at their reliability, SMS reminders, payment collection.
- Hard part: time zones. Store UTC, render in the visitor's zone, test a day when clocks change.

## 3. Link-in-bio page: one page of links with click counts

- Rebuild: a public page at a slug, an ordered list of links, a click count per link, an edit screen.
- Size: S.
- Cannot rebuild: their domain's reach, platform verification badges, their analytics breakdowns by referrer.
- Hard part: redirecting through your own route to count the click without slowing the visitor. Bots inflate counts; decide what you count.

## 4. Social post queue: write now, post later, one account

- Rebuild: a composer, a queue with dates, a status per post (queued, posted, failed), one platform.
- Size: M. The platform API approval alone can take longer than an hour.
- Cannot rebuild: their platform partner access, multi-account inboxes, best-time suggestions built on their data.
- Hard part: the scheduler. Locally a loop in the dev server is enough; hosted needs a cron and a retry rule.

## 5. Habit tracker: tick a box a day, see the streak

- Rebuild: a list of habits, a 7 column week grid, tap to tick, streak count per habit.
- Size: S.
- Cannot rebuild: their wearable integrations, community challenges, long-term stats across devices.
- Hard part: the 7 column grid at 390 px wide. Children need `min-width: 0` or chips push the grid off screen. "Today" depends on the user's zone, not the server's.

## 6. Invoice generator: fill a form, get a PDF with a number

- Rebuild: client, line items, tax rate, sequential invoice number, a printable page, a PDF via the browser's print.
- Size: S for the page and print to PDF. M if you need a server-rendered PDF file.
- Cannot rebuild: payment collection, bank reconciliation, tax filing integrations, their e-invoicing registrations.
- Hard part: the number must never repeat or skip. Use a single counter row and a transaction, not max plus one.

## 7. URL shortener with stats: short link, click count by day

- Rebuild: paste a long URL, get a short one, a page with clicks per day for the last 30 days.
- Size: S.
- Cannot rebuild: a short branded domain with trust, link safety scanning, QR analytics at scale.
- Hard part: a redirect route that writes a row and still returns in a few milliseconds. Use a 302, not a 301, so stats keep working.

## 8. Form builder: a few field types, a share link, a results table

- Rebuild: text, choice, checkbox fields; a public fill page; a results table with CSV export.
- Size: M. The editor is more screens than it looks.
- Cannot rebuild: their template library, payment fields, spam protection trained on their traffic, integrations marketplace.
- Hard part: storing answers for a schema that changes after answers exist. Store answers as JSON per response and keep a copy of the field list with each form version.

## 9. Newsletter signup page: an email box, a list, a CSV export

- Rebuild: a public page with one input, a list of subscribers with date, an unsubscribe link, CSV export.
- Size: S for collecting. Sending is a different feature and a different size.
- Cannot rebuild: their sending reputation and deliverability, their templates, their compliance tooling.
- Hard part: double opt-in needs sending one email. Locally, log the confirmation link to the console and click it yourself. Hosted, you need a transactional email provider.

## 10. Kanban board: three columns, drag a card, it stays

- Rebuild: one board, three columns, add and edit cards, drag between columns, order survives a refresh.
- Size: S for one board and one person. M for shared boards.
- Cannot rebuild: real time multiplayer at their smoothness, automations, the integrations ecosystem.
- Hard part: ordering. Store a sortable position per card (fractional index or a gap sequence) and write it on every drop. Keyboard move (select, arrow, enter) is part of the must list, not a could.

## How to use this list

Pick one. Run `clone-size` on the real app you pay for and see whether it agrees with the size here.
If it says L or XL, the slice is too big; cut it until it says S, then run the hour.
