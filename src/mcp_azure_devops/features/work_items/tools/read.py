"""
Read operations for Azure DevOps work items.

This module provides MCP tools for retrieving work item information.
"""
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from mcp_azure_devops.features.work_items.common import get_work_item_client, AzureDevOpsClientError
from mcp_azure_devops.features.work_items.formatting import format_work_item

def _get_work_item_impl(item_id: int, wit_client: WorkItemTrackingClient) -> str:
    """
    Implementation of work item retrieval.
    
    Args:
        item_id: The work item ID
        wit_client: Work item tracking client
            
    Returns:
        Formatted string containing work item information
    """
    try:
        work_item = wit_client.get_work_item(item_id, expand="all")
        return format_work_item(work_item)
    except Exception as e:
        return f"Error retrieving work item {item_id}: {str(e)}"

def register_tools(mcp) -> None:
    """
    Register work item read tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_work_item(id: int) -> str:
        """
        Get detailed information about a work item.
        
        Args:
            id: The work item ID
            
        Returns:
            Formatted string containing comprehensive work item information
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_impl(id, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
