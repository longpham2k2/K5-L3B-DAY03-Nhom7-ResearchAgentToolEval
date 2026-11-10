---
name: wiki
track: bonus
kind: live_api
provider: Wikipedia (MediaWiki API)
requires_env: []
inputs: [query, lang, limit]
outputs: [items]
side_effect: false
---
# wiki

Searches Wikipedia for background / definition pages. No API key.

- `lang`: `en` or `vi`; anything else falls back to `en`.
- `limit`: 1–20, default 5 (strings like `"0"` or junk fall back to 5).
- Empty `query` returns an error dict without calling the network.
