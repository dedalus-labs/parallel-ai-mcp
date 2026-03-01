# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Shared pytest fixtures for parallel-mcp tests."""

from __future__ import annotations

import os

import pytest
from dedalus_mcp.testing import ConnectionTester
from dotenv import load_dotenv

from parallel import parallel_chat_conn, parallel_web_conn


@pytest.fixture(scope="session")
def parallel_chat_tester() -> ConnectionTester:
    """Return a locally configured ConnectionTester for Parallel Chat API."""
    load_dotenv()
    if not os.getenv("PARALLEL_API_KEY"):
        pytest.skip("PARALLEL_API_KEY not set; skipping live Parallel connection tests")
    return ConnectionTester.from_env(parallel_chat_conn)


@pytest.fixture(scope="session")
def parallel_web_tester() -> ConnectionTester:
    """Return a locally configured ConnectionTester for Parallel Search/Extract API."""
    load_dotenv()
    if not os.getenv("PARALLEL_API_KEY"):
        pytest.skip("PARALLEL_API_KEY not set; skipping live Parallel connection tests")
    return ConnectionTester.from_env(parallel_web_conn)
