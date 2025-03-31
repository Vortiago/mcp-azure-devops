# Projects feature package for Azure DevOps MCP
from mcp_azure_devops.features.projects import tools


def register(mcp):
    """
    Register all projects components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
