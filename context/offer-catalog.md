# offer catalog (derived)

The catalog is no longer hand-maintained here. `hooks-wayfinder` **derives** it at
session start by scanning per-item frontmatter across `content/` (`id`, `category`,
`headline`, `try_now`, `trigger`, `signals`, `action`), filters out anything in
the decline file, and injects a compact index — plus the current bulletin in
packet shape — **ephemerally on your first message**. So the live menu arrives in
context; it is not always-on here.

When you see an offer's **trigger**, make the **offer** via propose→show→ack→act,
then run its **action** on ack. The hook may also drop a single conservative
"possible fit" nudge for an offer whose `signals.prompt_matches` matched — treat
it as a hint to propose, never as permission to act.

## Bodies come from the packet's `action` — never from a file search

A packet's `action` is the ONE authoritative way to show its body. Run it
**exactly as written**, including its `@namespace:` prefix — which may point to a
**different** bundle (e.g. `@made-support:…`), not wayfinder's own `content/`.
Never glob, grep, or search the filesystem for a packet's file, and never guess a
path from wayfinder's cache dir. The injected menu is authoritative about what
**exists**: if an item is on it, it exists — never tell the user a packet
"doesn't exist" or "isn't actionable" because your own file search missed it.
Follow its `action`.

To add or change offers: edit the item's frontmatter under `content/` (or add a
new `content/<category>/<id>.md`). Do not maintain a parallel list here.
