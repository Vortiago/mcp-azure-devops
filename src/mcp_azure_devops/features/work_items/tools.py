"""
Work item tools for Azure DevOps.

This module provides MCP tools for working with Azure DevOps work items.
"""
from typing import Optional, List
from azure.devops.v7_1.work_item_tracking.models import Wiql, WorkItem
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from mcp_azure_devops.utils.azure_client import get_connection
from mcp_azure_devops.features.work_items.common import get_work_item_client, AzureDevOpsClientError


def format_work_items(work_items: List[WorkItem]) -> str:
    """
    Format work items into readable strings.
    
    Args:
        work_items: List of work item objects to format
        
    Returns:
        Formatted string of work items
    """
    formatted_results = []
    for work_item in work_items:
        if work_item and work_item.fields is not None:
            item_type = work_item.fields.get("System.WorkItemType", "Unknown")
            item_id = work_item.id
            item_title = work_item.fields.get("System.Title", "Untitled")
            item_state = work_item.fields.get("System.State", "Unknown")
            
            formatted_results.append(
                f"{item_type} {item_id}: {item_title} ({item_state})"
            )
    
    return "\n".join(formatted_results)


def _query_work_items_impl(
    query: str, 
    top: int,
    wit_client: WorkItemTrackingClient
) -> str:
    """
    Implementation of query_work_items that operates with a client.
    
    Args:
        query: The WIQL query string
        top: Maximum number of results to return
        wit_client: Work item tracking client
            
    Returns:
        Formatted string containing work item details
    """
    
    # Create the WIQL query
    wiql = Wiql(query=query)
    
    # Execute the query
    wiql_results = wit_client.query_by_wiql(wiql, top=top).work_items
    
    if not wiql_results:
        return "No work items found matching the query."
    
    # Get the work items from the results
    work_item_ids = [int(res.id) for res in wiql_results]
    work_items = wit_client.get_work_items(ids=work_item_ids, error_policy="omit")
    
    return format_work_items(work_items)


def register_tools(mcp) -> None:
    """
    Register work item tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def query_work_items(
        query: str, 
        top: Optional[int]
    ) -> str:
        """
        Query work items using WIQL.
        
        Args:
            query: The WIQL query string
            top: Maximum number of results to return (default: 30)
                
        Returns:
            Formatted string containing work item details
        """
        try:
            wit_client = get_work_item_client()
            # Ensure top is not None before passing to implementation
            return _query_work_items_impl(query, top or 30, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
