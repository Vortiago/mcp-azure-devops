"""
Work item tools for Azure DevOps.

This module provides MCP tools for working with Azure DevOps work items.
"""
from typing import Optional
from azure.devops.v7_1.work_item_tracking.models import Wiql
from mcp_azure_devops.utils.azure_client import get_connection


def register_tools(mcp):
    """
    Register work item tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def query_work_items(query: str, top: Optional[int] = 30) -> str:
        """
        Query work items using WIQL.
        
        Args:
            query: The WIQL query string
            top: Maximum number of results to return (default: 30)
            
        Returns:
            Formatted string containing work item details
        """
        # Get connection to Azure DevOps
        connection = get_connection()
        
        if not connection:
            return "Error: Azure DevOps PAT or organization URL not found in environment variables."
        
        # Get the work item tracking client
        wit_client = connection.clients.get_work_item_tracking_client()
        
        # Create the WIQL query
        wiql = Wiql(query=query)
        
        # Execute the query
        wiql_results = wit_client.query_by_wiql(wiql, top=top).work_items
        
        if not wiql_results:
            return "No work items found matching the query."
        
        # Get the work items from the results
        work_item_ids = [int(res.id) for res in wiql_results]
        work_items = wit_client.get_work_items(ids=work_item_ids, error_policy="omit")
        
        # Format the results
        formatted_results = []
        for work_item in work_items:
            if work_item:
                item_type = work_item.fields.get("System.WorkItemType", "Unknown")
                item_id = work_item.id
                item_title = work_item.fields.get("System.Title", "Untitled")
                item_state = work_item.fields.get("System.State", "Unknown")
                
                formatted_results.append(
                    f"{item_type} {item_id}: {item_title} ({item_state})"
                )
        
        return "\n".join(formatted_results)
