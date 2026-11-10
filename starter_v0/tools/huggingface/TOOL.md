---
name: huggingface
track: bonus
kind: live_api
provider: Hugging Face Hub API (models)
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# huggingface

Searches models on the Hugging Face Hub (open-weight model releases). No API key.

- `sort`: `downloads` (default), `likes`, or `lastModified` (recently updated); anything else
  falls back to `downloads`.
- `limit`: 1–20, default 5.
- Each item: model id as `title`, `summary` = pipeline tag (e.g. `text-generation`),
  `metrics` = downloads / likes.
- Empty `query` returns an error dict without calling the network.
