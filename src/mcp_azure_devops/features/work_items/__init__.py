# Work items feature package for Azure DevOps MCP
from mcp_azure_devops.features.work_items import resources, tools

def register(mcp):
    """
    Register all work items components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    resources.register_resources(mcp)
    tools.register_tools(mcp)
