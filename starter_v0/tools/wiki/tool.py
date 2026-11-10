from __future__ import annotations

import html
import re
from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, USER_AGENT, _clamp, err

LANGS = ("en", "vi")


def _strip_tags(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def wiki_search(query: str = "", lang: str = "en", limit: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("Empty query")
        lang = lang if lang in LANGS else "en"
        limit = _clamp(limit, 5, 20)
        response = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": query, "srlimit": limit, "format": "json", "utf8": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        pages = ((data or {}).get("query") or {}).get("search") or []
        items = [{
            "title": page.get("title"),
            "url": f"https://{lang}.wikipedia.org/wiki/{quote(page.get('title', '').replace(' ', '_'))}",
            "source": f"{lang}.wikipedia.org",
            "summary": _strip_tags(page.get("snippet", "")),
            "date": page.get("timestamp"),
        } for page in pages[:limit]]
        return {"tool": "wiki_search", "query": query, "lang": lang, "items": items}
    except Exception as exc:
        return err("wiki_search", exc)
