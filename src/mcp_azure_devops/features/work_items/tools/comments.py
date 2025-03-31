"""
Comment operations for Azure DevOps work items.

This module provides MCP tools for retrieving work item comments.
"""
from typing import Optional
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from mcp_azure_devops.features.work_items.common import get_work_item_client, AzureDevOpsClientError

def _get_work_item_comments_impl(
    item_id: int,
    wit_client: WorkItemTrackingClient,
    project: Optional[str] = None
) -> str:
    """
    Implementation of work item comments retrieval.
    
    Args:
        item_id: The work item ID
        wit_client: Work item tracking client
        project: Optional project name
            
    Returns:
        Formatted string containing work item comments
    """
    # If project is not provided, try to get it from the work item
    if not project:
        try:
            work_item = wit_client.get_work_item(item_id)
            if work_item and work_item.fields:
                project = work_item.fields.get("System.TeamProject")
        except Exception as e:
            return f"Error retrieving work item {item_id} to determine project: {str(e)}"
    
    # Get comments using the project if available
    comments = wit_client.get_comments(project=project, work_item_id=item_id)
    
    # Format the comments
    formatted_comments = []
    for comment in comments.comments:
        # Format the date if available
        created_date = ""
        if hasattr(comment, 'created_date') and comment.created_date:
            created_date = f" on {comment.created_date}"
        
        # Format the author if available
        author = "Unknown"
        if hasattr(comment, 'created_by') and comment.created_by:
            if hasattr(comment.created_by, 'display_name') and comment.created_by.display_name:
                author = comment.created_by.display_name
        
        # Format the comment text
        text = "No text"
        if hasattr(comment, 'text') and comment.text:
            text = comment.text
        
        formatted_comments.append(f"## Comment by {author}{created_date}:\n{text}")
    
    if not formatted_comments:
        return "No comments found for this work item."
    
    return "\n\n".join(formatted_comments)

def register_tools(mcp) -> None:
    """
    Register work item comment tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_work_item_comments(
        id: int,
        project: Optional[str] = None
    ) -> str:
        """
        Get all comments for a work item.
    
        Args:
            id: The work item ID
            project: Optional project name. If not provided, will be determined from the work item.
            
        Returns:
            Formatted string containing all comments on the work item
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_comments_impl(id, wit_client, project)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
