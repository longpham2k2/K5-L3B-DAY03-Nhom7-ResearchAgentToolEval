---
name: hackernews
track: bonus
kind: live_api
provider: Hacker News (Algolia API)
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# hackernews

Searches Hacker News stories (tech community discussion). No API key.

- `sort`: `relevance` (default) or `date` (newest first); anything else falls back to `relevance`.
- `limit`: 1–20, default 5.
- Each item has `url` (the linked article, or the HN thread if it is a text post)
  and `discussion_url` (the HN comment thread).
- Empty `query` returns an error dict without calling the network.
