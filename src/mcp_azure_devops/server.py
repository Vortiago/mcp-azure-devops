"""
Azure DevOps MCP Server

A simple MCP server that exposes Azure DevOps capabilities.
"""
from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance with a name
mcp = FastMCP("Azure DevOps")

# For now, this server only provides capabilities without any implementation
# Later, we will add resources, tools, and prompts for Azure DevOps services

if __name__ == "__main__":
    mcp.run()