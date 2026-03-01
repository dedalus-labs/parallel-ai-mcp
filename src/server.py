# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""MCP server entrypoint."""

import os

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from parallel import parallel_connections, parallel_tools


def create_server() -> MCPServer:
    """Create MCP server with current env config."""
    as_url = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    return MCPServer(
        name="parallel-mcp",
        connections=parallel_connections,
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=as_url,
    )


async def main() -> None:
    """Start MCP server."""
    server = create_server()
    server.collect(*parallel_tools)
    await server.serve(port=8081)
