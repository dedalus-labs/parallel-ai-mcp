# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Live Parallel API connection probes."""

from __future__ import annotations

from http import HTTPStatus

import pytest
from dedalus_mcp.testing import ConnectionTester, HttpMethod
from dedalus_mcp.testing import TestRequest as Req


@pytest.mark.asyncio
async def test_chat_connection(parallel_chat_tester: ConnectionTester) -> None:
    """Chat API should accept a minimal completion request."""
    resp = await parallel_chat_tester.request(
        Req(
            method=HttpMethod.POST,
            path="/chat/completions",
            body={
                "model": "speed",
                "messages": [{"role": "user", "content": "Say hi in one word."}],
                "stream": False,
            },
        )
    )

    assert resp.success, f"Chat probe failed: status={resp.status} body={resp.body!r}"
    assert resp.status == HTTPStatus.OK
    assert resp.body is not None
    assert "choices" in resp.body


@pytest.mark.asyncio
async def test_search_connection(parallel_web_tester: ConnectionTester) -> None:
    """Search API should return results for a simple query."""
    resp = await parallel_web_tester.request(
        Req(
            method=HttpMethod.POST,
            path="/v1beta/search",
            headers={"parallel-beta": "search-extract-2025-10-10"},
            body={
                "objective": "Test search",
                "search_queries": ["Dedalus Labs YC"],
                "max_results": 1,
            },
        )
    )

    assert resp.success, f"Search probe failed: status={resp.status} body={resp.body!r}"
    assert resp.status == HTTPStatus.OK
    assert resp.body is not None
    assert "results" in resp.body


@pytest.mark.asyncio
async def test_extract_connection(parallel_web_tester: ConnectionTester) -> None:
    """Extract API should return content for a public URL."""
    resp = await parallel_web_tester.request(
        Req(
            method=HttpMethod.POST,
            path="/v1beta/extract",
            headers={"parallel-beta": "search-extract-2025-10-10"},
            body={
                "urls": ["https://example.com"],
                "excerpts": True,
                "full_content": False,
            },
        )
    )

    assert resp.success, f"Extract probe failed: status={resp.status} body={resp.body!r}"
    assert resp.status == HTTPStatus.OK
    assert resp.body is not None
    assert "results" in resp.body
