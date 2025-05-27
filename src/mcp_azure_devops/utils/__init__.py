from mcp_azure_devops.utils.conventions_promp import register_prompt


def register_all_prompts(mcp):
    """
    Register prompts with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    # Register prompts here
    register_prompt(mcp)
    