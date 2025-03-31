"""
Work item tools for Azure DevOps.
"""
from mcp_azure_devops.features.work_items.tools import (
    comments,
    create,
    query,
    read,
)


def register_tools(mcp) -> None:
    """
    Register all work item tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    query.register_tools(mcp)
    read.register_tools(mcp)
    comments.register_tools(mcp)
    create.register_tools(mcp)
