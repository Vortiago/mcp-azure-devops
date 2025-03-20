# Azure DevOps MCP features package
from mcp_azure_devops.features import work_items
from mcp_azure_devops.features import projects

def register_all(mcp):
    """
    Register all features with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    work_items.register(mcp)
    projects.register(mcp)
