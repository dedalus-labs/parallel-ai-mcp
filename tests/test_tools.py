# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Unit tests for Parallel tool functions (monkeypatched, no network)."""

from __future__ import annotations

from typing import Any

import pytest

from parallel import (
    ChatModel,
    ChatResult,
    ExtractHit,
    ExtractResult,
    SearchHit,
    SearchResult,
    parallel_ask,
    parallel_extract,
    parallel_search,
)

# --- parallel_ask ---


@pytest.mark.asyncio
async def test_ask_passes_question_and_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """parallel_ask should forward question/model to _dispatch_chat."""
    captured: dict[str, Any] = {}

    async def fake_dispatch(body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        captured.update(body)
        return {
            "choices": [{"message": {"content": "42"}}],
            "model": "core",
            "basis": [{"url": "https://example.com"}],
        }, None

    monkeypatch.setattr("parallel.tools._dispatch_chat", fake_dispatch)
    result = await parallel_ask(question="meaning of life", model=ChatModel.core)

    assert isinstance(result, ChatResult)
    assert result.success
    assert result.answer == "42"
    assert result.model == "core"
    assert len(result.basis) == 1
    assert captured["model"] == "core"
    assert captured["messages"][0]["content"] == "meaning of life"
    assert captured["stream"] is False


@pytest.mark.asyncio
async def test_ask_surfaces_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """parallel_ask should propagate upstream errors as typed ChatResult."""

    async def fake_dispatch(_body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        return {}, "rate limited"

    monkeypatch.setattr("parallel.tools._dispatch_chat", fake_dispatch)
    result = await parallel_ask(question="anything")

    assert isinstance(result, ChatResult)
    assert not result.success
    assert result.error == "rate limited"
    assert result.answer is None


@pytest.mark.asyncio
async def test_ask_handles_empty_choices(monkeypatch: pytest.MonkeyPatch) -> None:
    """parallel_ask should handle empty choices gracefully."""

    async def fake_dispatch(_body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        return {"choices": [], "model": "speed", "basis": []}, None

    monkeypatch.setattr("parallel.tools._dispatch_chat", fake_dispatch)
    result = await parallel_ask(question="anything")

    assert result.success
    assert result.answer is None


# --- parallel_search ---


@pytest.mark.asyncio
async def test_search_builds_correct_request(monkeypatch: pytest.MonkeyPatch) -> None:
    """parallel_search should construct the expected payload and parse results."""
    captured: dict[str, Any] = {}

    async def fake_dispatch(path: str, body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        captured["path"] = path
        captured["body"] = body
        return {
            "search_id": "search_abc",
            "results": [
                {"url": "https://example.com", "title": "Test", "publish_date": "2026-01-01", "excerpts": ["hello"]},
            ],
        }, None

    monkeypatch.setattr("parallel.tools._dispatch_web", fake_dispatch)
    result = await parallel_search(
        objective="find docs",
        search_queries=["dedalus docs", "mcp tutorial"],
        max_results=5,
    )

    assert isinstance(result, SearchResult)
    assert result.success
    assert result.search_id == "search_abc"
    assert len(result.results) == 1
    assert isinstance(result.results[0], SearchHit)
    assert result.results[0].url == "https://example.com"
    assert result.results[0].excerpts == ["hello"]
    assert captured["path"] == "/v1beta/search"
    assert captured["body"]["objective"] == "find docs"
    assert captured["body"]["search_queries"] == ["dedalus docs", "mcp tutorial"]
    assert captured["body"]["max_results"] == 5


@pytest.mark.asyncio
async def test_search_clamps_max_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """max_results should be clamped to [1, 20]."""
    captured_bodies: list[dict[str, Any]] = []

    async def fake_dispatch(_path: str, body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        captured_bodies.append(body)
        return {"results": []}, None

    monkeypatch.setattr("parallel.tools._dispatch_web", fake_dispatch)

    await parallel_search(objective="x", search_queries=["q"], max_results=-5)
    await parallel_search(objective="x", search_queries=["q"], max_results=999)

    assert captured_bodies[0]["max_results"] == 1
    assert captured_bodies[1]["max_results"] == 20


@pytest.mark.asyncio
async def test_search_truncates_queries_to_five(monkeypatch: pytest.MonkeyPatch) -> None:
    """More than 5 queries should be silently truncated."""
    captured: dict[str, Any] = {}

    async def fake_dispatch(_path: str, body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        captured.update(body)
        return {"results": []}, None

    monkeypatch.setattr("parallel.tools._dispatch_web", fake_dispatch)
    await parallel_search(objective="x", search_queries=[f"q{i}" for i in range(10)])

    assert len(captured["search_queries"]) == 5


# --- parallel_extract ---


@pytest.mark.asyncio
async def test_extract_with_objective(monkeypatch: pytest.MonkeyPatch) -> None:
    """parallel_extract should include objective and parse typed results."""
    captured: dict[str, Any] = {}

    async def fake_dispatch(path: str, body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        captured["path"] = path
        captured["body"] = body
        return {
            "extract_id": "extract_xyz",
            "results": [
                {
                    "url": "https://x.com/WindsorNguyen",
                    "title": "Windsor Nguyen",
                    "excerpts": ["859 Followers"],
                    "full_content": "full page markdown",
                },
            ],
        }, None

    monkeypatch.setattr("parallel.tools._dispatch_web", fake_dispatch)
    result = await parallel_extract(
        urls=["https://x.com/WindsorNguyen"],
        objective="Get follower count",
        full_content=True,
    )

    assert isinstance(result, ExtractResult)
    assert result.success
    assert result.extract_id == "extract_xyz"
    assert len(result.results) == 1
    hit = result.results[0]
    assert isinstance(hit, ExtractHit)
    assert hit.url == "https://x.com/WindsorNguyen"
    assert hit.full_content == "full page markdown"
    assert captured["path"] == "/v1beta/extract"
    assert captured["body"]["objective"] == "Get follower count"
    assert captured["body"]["full_content"] is True


@pytest.mark.asyncio
async def test_extract_without_objective(monkeypatch: pytest.MonkeyPatch) -> None:
    """parallel_extract should omit objective key when None."""
    captured: dict[str, Any] = {}

    async def fake_dispatch(_path: str, body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        captured.update(body)
        return {"results": []}, None

    monkeypatch.setattr("parallel.tools._dispatch_web", fake_dispatch)
    await parallel_extract(urls=["https://example.com"])

    assert "objective" not in captured


@pytest.mark.asyncio
async def test_extract_truncates_urls_to_ten(monkeypatch: pytest.MonkeyPatch) -> None:
    """More than 10 URLs should be silently truncated."""
    captured: dict[str, Any] = {}

    async def fake_dispatch(_path: str, body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        captured.update(body)
        return {"results": []}, None

    monkeypatch.setattr("parallel.tools._dispatch_web", fake_dispatch)
    await parallel_extract(urls=[f"https://example.com/{i}" for i in range(20)])

    assert len(captured["urls"]) == 10
