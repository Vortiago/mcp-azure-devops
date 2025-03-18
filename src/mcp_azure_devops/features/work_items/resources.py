"""
Work item resources for Azure DevOps.

This module provides MCP resources for accessing Azure DevOps work items.
"""
from typing import Optional
from azure.devops.v7_1.work_item_tracking.models import WorkItem
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from mcp_azure_devops.utils.azure_client import get_connection
from mcp_azure_devops.features.work_items.common import get_work_item_client, AzureDevOpsClientError


def _format_work_item_basic(work_item: WorkItem) -> str:
    """
    Format basic work item information.
    
    Args:
        work_item: Work item object to format
        
    Returns:
        String with basic work item details
    """
    fields = work_item.fields or {}
    title = fields.get("System.Title", "Untitled")
    item_type = fields.get("System.WorkItemType", "Unknown")
    state = fields.get("System.State", "Unknown")
    
    return f"# Work Item {work_item.id}: {title}\nType: {item_type}\nState: {state}"


def _format_work_item_detailed(work_item: WorkItem, basic_info: str) -> str:
    """
    Add detailed information to basic work item information.
    
    Args:
        work_item: Work item object to format
        basic_info: Already formatted basic information
        
    Returns:
        String with comprehensive work item details
    """
    details = [basic_info]  # Start with basic info already provided
    
    fields = work_item.fields or {}
    
    if "System.Description" in fields:
        details.append("\n## Description")
        details.append(fields["System.Description"])
    
    # Add additional details section
    details.append("\n## Additional Details")
    
    if "System.AssignedTo" in fields:
        details.append(f"Assigned To: {fields['System.AssignedTo']}")
    
    if "System.IterationPath" in fields:
        details.append(f"Iteration: {fields['System.IterationPath']}")
    
    if "System.AreaPath" in fields:
        details.append(f"Area: {fields['System.AreaPath']}")
    
    # Add more fields as needed
    
    return "\n".join(details)


def _get_work_item_impl(
    item_id: int,
    wit_client: WorkItemTrackingClient,
    detailed: bool = False
) -> str:
    """
    Implementation of work item retrieval.
    
    Args:
        item_id: The work item ID
        wit_client: Work item tracking client
        detailed: Whether to return detailed information
            
    Returns:
        Formatted string containing work item information
    """
    try:
        work_item = wit_client.get_work_item(item_id)
        
        # Always format basic info first
        basic_info = _format_work_item_basic(work_item)
        
        # If detailed is requested, add more information
        if detailed:
            return _format_work_item_detailed(work_item, basic_info)
        else:
            return basic_info
            
    except Exception as e:
        return f"Error retrieving work item {item_id}: {str(e)}"


def register_resources(mcp):
    """
    Register work item resources with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.resource("azuredevops://workitem/{id}")
    def get_work_item_basic(id: str) -> str:
        """
        Get basic information about a work item.
        
        Args:
            id: The work item ID
            
        Returns:
            Formatted string containing basic work item information
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_impl(int(id), wit_client, detailed=False)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.resource("azuredevops://workitem/{id}/details")
    def get_work_item_details(id: str) -> str:
        """
        Get detailed information about a work item.
        
        Args:
            id: The work item ID
            
        Returns:
            Formatted string containing comprehensive work item information
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_impl(int(id), wit_client, detailed=True)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
