# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Typed models for Parallel API tools.

Result types (frozen dataclasses):
  ChatResult     -- web-grounded chat answer with citations
  SearchHit      -- single search result with excerpts
  SearchResult   -- collection of search hits
  ExtractHit     -- single extracted page with content
  ExtractResult  -- collection of extracted pages

Enums:
  ChatModel      -- Parallel chat model tiers

Type aliases:
  JSONValue      -- recursive JSON value (pre-3.12 TypeAlias)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, TypeAlias

# --- JSON types ---

JSONValue: TypeAlias = str | int | float | bool | dict[str, Any] | list[Any] | None
"""Recursive JSON value. Uses Any for nesting (pre-PEP 695)."""


# --- Enums ---


class ChatModel(StrEnum):
    """Parallel chat model tiers, ordered by capability."""

    speed = "speed"
    lite = "lite"
    base = "base"
    core = "core"


# --- Chat ---


@dataclass(frozen=True, slots=True)
class ChatResult:
    """Web-grounded chat answer with optional citation basis."""

    success: bool
    answer: str | None = None
    model: str | None = None
    basis: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


# --- Search ---


@dataclass(frozen=True, slots=True)
class SearchHit:
    """Single search result with excerpts."""

    url: str
    title: str | None = None
    publish_date: str | None = None
    excerpts: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Collection of search hits."""

    success: bool
    search_id: str | None = None
    results: list[SearchHit] = field(default_factory=list)
    error: str | None = None


# --- Extract ---


@dataclass(frozen=True, slots=True)
class ExtractHit:
    """Single extracted page with structured content."""

    url: str
    title: str | None = None
    publish_date: str | None = None
    excerpts: list[str] = field(default_factory=list)
    full_content: str | None = None


@dataclass(frozen=True, slots=True)
class ExtractResult:
    """Collection of extracted pages."""

    success: bool
    extract_id: str | None = None
    results: list[ExtractHit] = field(default_factory=list)
    error: str | None = None
