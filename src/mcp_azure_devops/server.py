"""
Azure DevOps MCP Server

A simple MCP server that exposes Azure DevOps capabilities.
"""
from mcp.server.fastmcp import FastMCP
from mcp_azure_devops.resources import work_items

# Create a FastMCP server instance with a name
mcp = FastMCP("Azure DevOps")

# Register work item resources
work_items.register_resources(mcp)

if __name__ == "__main__":
    mcp.run()
