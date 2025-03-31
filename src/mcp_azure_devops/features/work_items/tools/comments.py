"""
Comment operations for Azure DevOps work items.

This module provides MCP tools for retrieving and adding work item comments.
"""
from typing import Optional

from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.v7_1.work_item_tracking.models import CommentCreate

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)


def _format_comment(comment) -> str:
    """
    Format a work item comment for display.
    
    Args:
        comment: Comment object to format
        
    Returns:
        Formatted string representation of the comment
    """
    # Format the date if available
    created_date = ""
    if hasattr(comment, 'created_date') and comment.created_date:
        created_date = f" on {comment.created_date}"
    
    # Format the author if available
    author = "Unknown"
    if hasattr(comment, 'created_by') and comment.created_by:
        if (hasattr(comment.created_by, 'display_name') and 
                comment.created_by.display_name):
            author = comment.created_by.display_name
    
    # Format the comment text
    text = "No text"
    if hasattr(comment, 'text') and comment.text:
        text = comment.text
    
    return f"## Comment by {author}{created_date}:\n{text}"


def _get_project_for_work_item(
    item_id: int,
    wit_client: WorkItemTrackingClient
) -> Optional[str]:
    """
    Get the project name for a work item.
    
    Args:
        item_id: The work item ID
        wit_client: Work item tracking client
            
    Returns:
        Project name or None if not found
    """
    try:
        work_item = wit_client.get_work_item(item_id)
        if work_item and work_item.fields:
            return work_item.fields.get("System.TeamProject")
    except Exception:
        pass
    
    return None


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
        project = _get_project_for_work_item(item_id, wit_client)
        
        if not project:
            return f"Error retrieving work item {item_id} to determine project"
    
    # Get comments using the project if available
    comments = wit_client.get_comments(project=project, work_item_id=item_id)
    
    # Format the comments
    formatted_comments = [
        _format_comment(comment) for comment in comments.comments
    ]
    
    if not formatted_comments:
        return "No comments found for this work item."
    
    return "\n\n".join(formatted_comments)


def _add_work_item_comment_impl(
    item_id: int,
    text: str,
    wit_client: WorkItemTrackingClient,
    project: Optional[str] = None
) -> str:
    """
    Implementation of work item comment addition.
    
    Args:
        item_id: The work item ID
        text: Comment text to add
        wit_client: Work item tracking client
        project: Optional project name
            
    Returns:
        Formatted string containing the added comment
    """
    # If project is not provided, try to get it from the work item
    if not project:
        project = _get_project_for_work_item(item_id, wit_client)
        
        if not project:
            return f"Error retrieving work item {item_id} to determine project"
    
    # Create comment request
    comment_request = CommentCreate(text=text)
    
    # Add the comment
    new_comment = wit_client.add_comment(
        request=comment_request, 
        project=project, 
        work_item_id=item_id
    )
    
    return f"Comment added successfully.\n\n{_format_comment(new_comment)}"


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
        Retrieves all comments associated with a specific work item.
    
        Use this tool when you need to:
        - Review discussion history about a work item
        - See feedback or notes left by team members
        - Check if specific questions have been answered
        - Understand the context and evolution of a work item
        
        Args:
            id: The work item ID
            project: Optional project name. If not provided, will be 
                determined from the work item.
            
        Returns:
            Formatted string containing all comments on the work item, 
            including author names, timestamps, and content, organized 
            chronologically and formatted as markdown
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_comments_impl(id, wit_client, project)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    
    @mcp.tool()
    def add_work_item_comment(
        id: int,
        text: str,
        project: Optional[str] = None
    ) -> str:
        """
        Adds a new comment to a work item.
    
        Use this tool when you need to:
        - Provide feedback or clarification on a work item
        - Document decisions made about the work
        - Add context without changing the work item's fields
        - Communicate with team members about specific tasks
        
        IMPORTANT: Comments in Azure DevOps become part of the permanent work
        item history and cannot be edited or deleted after they are added. The
        comment will be attributed to the user associated with the Personal
        Access Token used for authentication.
        
        Args:
            id: The work item ID
            text: The text of the comment (supports markdown formatting)
            project: Optional project name. If not provided, will be 
                determined from the work item.
            
        Returns:
            Formatted string containing confirmation and the added comment with
            author information and timestamp
        """
        try:
            wit_client = get_work_item_client()
            return _add_work_item_comment_impl(id, text, wit_client, project)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
