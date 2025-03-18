"""
Azure DevOps MCP Server

A simple MCP server that exposes Azure DevOps capabilities.
"""
import argparse
from mcp.server.fastmcp import FastMCP
from mcp_azure_devops.features.work_items import resources as work_item_resources
from mcp_azure_devops.features.work_items import tools as work_item_tools

# Create a FastMCP server instance with a name
mcp = FastMCP("Azure DevOps")

# Register work item resources and tools
work_item_resources.register_resources(mcp)
work_item_tools.register_tools(mcp)

def main():
    """Entry point for the command-line script."""
    parser = argparse.ArgumentParser(description="Run the Azure DevOps MCP server")
    # Add more command-line arguments as needed
    
    args = parser.parse_args()
    
    # Register all resources and tools
    # work_items.register_resources(mcp)
    # ... register other resources and tools
    
    # Start the server
    mcp.run()

if __name__ == "__main__":
    main()
