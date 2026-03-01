# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Parallel AI web intelligence tools.

Exposes Parallel's Chat, Search, and Extract APIs as MCP tools.
Parallel can access real-time web data including X/Twitter profiles,
social media, news, documentation, and any public web content.

API docs: https://docs.parallel.ai

Auth notes:
  - Chat API uses Authorization: Bearer {key}
  - Search/Extract APIs use x-api-key: {key} + beta header
  Two separate Connections handle this transparently.
"""

from __future__ import annotations

from typing import Any

from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.types import ToolAnnotations

from parallel.types import (
    ChatModel,
    ChatResult,
    ExtractHit,
    ExtractResult,
    SearchHit,
    SearchResult,
)

# --- Connections ---

_BASE_URL = "https://api.parallel.ai"

parallel_chat_conn = Connection(
    name="parallel_chat",
    secrets=SecretKeys(token="PARALLEL_API_KEY"),
    base_url=_BASE_URL,
    auth_header_format="Bearer {api_key}",
)

parallel_web_conn = Connection(
    name="parallel_web",
    secrets=SecretKeys(token="PARALLEL_API_KEY"),
    base_url=_BASE_URL,
    auth_header_name="x-api-key",
    auth_header_format="{api_key}",
)

parallel_connections = [parallel_chat_conn, parallel_web_conn]


# --- Transport ---


async def _dispatch_chat(body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """Dispatch to Parallel Chat API. Returns (body, error)."""
    ctx = get_context()
    resp = await ctx.dispatch(
        "parallel_chat",
        HttpRequest(method=HttpMethod.POST, path="/chat/completions", body=body),
    )
    if resp.success and resp.response is not None:
        raw = resp.response.body
        return raw if isinstance(raw, dict) else {}, None
    return {}, resp.error.message if resp.error else "Chat request failed"


async def _dispatch_web(path: str, body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """Dispatch to Parallel Search/Extract API. Returns (body, error)."""
    ctx = get_context()
    resp = await ctx.dispatch(
        "parallel_web",
        HttpRequest(
            method=HttpMethod.POST,
            path=path,
            body=body,
            headers={"parallel-beta": "search-extract-2025-10-10"},
        ),
    )
    if resp.success and resp.response is not None:
        raw = resp.response.body
        return raw if isinstance(raw, dict) else {}, None
    return {}, resp.error.message if resp.error else "Web request failed"


# --- Chat ---


@tool(
    description=(
        "Ask a question with real-time web-grounded answers. "
        "Parallel searches the web and synthesizes an answer with citations. "
        "Great for factual questions, current events, social media lookups, and research."
    ),
    tags=["chat", "search", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def parallel_ask(
    question: str,
    model: ChatModel = ChatModel.speed,
) -> ChatResult:
    """Ask a web-grounded question.

    Args:
        question: Natural language question (web search is automatic)
        model: Model tier -- speed (fastest), lite, base, core (most capable)

    Returns:
        ChatResult with answer text and citation basis

    """
    raw, error = await _dispatch_chat(
        {
            "model": model,
            "messages": [{"role": "user", "content": question}],
            "stream": False,
        }
    )
    if error:
        return ChatResult(success=False, error=error)
    choices = raw.get("choices", [])
    answer = choices[0]["message"]["content"] if choices else None
    return ChatResult(
        success=True,
        answer=answer,
        model=raw.get("model"),
        basis=raw.get("basis", []),
    )


# --- Search ---


@tool(
    description=(
        "Search the web with an objective and specific queries. "
        "Returns relevant URLs with excerpts. "
        "Use for finding articles, social profiles, documentation, data, or anything on the public web."
    ),
    tags=["search", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def parallel_search(
    objective: str,
    search_queries: list[str],
    max_results: int = 10,
) -> SearchResult:
    """Search the web.

    Args:
        objective: High-level goal describing what you're looking for
        search_queries: Specific search queries to execute (1-5 recommended)
        max_results: Maximum results to return (1-20, default 10)

    Returns:
        SearchResult with typed SearchHit objects

    """
    raw, error = await _dispatch_web(
        "/v1beta/search",
        {
            "objective": objective,
            "search_queries": search_queries[:5],
            "max_results": max(1, min(20, max_results)),
            "excerpts": {"max_chars_per_result": 3000},
        },
    )
    if error:
        return SearchResult(success=False, error=error)
    return SearchResult(
        success=True,
        search_id=raw.get("search_id"),
        results=[
            SearchHit(
                url=hit["url"],
                title=hit.get("title"),
                publish_date=hit.get("publish_date"),
                excerpts=hit.get("excerpts", []),
            )
            for hit in raw.get("results", [])
        ],
    )


# --- Extract ---


@tool(
    description=(
        "Extract structured content from one or more URLs. "
        "Can scrape web pages, social media profiles (including X/Twitter), articles, docs, etc. "
        "Returns markdown-formatted content with optional full page text."
    ),
    tags=["extract", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def parallel_extract(
    urls: list[str],
    objective: str | None = None,
    full_content: bool = False,
) -> ExtractResult:
    """Extract content from URLs.

    Args:
        urls: URLs to extract content from (1-10)
        objective: Optional focus for extraction (e.g., "Extract follower count and bio")
        full_content: If True, return full page content in addition to excerpts

    Returns:
        ExtractResult with typed ExtractHit objects

    """
    body: dict[str, Any] = {
        "urls": urls[:10],
        "excerpts": True,
        "full_content": full_content,
    }
    if objective:
        body["objective"] = objective
    raw, error = await _dispatch_web("/v1beta/extract", body)
    if error:
        return ExtractResult(success=False, error=error)
    return ExtractResult(
        success=True,
        extract_id=raw.get("extract_id"),
        results=[
            ExtractHit(
                url=hit["url"],
                title=hit.get("title"),
                publish_date=hit.get("publish_date"),
                excerpts=hit.get("excerpts", []),
                full_content=hit.get("full_content"),
            )
            for hit in raw.get("results", [])
        ],
    )


# --- Export ---

parallel_tools = [
    parallel_ask,
    parallel_search,
    parallel_extract,
]
