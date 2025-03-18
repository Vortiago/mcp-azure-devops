"""
MCP Azure DevOps Server - A Model Context Protocol server for Azure DevOps
integration.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("mcp-azure-devops")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"