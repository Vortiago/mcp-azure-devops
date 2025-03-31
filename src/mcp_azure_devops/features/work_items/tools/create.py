"""
Create operations for Azure DevOps work items.

This module provides MCP tools for creating work items.
"""
import os
from typing import Any, Dict, Optional

from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)
from mcp_azure_devops.features.work_items.formatting import format_work_item


def _build_field_document(fields: Dict[str, Any], 
                          operation: str = "add") -> list:
    """
    Build a document of JsonPatchOperations from a dictionary of fields.
    
    Args:
        fields: Dictionary of field name/value pairs
        operation: The operation to perform (add or replace)
        
    Returns:
        List of JsonPatchOperation objects
    """
    document = []
    
    for field_name, field_value in fields.items():
        # Ensure field names are prefixed with /fields/
        path = (field_name if field_name.startswith("/fields/") 
                else f"/fields/{field_name}")
        
        document.append(
            JsonPatchOperation(
                op=operation,
                path=path,
                value=field_value
            )
        )
    
    return document


def _get_organization_url() -> str:
    """
    Get the Azure DevOps organization URL from environment variables.
    
    Returns:
        Organization URL string
    """
    return os.environ.get("AZURE_DEVOPS_ORGANIZATION_URL", "").rstrip('/')


def _build_link_document(target_id: int, link_type: str, org_url: str) -> list:
    """
    Build a document for creating a link between work items.
    
    Args:
        target_id: ID of the target work item to link to
        link_type: Type of link to create
        org_url: Base organization URL
        
    Returns:
        List of JsonPatchOperation objects
    """
    return [
        JsonPatchOperation(
            op="add",
            path="/relations/-",
            value={
                "rel": link_type,
                "url": f"{org_url}/_apis/wit/workItems/{target_id}"
            }
        )
    ]


def _create_work_item_impl(
    fields: Dict[str, Any],
    project: str,
    work_item_type: str,
    wit_client: WorkItemTrackingClient,
    parent_id: Optional[int] = None,
) -> str:
    """
    Implementation of creating a work item.
    
    Args:
        fields: Dictionary of field name/value pairs to set
        project: The project name or ID
        work_item_type: Type of work item (e.g., "User Story", "Bug", "Task")
        wit_client: Work item tracking client
        parent_id: Optional ID of parent work item for hierarchy
        
    Returns:
        Formatted string containing the created work item details
    """
    document = _build_field_document(fields)
    
    # Create the work item
    new_work_item = wit_client.create_work_item(
        document=document,
        project=project,
        type=work_item_type
    )
    
    # If parent_id is provided, establish parent-child relationship
    if parent_id:
        try:
            # Get organization URL from environment
            org_url = _get_organization_url()
            
            # Create parent-child relationship
            link_document = _build_link_document(
                target_id=parent_id,
                link_type="System.LinkTypes.Hierarchy-Reverse",
                org_url=org_url
            )
            
            # Update the work item to add the parent link
            new_work_item = wit_client.update_work_item(
                document=link_document,
                id=new_work_item.id,
                project=project
            )
        except Exception as e:
            return (f"Work item created successfully, but failed to establish "
                   f"parent-child relationship: {str(e)}\n\n"
                   f"{format_work_item(new_work_item)}")
    
    # Format and return the created work item
    return format_work_item(new_work_item)


def _update_work_item_impl(
    id: int,
    fields: Dict[str, Any],
    wit_client: WorkItemTrackingClient,
    project: Optional[str] = None,
) -> str:
    """
    Implementation of updating a work item.
    
    Args:
        id: The ID of the work item to update
        fields: Dictionary of field name/value pairs to update
        wit_client: Work item tracking client
        project: Optional project name or ID
        
    Returns:
        Formatted string containing the updated work item details
    """
    document = _build_field_document(fields, "replace")
    
    # Update the work item
    updated_work_item = wit_client.update_work_item(
        document=document,
        id=id,
        project=project
    )
    
    return format_work_item(updated_work_item)


def _add_link_to_work_item_impl(
    source_id: int,
    target_id: int,
    link_type: str,
    wit_client: WorkItemTrackingClient,
    project: Optional[str] = None,
) -> str:
    """
    Implementation of adding a link between work items.
    
    Args:
        source_id: ID of the source work item
        target_id: ID of the target work item
        link_type: Type of link to create
        wit_client: Work item tracking client
        project: Optional project name or ID
        
    Returns:
        Formatted string containing the updated work item details
    """
    # Get organization URL from environment
    org_url = _get_organization_url()
    
    # Build link document with the full URL
    link_document = _build_link_document(target_id, link_type, org_url)
    
    # Update the work item to add the link
    updated_work_item = wit_client.update_work_item(
        document=link_document,
        id=source_id,
        project=project
    )
    
    return format_work_item(updated_work_item)


def _prepare_create_fields(
    title: str,
    description: Optional[str] = None,
    state: Optional[str] = None,
    assigned_to: Optional[str] = None,
    iteration_path: Optional[str] = None,
    area_path: Optional[str] = None,
    story_points: Optional[float] = None,
    priority: Optional[int] = None,
    tags: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prepare fields dictionary for work item creation.
    
    Args:
        title: The title of the work item
        description: Optional description of the work item
        state: Optional initial state for the work item
        assigned_to: Optional user email to assign the work item to
        iteration_path: Optional iteration path for the work item
        area_path: Optional area path for the work item
        story_points: Optional story points value
        priority: Optional priority value
        tags: Optional tags as comma-separated string
    
    Returns:
        Dictionary of field name/value pairs
    """
    fields = {
        "System.Title": title
    }
    
    if description:
        fields["System.Description"] = description
    
    if state:
        fields["System.State"] = state
    
    if assigned_to:
        fields["System.AssignedTo"] = assigned_to
    
    if iteration_path:
        fields["System.IterationPath"] = iteration_path
    
    if area_path:
        fields["System.AreaPath"] = area_path
    
    if story_points is not None:
        # Convert float to string to avoid type errors
        fields["Microsoft.VSTS.Scheduling.StoryPoints"] = str(story_points)
    
    if priority is not None:
        fields["Microsoft.VSTS.Common.Priority"] = str(priority)
    
    if tags:
        fields["System.Tags"] = tags
    
    return fields


def register_tools(mcp) -> None:
    """
    Register work item creation tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def create_work_item(
        title: str,
        project: str,
        work_item_type: str,
        description: Optional[str] = None,
        state: Optional[str] = None,
        assigned_to: Optional[str] = None,
        parent_id: Optional[int] = None,
        iteration_path: Optional[str] = None,
        area_path: Optional[str] = None,
        story_points: Optional[float] = None,
        priority: Optional[int] = None,
        tags: Optional[str] = None,
    ) -> str:
        """
        Creates a new work item in Azure DevOps.
        
        Use this tool when you need to:
        - Add a new task, user story, bug, or other work item to a project
        - Create work items with specific field values and metadata
        - Establish work hierarchies by setting parent relationships
        - Track new requirements, features, or issues in your project
        
        IMPORTANT: The work item will be created immediately and visible to all
        users with access to the specified project. It will also trigger any
        configured notifications or automation rules.
        
        Args:
            title: The title of the work item
            project: The project name or ID where the work item will be created
            work_item_type: Type of work item (e.g., "User Story", "Bug", 
                "Task")
            description: Optional description of the work item
            state: Optional initial state for the work item
            assigned_to: Optional user email to assign the work item to
            parent_id: Optional ID of parent work item for hierarchy
            iteration_path: Optional iteration path for the work item
            area_path: Optional area path for the work item
            story_points: Optional story points value
            priority: Optional priority value
            tags: Optional tags as comma-separated string
            
        Returns:
            Formatted string containing the created work item details including
            ID, title, type, state, and all other specified fields, formatted
            as markdown
        """
        try:
            wit_client = get_work_item_client()
            fields = _prepare_create_fields(
                title, description, state, assigned_to,
                iteration_path, area_path, story_points, priority, tags
            )
            
            return _create_work_item_impl(
                fields=fields,
                project=project,
                work_item_type=work_item_type,
                wit_client=wit_client,
                parent_id=parent_id
            )
            
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error creating work item: {str(e)}"
    
    
    @mcp.tool()
    def update_work_item(
        id: int,
        project: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[str] = None,
        assigned_to: Optional[str] = None,
        iteration_path: Optional[str] = None,
        area_path: Optional[str] = None,
        story_points: Optional[float] = None,
        priority: Optional[int] = None,
        tags: Optional[str] = None,
    ) -> str:
        """
        Modifies an existing work item's fields and properties.
        
        Use this tool when you need to:
        - Change the status or state of a work item
        - Reassign work to a different team member
        - Update the description or details of a requirement
        - Modify effort estimates or priority levels
        - Add or change classification (area/iteration)
        
        IMPORTANT: This tool updates the work item directly in Azure DevOps.
        Changes will be immediately visible to all users with access to the
        work item and will trigger any configured notifications or workflows.
        You must specify at least one field to update.
        
        Args:
            id: The ID of the work item to update
            project: Optional project name or ID
            title: Optional new title for the work item
            description: Optional new description
            state: Optional new state
            assigned_to: Optional user email to assign to
            iteration_path: Optional new iteration path
            area_path: Optional new area path
            story_points: Optional new story points value
            priority: Optional new priority value
            tags: Optional new tags as comma-separated string
            
        Returns:
            Formatted string containing the updated work item details with
            all current field values, formatted as markdown
        """
        try:
            wit_client = get_work_item_client()
            fields = _prepare_create_fields(
                title if title else "", description, state, assigned_to,
                iteration_path, area_path, story_points, priority, tags
            )
            
            # Remove empty title if it was not provided
            if not title:
                fields.pop("System.Title", None)
                
            if not fields:
                return "Error: At least one field must be specified for update"
            
            return _update_work_item_impl(
                id=id,
                fields=fields,
                wit_client=wit_client,
                project=project
            )
            
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error updating work item: {str(e)}"
    
    
    @mcp.tool()
    def add_parent_child_link(
        parent_id: int,
        child_id: int,
        project: Optional[str] = None,
    ) -> str:
        """
        Adds a parent-child relationship between two work items.
        
        Use this tool when you need to:
        - Establish hierarchy between work items
        - Organize epics, features, user stories, and tasks
        - Create a structured breakdown of work
        - Enable rollup of effort and progress tracking
        
        IMPORTANT: The child work item will immediately appear under the parent
        in hierarchical views. This relationship affects how the items are
        displayed in backlogs and boards. In Azure DevOps, a work item can have
        only one parent but multiple children.
        
        Args:
            parent_id: ID of the parent work item
            child_id: ID of the child work item
            project: Optional project name or ID
            
        Returns:
            Formatted string containing the updated child work item details
            showing the new parent relationship, formatted as markdown
        """
        try:
            wit_client = get_work_item_client()
            
            return _add_link_to_work_item_impl(
                source_id=child_id,
                target_id=parent_id,
                link_type="System.LinkTypes.Hierarchy-Reverse",
                wit_client=wit_client,
                project=project
            )
            
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error creating parent-child link: {str(e)}"
