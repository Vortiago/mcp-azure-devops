# Teams feature package for Azure DevOps MCP
from mcp_azure_devops.features.teams import tools


def register(mcp):
    """
    Register all teams components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
