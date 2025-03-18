"""
Main entry point for running the MCP Azure DevOps server as a module.

This allows running the server with:
    python -m mcp_azure_devops
"""
from mcp_azure_devops.server import main

if __name__ == "__main__":
    main()
