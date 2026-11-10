---
name: github
track: bonus
kind: live_api
provider: GitHub REST API (search/repositories)
requires_env: []
inputs: [query, sort, limit]
outputs: [items, total_count]
side_effect: false
---
# github

Searches public GitHub repositories (open-source projects, code releases). No API key;
unauthenticated search is rate-limited (~10 requests/minute) — a 403 comes back as an error dict.

- `sort`: `stars` (default), `updated`, or `best_match`; anything else falls back to `stars`.
- `limit`: 1–20, default 5.
- Empty `query` returns an error dict without calling the network.
