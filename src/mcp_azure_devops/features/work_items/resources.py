"""
Work item resources for Azure DevOps.

This module provides MCP resources for accessing Azure DevOps work items.
"""
from mcp_azure_devops.utils.azure_client import get_connection


def register_resources(mcp):
    """
    Register work item resources with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.resource("azuredevops://workitems/{id}")
    def get_work_item(id: str) -> str:
        """
        Get a specific work item by ID.
        
        Args:
            id: The work item ID
            
        Returns:
            Formatted string containing detailed work item information
        """
        # Get connection to Azure DevOps
        connection = get_connection()
        
        if not connection:
            return "Error: Azure DevOps PAT or organization URL not found in environment variables."
        
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
