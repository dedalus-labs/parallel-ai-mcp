# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Sample MCP client demonstrating credential encryption and JIT token exchange.

Environment variables:
    DEDALUS_API_KEY: Your Dedalus API key (dsk_*)
    DEDALUS_API_URL: Product API base URL
    DEDALUS_AS_URL: Authorization server URL (for encryption key)
    PARALLEL_API_KEY: Parallel AI API key
"""

import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from dedalus_labs import AsyncDedalus, DedalusRunner
from dedalus_mcp.auth import SecretValues

from parallel import parallel_chat_conn, parallel_web_conn


class MissingEnvError(ValueError):
    """Required environment variable not set."""


def get_env(key: str) -> str:
    """Get required env var or raise."""
    val = os.getenv(key)
    if not val:
        raise MissingEnvError(key)
    return val


API_URL = get_env("DEDALUS_API_URL")
AS_URL = get_env("DEDALUS_AS_URL")
DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY")
PARALLEL_KEY = os.getenv("PARALLEL_API_KEY", "")

parallel_chat_secrets = SecretValues(parallel_chat_conn, token=PARALLEL_KEY)
parallel_web_secrets = SecretValues(parallel_web_conn, token=PARALLEL_KEY)


async def run_with_runner() -> None:
    """Demo using DedalusRunner (handles multi-turn, aggregates results)."""
    client = AsyncDedalus(api_key=DEDALUS_API_KEY, base_url=API_URL, as_base_url=AS_URL)
    runner = DedalusRunner(client)

    result = await runner.run(
        input="How many followers does @WindsorNguyen have on X/Twitter?",
        model="openai/gpt-4.1",
        mcp_servers=["windsor/parallel-mcp"],
        credentials=[parallel_chat_secrets, parallel_web_secrets],
    )

    print("=== Model Output ===")
    print(result.output)

    if result.mcp_results:
        print("\n=== MCP Tool Results ===")
        for r in result.mcp_results:
            print(f"  {r.tool_name} ({r.duration_ms}ms): {str(r.result)[:200]}")


async def run_raw() -> None:
    """Demo using raw client (single request, full control)."""
    client = AsyncDedalus(api_key=DEDALUS_API_KEY, base_url=API_URL, as_base_url=AS_URL)

    resp = await client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": "How many followers does @WindsorNguyen have on X/Twitter?",
            }
        ],
        mcp_servers=["windsor/parallel-mcp"],
        credentials=[parallel_chat_secrets, parallel_web_secrets],
    )

    print("=== Model Output ===")
    print(resp.choices[0].message.content)

    if resp.mcp_tool_results:
        print("\n=== MCP Tool Results ===")
        for r in resp.mcp_tool_results:
            print(f"  {r.tool_name} ({r.duration_ms}ms): {str(r.result)[:200]}")


async def main() -> None:
    """Run both demo modes."""
    print("=" * 60)
    print("DedalusRunner")
    print("=" * 60)
    await run_with_runner()

    print("\n" + "=" * 60)
    print("Raw Client")
    print("=" * 60)
    await run_raw()


if __name__ == "__main__":
    asyncio.run(main())
