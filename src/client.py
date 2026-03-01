# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Sample MCP client for testing parallel-mcp server locally."""

import asyncio

from dedalus_mcp.client import MCPClient

SERVER_URL = "http://localhost:8081/mcp"


async def main() -> None:
    client = await MCPClient.connect(SERVER_URL)

    result = await client.list_tools()
    print(f"\nAvailable tools ({len(result.tools)}):\n")
    for t in result.tools:
        print(f"  {t.name}")
        if t.description:
            print(f"    {t.description[:80]}...")
        print()

    print("--- parallel_ask ---")
    answer = await client.call_tool(
        "parallel_ask",
        {"question": "How many X/Twitter followers does @WindsorNguyen have?"},
    )
    print(answer)
    print()

    print("--- parallel_search ---")
    results = await client.call_tool(
        "parallel_search",
        {
            "objective": "Find Windsor Nguyen's X/Twitter profile and follower count",
            "search_queries": ["WindsorNguyen Twitter followers", "Windsor Nguyen @WindsorNguyen X"],
        },
    )
    print(results)
    print()

    print("--- parallel_extract ---")
    content = await client.call_tool(
        "parallel_extract",
        {
            "urls": ["https://x.com/WindsorNguyen"],
            "objective": "Extract follower count, bio, and recent posts",
        },
    )
    print(content)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
