"""
Read operations for Azure DevOps work items.

This module provides MCP tools for retrieving work item information.
"""
from typing import Union
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)
from mcp_azure_devops.features.work_items.formatting import format_work_item


def _get_work_item_impl(
    item_id: Union[int, list[int]], 
    wit_client: WorkItemTrackingClient,
    detailed: bool = True
) -> str:
    """
    Implementation of work item retrieval.
    
    Args:
        item_id: The work item ID (integer) or list of work item IDs (integers).
                Examples: 502199 or [502199, 502200, 502201]
        wit_client: Work item tracking client
        detailed: Whether to return detailed information
            
    Returns:
        Formatted string containing work item information
    """
    try:
        if isinstance(item_id, int):
            # Handle single work item
            work_item = wit_client.get_work_item(item_id, expand="all")
            return format_work_item(work_item, detailed=detailed)
        else:
            # Handle list of work items
            item_ids = [int(id) for id in item_id]  # Ensure integer conversion
            work_items = wit_client.get_work_items(ids=item_ids,
                                                   error_policy="omit",
                                                   expand="all")
            
            if not work_items:
                return "No work items found."
                
            formatted_results = []
            for work_item in work_items:
                if work_item:  # Skip None values (failed retrievals)
                    formatted_results.append(format_work_item(work_item, detailed=detailed))
            
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
    def get_work_item(id: Union[int, list[int]]) -> str:
        """
        Retrieves detailed information about one or multiple work items.
        
        Use this tool when you need to:
        - View the complete details of a specific work item
        - Examine the current state, assigned user, and other properties
        - Get information about multiple work items at once
        - Access the full description and custom fields of work items
        
        Args:
            id: The work item ID (integer) or a list of work item IDs (integers).
                Examples: 502199 or [502199, 502200, 502201]
            
        Returns:
            Formatted string containing comprehensive information for the
            requested work item(s), including all system and custom fields,
            formatted as markdown with clear section headings
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_impl(id, wit_client, detailed=True)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_work_item_basic(id: int) -> str:
        """
        Retrieves basic information about a work item.
        
        Use this tool when you need to:
        - Quickly check the basic details of a specific work item
        - Verify the ID, title, type, and state of a work item
        - Get a concise summary without all details
        
        Args:
            id: The work item ID (integer). Example: 502199
                This should be a positive integer representing the unique
                identifier of the work item in Azure DevOps.
            
        Returns:
            Formatted string containing basic information for the
            requested work item, including ID, title, type, and state,
            formatted as markdown
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_impl(id, wit_client, detailed=False)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_work_item_details(id: int) -> str:
        """
        Retrieves comprehensive information about a work item.
        
        Use this tool when you need to:
        - View the complete details of a specific work item
        - Examine all fields, relationships, and properties
        - Get the full information for analysis or reference
        
        If the work item contains embedded images in its Description or other HTML fields 
        (indicated by <img src> tags), use the get_work_item_attachments tool to retrieve 
        and view these images separately. This is particularly useful for work items with 
        rich content like screenshots, diagrams, or other visual information.
        
        Args:
            id: The work item ID (integer). Example: 502199
                This should be a positive integer representing the unique
                identifier of the work item in Azure DevOps.
            
        Returns:
            Formatted string containing comprehensive information for the
            requested work item, including all fields and relationships,
            formatted as markdown
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_impl(id, wit_client, detailed=True)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
