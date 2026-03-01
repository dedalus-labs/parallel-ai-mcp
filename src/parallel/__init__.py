# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Parallel AI web intelligence MCP tools."""

from parallel.tools import (
    parallel_ask,
    parallel_chat_conn,
    parallel_connections,
    parallel_extract,
    parallel_search,
    parallel_tools,
    parallel_web_conn,
)
from parallel.types import (
    ChatModel,
    ChatResult,
    ExtractHit,
    ExtractResult,
    SearchHit,
    SearchResult,
)

__all__ = [
    # Connections
    "parallel_chat_conn",
    "parallel_web_conn",
    "parallel_connections",
    # Tools
    "parallel_ask",
    "parallel_search",
    "parallel_extract",
    "parallel_tools",
    # Types
    "ChatModel",
    "ChatResult",
    "SearchHit",
    "SearchResult",
    "ExtractHit",
    "ExtractResult",
]
