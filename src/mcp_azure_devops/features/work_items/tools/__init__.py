"""
Work item tools for Azure DevOps.
"""
from mcp_azure_devops.features.work_items.tools import (
    attachments,
    comments,
    create,
    process,
    query,
    read,
    templates,
    types,
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
    types.register_tools(mcp)
    templates.register_tools(mcp)
    process.register_tools(mcp)
    attachments.register_tools(mcp)
