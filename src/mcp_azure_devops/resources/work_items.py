"""
Work item resources for Azure DevOps.

This module provides MCP resources for accessing Azure DevOps work items.
"""
import os
from typing import Optional
from azure.devops.connection import Connection
from azure.devops.v7_1.work_item_tracking.models import Wiql
from msrest.authentication import BasicAuthentication


def register_resources(mcp):
    """
    Register work item resources with the MCP server.
    
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
        # Get credentials from environment variables
        pat = os.environ.get("AZURE_DEVOPS_PAT")
        organization_url = os.environ.get("AZURE_DEVOPS_ORGANIZATION_URL")
        
        if not pat or not organization_url:
            return "Error: Azure DevOps PAT or organization URL not found in environment variables."
        
        # Create a connection to Azure DevOps
        credentials = BasicAuthentication('', pat)
        connection = Connection(base_url=organization_url, creds=credentials)
        
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
    
    @mcp.resource("azuredevops://workitems/{id}")
    def get_work_item(id: str) -> str:
        """
        Get a specific work item by ID.
        
        Args:
            id: The work item ID
            
        Returns:
            Formatted string containing detailed work item information
        """
        # Get credentials from environment variables
        pat = os.environ.get("AZURE_DEVOPS_PAT")
        organization_url = os.environ.get("AZURE_DEVOPS_ORGANIZATION_URL")
        
        if not pat or not organization_url:
            return "Error: Azure DevOps PAT or organization URL not found in environment variables."
        
        # Create a connection to Azure DevOps
        credentials = BasicAuthentication('', pat)
        connection = Connection(base_url=organization_url, creds=credentials)
        
        # Get the work item tracking client
        wit_client = connection.clients.get_work_item_tracking_client()
        
        try:
            work_item = wit_client.get_work_item(int(id))
            
            # Format the work item details
            details = [f"# Work Item {work_item.id}: {work_item.fields.get('System.Title', 'Untitled')}"]
            details.append(f"Type: {work_item.fields.get('System.WorkItemType', 'Unknown')}")
            details.append(f"State: {work_item.fields.get('System.State', 'Unknown')}")
            
            if "System.Description" in work_item.fields:
                details.append("\n## Description")
                details.append(work_item.fields["System.Description"])
            
            if "System.AssignedTo" in work_item.fields:
                details.append(f"\nAssigned To: {work_item.fields['System.AssignedTo']}")
            
            if "System.IterationPath" in work_item.fields:
                details.append(f"Iteration: {work_item.fields['System.IterationPath']}")
            
            if "System.AreaPath" in work_item.fields:
                details.append(f"Area: {work_item.fields['System.AreaPath']}")
            
            return "\n".join(details)
            
        except Exception as e:
            return f"Error retrieving work item {id}: {str(e)}"
