from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, USER_AGENT, _clamp, err

SORTS = ("stars", "updated", "best_match")


def github_search(query: str = "", sort: str = "stars", limit: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("Empty query")
        sort = sort if sort in SORTS else "stars"
        limit = _clamp(limit, 5, 20)
        params: dict[str, Any] = {"q": query, "per_page": limit}
        if sort != "best_match":
            params["sort"] = sort
            params["order"] = "desc"
        response = requests.get(
            "https://api.github.com/search/repositories",
            params=params,
            headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json() or {}
        items = [{
            "title": repo.get("full_name"),
            "url": repo.get("html_url"),
            "source": "github.com",
            "summary": repo.get("description") or "",
            "date": repo.get("updated_at"),
            "metrics": {"stars": repo.get("stargazers_count"), "language": repo.get("language")},
        } for repo in (data.get("items") or [])[:limit]]
        return {"tool": "github_search", "query": query, "sort": sort, "total_count": data.get("total_count"), "items": items}
    except Exception as exc:
        return err("github_search", exc)
