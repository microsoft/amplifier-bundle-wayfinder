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

To add or change offers: edit the item's frontmatter under `content/` (or add a
new `content/<category>/<id>.md`). Do not maintain a parallel list here.
