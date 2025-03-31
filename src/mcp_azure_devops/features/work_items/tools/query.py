"""
Query operations for Azure DevOps work items.

This module provides MCP tools for querying work items.
"""
from typing import Optional

from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.v7_1.work_item_tracking.models import Wiql

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)
from mcp_azure_devops.features.work_items.formatting import format_work_item


def _query_work_items_impl(query: str, top: int, 
                           wit_client: WorkItemTrackingClient) -> str:
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
    work_items = wit_client.get_work_items(ids=work_item_ids,
                                           expand="all",
                                           error_policy="omit")
    
    # Use the standard formatting for all work items
    formatted_results = []
    for work_item in work_items:
        if work_item:
            formatted_results.append(format_work_item(work_item))
    
    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register work item query tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def query_work_items(query: str, top: Optional[int] = None) -> str:
        """
        Searches for work items using Work Item Query Language (WIQL).
        
        Use this tool when you need to:
        - Find work items matching specific criteria
        - Search across projects for related tasks or bugs
        - Create dynamic reports based on work item attributes
        - Identify work items assigned to specific team members
        
        IMPORTANT: WIQL syntax is similar to SQL and allows you to query
        work items based on their fields. The query must follow Azure DevOps
        WIQL syntax rules, with proper SELECT, FROM, and WHERE clauses.
        
        Args:
            query: The WIQL query string (e.g., "SELECT * FROM workitems 
                WHERE [System.State] = 'Active'")
            top: Maximum number of results to return (default: 30)
                
        Returns:
            Formatted string containing detailed information for each matching
            work item, with all fields and values formatted as markdown
        """
        try:
            wit_client = get_work_item_client()
            return _query_work_items_impl(query, top or 30, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
