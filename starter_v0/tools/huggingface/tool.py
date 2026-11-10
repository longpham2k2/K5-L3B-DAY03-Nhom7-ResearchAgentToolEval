from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, USER_AGENT, _clamp, err

SORTS = ("downloads", "likes", "lastModified")


def hf_models(query: str = "", sort: str = "downloads", limit: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("Empty query")
        sort = sort if sort in SORTS else "downloads"
        limit = _clamp(limit, 5, 20)
        response = requests.get(
            "https://huggingface.co/api/models",
            params={"search": query, "sort": sort, "direction": -1, "limit": limit},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        models = response.json()
        if not isinstance(models, list):
            models = []
        items = []
        for model in models[:limit]:
            model_id = model.get("id") or model.get("modelId") or ""
            items.append({
                "title": model_id,
                "url": f"https://huggingface.co/{model_id}",
                "source": "huggingface.co",
                "summary": model.get("pipeline_tag") or "",
                "date": model.get("lastModified") or model.get("createdAt"),
                "metrics": {"downloads": model.get("downloads"), "likes": model.get("likes")},
            })
        return {"tool": "hf_models", "query": query, "sort": sort, "items": items}
    except Exception as exc:
        return err("hf_models", exc)
