# Work items feature package for Azure DevOps MCP
from mcp_azure_devops.features.work_items import tools


def register(mcp):
    """
    Register all work items components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
