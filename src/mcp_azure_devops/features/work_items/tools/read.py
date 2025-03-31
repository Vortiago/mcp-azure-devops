"""
Read operations for Azure DevOps work items.

This module provides MCP tools for retrieving work item information.
"""
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)
from mcp_azure_devops.features.work_items.formatting import format_work_item


def _get_work_item_impl(item_id: int | list[int], 
                        wit_client: WorkItemTrackingClient) -> str:
    """
    Implementation of work item retrieval.
    
    Args:
        item_id: The work item ID or list of IDs
        wit_client: Work item tracking client
            
    Returns:
        Formatted string containing work item information
    """
    try:
        if isinstance(item_id, int):
            # Handle single work item
            work_item = wit_client.get_work_item(item_id, expand="all")
            return format_work_item(work_item)
        else:
            # Handle list of work items
            work_items = wit_client.get_work_items(ids=item_id,
                                                   error_policy="omit",
                                                   expand="all")
            
            if not work_items:
                return "No work items found."
                
            formatted_results = []
            for work_item in work_items:
                if work_item:  # Skip None values (failed retrievals)
                    formatted_results.append(format_work_item(work_item))
            
            if not formatted_results:
                return "No valid work items found with the provided IDs."
                
            return "\n\n".join(formatted_results)
    except Exception as e:
        if isinstance(item_id, int):
            return f"Error retrieving work item {item_id}: {str(e)}"
        else:
            return f"Error retrieving work items {item_id}: {str(e)}"

def register_tools(mcp) -> None:
    """
    Register work item read tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_work_item(id: int | list[int]) -> str:
        """
        Retrieves detailed information about one or multiple work items.
        
        Use this tool when you need to:
        - View the complete details of a specific work item
        - Examine the current state, assigned user, and other properties
        - Get information about multiple work items at once
        - Access the full description and custom fields of work items
        
        Args:
            id: The work item ID or a list of work item IDs
            
        Returns:
            Formatted string containing comprehensive information for the
            requested work item(s), including all system and custom fields,
            formatted as markdown with clear section headings
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_impl(id, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
