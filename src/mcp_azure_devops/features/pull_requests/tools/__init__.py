"""
Pull request tools package for Azure DevOps MCP.

This module registers all pull request tools with the MCP server.
"""
from mcp_azure_devops.features.pull_requests.tools import (
    create,
    read,
    update,
    comments,
    work_items
)


def register_tools(mcp) -> None:
    """
    Register all pull request tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    create.register_tools(mcp)
    read.register_tools(mcp)
    update.register_tools(mcp)
    comments.register_tools(mcp)
    work_items.register_tools(mcp)
