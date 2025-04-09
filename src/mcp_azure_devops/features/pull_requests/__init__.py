# Pull Requests feature package for Azure DevOps MCP
from mcp_azure_devops.features.pull_requests import tools

def register(mcp):
    """
    Register all pull requests components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
