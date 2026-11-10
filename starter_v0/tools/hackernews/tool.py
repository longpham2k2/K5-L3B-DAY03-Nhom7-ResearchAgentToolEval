from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, _clamp, domain, err

ENDPOINTS = {
    "relevance": "https://hn.algolia.com/api/v1/search",
    "date": "https://hn.algolia.com/api/v1/search_by_date",
}


def hackernews_search(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("Empty query")
        sort = sort if sort in ENDPOINTS else "relevance"
        limit = _clamp(limit, 5, 20)
        response = requests.get(
            ENDPOINTS[sort],
            params={"query": query, "tags": "story", "hitsPerPage": limit},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        hits = (response.json() or {}).get("hits") or []
        items = []
        for hit in hits[:limit]:
            discussion = f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            url = hit.get("url") or discussion
            items.append({
                "title": hit.get("title"),
                "url": url,
                "source": domain(url) or "news.ycombinator.com",
                "discussion_url": discussion,
                "date": hit.get("created_at"),
                "metrics": {"points": hit.get("points"), "comments": hit.get("num_comments")},
            })
        return {"tool": "hackernews_search", "query": query, "sort": sort, "items": items}
    except Exception as exc:
        return err("hackernews_search", exc)
