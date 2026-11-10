"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import requests

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401
from tools._shared import _clamp


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = TOOL_FUNCTIONS["clarify"](question="Bạn muốn xem nguồn nào?", response_type="choice", options=["Twitter", "Web"])

    assert result["options"] == ["Twitter", "Web"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [{"title": "a", "section": "A"}, {"title": "b", "section": "B"}, {"title": "c", "section": "A"}]

    markdown = TOOL_FUNCTIONS["format"](items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    assert markdown.index("- a") < markdown.index("- c") < markdown.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"Tin {i}"} for i in range(3)]

    markdown = TOOL_FUNCTIONS["format"](items=items, template="thread")["markdown"]

    assert [line[:2] for line in markdown.split("\n\n")] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    assert TOOL_FUNCTIONS["format"](items=None)["item_count"] == 0
    assert TOOL_FUNCTIONS["format"](items=[], template="brief")["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "456")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "tok123" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "456"
    assert calls[0]["json"]["text"] == "Bản tin"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))

    result = TOOL_FUNCTIONS["lookup"](query="OpenAI", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert result["items"] == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/p"},
    }}))

    result = TOOL_FUNCTIONS["fetch"](url="https://www.example.com/p")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/p"
    assert calls[0]["headers"]["Authorization"] == "Bearer fc-key"
    assert result["items"][0] == {
        "title": "T", "url": "https://www.example.com/p", "source": "example.com", "summary": "# Hello",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    summary = TOOL_FUNCTIONS["fetch"](url="https://example.com")["items"][0]["summary"]

    assert len(summary) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    raw = [{"text": "no id", "screen_name": "sama"}] + [
        {"tweet_id": str(i), "text": f"t{i}", "screen_name": "sama"} for i in range(1, 7)
    ]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert [item["url"] for item in result["items"]] == [
        "https://x.com/sama/status/1", "https://x.com/sama/status/2", "https://x.com/sama/status/3",
    ]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    calls = fake_http(FakeResponse({"timeline": []}))

    result = TOOL_FUNCTIONS["social_search"](query="gpt-5", search_type="Top")

    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "gpt-5", "search_type": "Top"}
    assert result["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert TOOL_FUNCTIONS["policy"](query="")["results"] == []
    assert TOOL_FUNCTIONS["policy"](query="the and of")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = TOOL_FUNCTIONS["policy"](query="API keys credentials", policy_area="data_privacy", top_k=5)["results"]

    assert results
    assert all(item["policy_area"] == "data_privacy" for item in results)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = TOOL_FUNCTIONS["policy"](query="injection probe", policy_area="source_citation")["results"]

    probe = next(item for item in results if item["section"] == "Injection probe")
    assert any("ignore the citation policy" in line for line in probe["untrusted_text"])
    assert all("ignore the citation policy" not in item["facts"] for item in results)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

wiki = TOOL_FUNCTIONS["wiki"]
hackernews = TOOL_FUNCTIONS["hackernews"]
github = TOOL_FUNCTIONS["github"]
huggingface = TOOL_FUNCTIONS["huggingface"]


def test_wiki_maps_pages_in_search_order(fake_http) -> None:
    calls = fake_http(FakeResponse({"query": {"search": [
        {"title": "Large language model", "snippet": 'A <span class="searchmatch">LLM</span> is &amp; more', "timestamp": "2026-11-01T00:00:00Z"},
        {"title": "Transformer (deep learning)", "snippet": "Architecture", "timestamp": "2026-10-01T00:00:00Z"},
    ]}}))

    result = wiki(query="LLM", lang="en", limit=2)

    assert calls[0]["url"] == "https://en.wikipedia.org/w/api.php"
    assert calls[0]["params"]["list"] == "search"
    assert calls[0]["params"]["srsearch"] == "LLM"
    assert calls[0]["params"]["srlimit"] == 2
    assert calls[0]["headers"]["User-Agent"]
    assert [item["title"] for item in result["items"]] == ["Large language model", "Transformer (deep learning)"]
    assert result["items"][0]["url"] == "https://en.wikipedia.org/wiki/Large_language_model"
    assert result["items"][1]["url"] == "https://en.wikipedia.org/wiki/Transformer_%28deep_learning%29"
    assert result["items"][0]["summary"] == "A LLM is & more"


def test_wiki_bad_lang_and_limit_are_sanitized(fake_http) -> None:
    calls = fake_http(FakeResponse({"query": {"search": []}}))

    result = wiki(query="LLM", lang="fr", limit=500)

    assert calls[0]["url"] == "https://en.wikipedia.org/w/api.php"
    assert calls[0]["params"]["srlimit"] == 20
    assert result["lang"] == "en"


def test_wiki_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({}))

    result = wiki(query="   ")

    assert result["error"] == "ValueError"
    assert calls == []


def test_wiki_http_503_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    result = wiki(query="LLM")

    assert result["error"] == "HTTPError"
    assert "503" in result["message"]


def test_hackernews_maps_hits_and_falls_back_to_thread_url(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [
        {"objectID": "101", "title": "Show HN: Agent eval kit", "url": "https://www.example.com/a",
         "points": 120, "num_comments": 45, "created_at": "2026-11-09T10:00:00Z"},
        {"objectID": "102", "title": "Ask HN: Best eval set?", "url": None,
         "points": 10, "num_comments": 3, "created_at": "2026-11-08T10:00:00Z"},
    ]}))

    result = hackernews(query="LLM agents", sort="date", limit=2)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"] == {"query": "LLM agents", "tags": "story", "hitsPerPage": 2}
    assert result["items"][0] == {
        "title": "Show HN: Agent eval kit", "url": "https://www.example.com/a", "source": "example.com",
        "discussion_url": "https://news.ycombinator.com/item?id=101",
        "date": "2026-11-09T10:00:00Z", "metrics": {"points": 120, "comments": 45},
    }
    assert result["items"][1]["url"] == "https://news.ycombinator.com/item?id=102"
    assert result["items"][1]["source"] == "news.ycombinator.com"


def test_hackernews_bad_sort_and_limit_are_sanitized(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    result = hackernews(query="LLM", sort="weird", limit="abc")

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"]["hitsPerPage"] == 5
    assert result["sort"] == "relevance"


def test_hackernews_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({}))

    assert hackernews(query="")["error"] == "ValueError"
    assert calls == []


def test_hackernews_network_down_returns_error_dict(fake_http) -> None:
    fake_http(requests.ConnectionError("offline"))

    result = hackernews(query="LLM")

    assert result["error"] == "ConnectionError"
    assert result["tool"] == "hackernews_search"


def test_github_sends_search_request_and_maps_repos(fake_http) -> None:
    calls = fake_http(FakeResponse({"total_count": 42, "items": [
        {"full_name": "org/agent-kit", "html_url": "https://github.com/org/agent-kit", "description": "Agent toolkit",
         "stargazers_count": 1500, "language": "Python", "updated_at": "2026-11-09T00:00:00Z"},
    ]}))

    result = github(query="llm agent", sort="stars", limit=3)

    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {"q": "llm agent", "per_page": 3, "sort": "stars", "order": "desc"}
    assert calls[0]["headers"]["Accept"] == "application/vnd.github+json"
    assert calls[0]["headers"]["User-Agent"]
    assert result["total_count"] == 42
    assert result["items"][0] == {
        "title": "org/agent-kit", "url": "https://github.com/org/agent-kit", "source": "github.com",
        "summary": "Agent toolkit", "date": "2026-11-09T00:00:00Z",
        "metrics": {"stars": 1500, "language": "Python"},
    }


def test_github_bad_sort_and_limit_are_sanitized(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    result = github(query="llm", sort="weird", limit=500)

    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 20
    assert result["sort"] == "stars"


def test_github_best_match_omits_sort_param(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    github(query="llm", sort="best_match")

    assert "sort" not in calls[0]["params"]
    assert "order" not in calls[0]["params"]


def test_github_rate_limit_403_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=403))

    result = github(query="llm")

    assert result["error"] == "HTTPError"
    assert "403" in result["message"]


def test_github_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({}))

    assert github(query=None)["error"] == "ValueError"
    assert calls == []


def test_huggingface_sends_request_and_maps_models(fake_http) -> None:
    calls = fake_http(FakeResponse([
        {"id": "org/tiny-llm", "pipeline_tag": "text-generation", "downloads": 9000, "likes": 120,
         "lastModified": "2026-11-05T00:00:00.000Z"},
    ]))

    result = huggingface(query="tiny llm", sort="likes", limit=2)

    assert calls[0]["url"] == "https://huggingface.co/api/models"
    assert calls[0]["params"] == {"search": "tiny llm", "sort": "likes", "direction": -1, "limit": 2}
    assert result["items"][0] == {
        "title": "org/tiny-llm", "url": "https://huggingface.co/org/tiny-llm", "source": "huggingface.co",
        "summary": "text-generation", "date": "2026-11-05T00:00:00.000Z",
        "metrics": {"downloads": 9000, "likes": 120},
    }


def test_huggingface_bad_sort_and_string_zero_limit_are_sanitized(fake_http) -> None:
    calls = fake_http(FakeResponse([]))

    result = huggingface(query="llm", sort="trending!!", limit="0")

    assert calls[0]["params"]["sort"] == "downloads"
    assert calls[0]["params"]["limit"] == 5
    assert result["sort"] == "downloads"


def test_huggingface_unexpected_payload_returns_empty_items(fake_http) -> None:
    fake_http(FakeResponse({"error": "something odd"}))

    result = huggingface(query="llm")

    assert result["items"] == []


def test_huggingface_http_503_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    assert huggingface(query="llm")["error"] == "HTTPError"


def test_huggingface_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse([]))

    assert huggingface(query="")["error"] == "ValueError"
    assert calls == []


def test_clamp_handles_string_zero_junk_and_cap() -> None:
    assert _clamp("0", 5, 100) == 5
    assert _clamp("abc", 5, 100) == 5
    assert _clamp(None, 5, 100) == 5
    assert _clamp(-3, 5, 100) == 5
    assert _clamp("7", 5, 100) == 7
    assert _clamp(500, 5, 100) == 100


def test_timeline_string_zero_limit_falls_back_to_default(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    raw = [{"tweet_id": str(i), "text": f"t{i}", "screen_name": "sama"} for i in range(8)]
    fake_http(FakeResponse({"timeline": raw}))

    assert len(TOOL_FUNCTIONS["timeline"](screenname="sama", limit="0")["items"]) == 5


def test_social_search_string_zero_limit_falls_back_to_default(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    raw = [{"tweet_id": str(i), "text": f"t{i}", "screen_name": "sama"} for i in range(8)]
    fake_http(FakeResponse({"timeline": raw}))

    assert len(TOOL_FUNCTIONS["social_search"](query="gpt", limit="0")["items"]) == 5


def test_lookup_string_zero_max_results_falls_back_to_default(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))

    TOOL_FUNCTIONS["lookup"](query="x", max_results="0")

    assert calls[0]["json"]["max_results"] == 5
