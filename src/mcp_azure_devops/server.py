"""
Azure DevOps MCP Server

A Model Context Protocol server that exposes Azure DevOps capabilities.

For detailed configuration options and usage examples, see the README.md file.

Required Environment Variables:
    AZURE_DEVOPS_PAT: Personal Access Token for Azure DevOps authentication
    AZURE_DEVOPS_ORGANIZATION_URL: Azure DevOps organization URL

Optional Environment Variables:
    FASTMCP_* variables can be used to configure server settings.
    See README.md for a complete list.
"""

import argparse
from enum import Enum

from mcp.server.fastmcp import FastMCP

from mcp_azure_devops.features import register_all
from mcp_azure_devops.utils import register_all_prompts


class TransportType(Enum):
    """Transport types supported by the MCP server"""

    STDIO = "stdio"  # Standard input/output transport
    SSE = "sse"  # Server-Sent Events transport
    STREAMABLE_HTTP = (
        "streamable-http"  # HTTP-based transport with streaming capabilities
    )


# Create a FastMCP server instance with a name
mcp = FastMCP("Azure DevOps")

# Register all features
register_all(mcp)
register_all_prompts(mcp)


def main():
    """Entry point for the command-line script.

    Command-line Arguments:
        --transport: Transport type to use (stdio, sse, streamable-http)

    See README.md for detailed configuration options and usage examples.
    """
    parser = argparse.ArgumentParser(
        description="Run the Azure DevOps MCP server",
        epilog="For detailed configuration options, see README.md",
    )
    parser.add_argument(
        "--transport",
        type=str,
        default=TransportType.STDIO.value,
        choices=[t.value for t in TransportType],
        help="Transport to use: %(choices)s",
    )

    args = parser.parse_args()

    # Start the server
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
