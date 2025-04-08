"""
Work item types and fields operations for Azure DevOps.

This module provides MCP tools for retrieving work item types and fields.
"""
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)
from mcp_azure_devops.utils.azure_client import (
    get_core_client,
    get_work_item_tracking_process_client,
)


def _format_table(headers, rows):
    """Format data as a markdown table."""
    result = []
    result.append("| " + " | ".join(headers) + " |")
    result.append("| " + " | ".join(["----"] * len(headers)) + " |")
    result.extend(rows)
    return "\n".join(result)


def _format_work_item_type(wit):
    """Format work item type data for display."""
    result = [f"# Work Item Type: {wit.name}"]
    
    description = getattr(wit, "description", None)
    if description:
        result.append(f"\n**Description:** {description}")
    
    for attr in ["color", "icon", "reference_name"]:
        value = getattr(wit, attr, None)
        if value:
            result.append(f"**{attr.capitalize()}:** {value}")
    
    is_disabled = getattr(wit, "is_disabled", None)
    if is_disabled is not None:
        result.append(f"**Is Disabled:** {is_disabled}")
    
    states = getattr(wit, "states", None)
    if states:
        result.append("\n## States")
        for state in states:
            state_info = f"- **{state.name}** (Category: {state.category}, Color: {state.color})"
            order = getattr(state, "order", None)
            if order is not None:
                state_info += f", Order: {order}"
            result.append(state_info)
    
    return "\n".join(result)


def _get_work_item_types_impl(project: str, wit_client: WorkItemTrackingClient) -> str:
    """Implementation of work item types retrieval."""
    work_item_types = wit_client.get_work_item_types(project)
    
    if not work_item_types:
        return f"No work item types found in project {project}."
    
    headers = ["Name", "Reference Name", "Description"]
    
    # Use list comprehension for more concise table building
    rows = [
        f"| {wit.name} | {getattr(wit, 'reference_name', 'N/A')} | {getattr(wit, 'description', 'N/A')} |"
        for wit in work_item_types
    ]
    
    return f"# Work Item Types in Project: {project}\n\n" + _format_table(headers, rows)


def _get_work_item_type_impl(project: str, type_name: str, 
                             wit_client: WorkItemTrackingClient) -> str:
    """Implementation of work item type detail retrieval."""
    work_item_type = wit_client.get_work_item_type(project, type_name)
    
    if not work_item_type:
        return f"Work item type '{type_name}' not found in project {project}."
    
    return _format_work_item_type(work_item_type)


def _get_work_item_type_fields_impl(project: str, type_name: str, 
                                   wit_client: WorkItemTrackingClient) -> str:
    """Implementation of work item type fields retrieval using process API."""
    try:
        # Get the work item type to get its reference name
        wit = wit_client.get_work_item_type(project, type_name)
        if not wit:
            return f"Work item type '{type_name}' not found in project {project}."
        
        wit_ref_name = wit.reference_name
        
        # Get project process info
        core_client = get_core_client()
        project_details = core_client.get_project(project, include_capabilities=True)
        process_id = project_details.capabilities.get("processTemplate", {}).get("templateTypeId")
        
        if not process_id:
            return f"Could not determine process ID for project {project}"
        
        # Get process client and fields for this work item type
        process_client = get_work_item_tracking_process_client()
        fields = process_client.get_all_work_item_type_fields(process_id, wit_ref_name)
        
        if not fields:
            return f"No fields found for work item type '{type_name}' in project {project}."
        
        headers = ["Name", "Reference Name", "Type", "Required", "Read Only", "Allowed Values"]
        
        # Simple table formatting
        rows = [
            f"| {field.name} | {field.reference_name} | " +
            f"{getattr(field, 'type', 'N/A')} | " +
            f"{'Yes' if getattr(field, 'required', False) else 'No'} | " +
            f"{'Yes' if getattr(field, 'read_only', False) else 'No'} | " +
            f"{', '.join(str(v) for v in getattr(field, 'allowed_values', []) or [])} |"
            for field in fields
        ]
        
        return f"# Fields for Work Item Type: {type_name}\n\n" + _format_table(headers, rows)
    except Exception as e:
        return f"Error retrieving fields for work item type '{type_name}' in project '{project}': {str(e)}"


def _get_work_item_type_field_impl(project: str, type_name: str, field_name: str,
                                   wit_client: WorkItemTrackingClient) -> str:
    """Implementation of work item type field detail retrieval using process API."""
    try:
        # Get the work item type to get its reference name
        wit = wit_client.get_work_item_type(project, type_name)
        if not wit:
            return f"Work item type '{type_name}' not found in project {project}."
        
        wit_ref_name = wit.reference_name
        
        # Get project process info
        core_client = get_core_client()
        project_details = core_client.get_project(project, include_capabilities=True)
        process_id = project_details.capabilities.get("processTemplate", {}).get("templateTypeId")
        
        if not process_id:
            return f"Could not determine process ID for project {project}"
        
        # Get process client and field details
        process_client = get_work_item_tracking_process_client()
        
        # Determine if field_name is a display name or reference name
        if not field_name.startswith("System.") and not field_name.startswith("Custom."):
            # Get all fields to find the reference name
            all_fields = process_client.get_all_work_item_type_fields(process_id, wit_ref_name)
            field_ref = next((f.reference_name for f in all_fields if f.name.lower() == field_name.lower()), None)
            if not field_ref:
                return f"Field '{field_name}' not found for work item type '{type_name}' in project '{project}'."
            field_name = field_ref
        
        field = process_client.get_work_item_type_field(process_id, wit_ref_name, field_name)
        
        if not field:
            return f"Field '{field_name}' not found for work item type '{type_name}' in project '{project}'."
        
        # Format field details
        result = [f"# Field: {field.name}"]
        result.append(f"**Reference Name:** {field.reference_name}")
        
        if hasattr(field, "description") and field.description:
            result.append(f"**Description:** {field.description}")
        
        if hasattr(field, "type"):
            result.append(f"**Type:** {field.type}")
        
        result.append(f"**Required:** {'Yes' if getattr(field, 'required', False) else 'No'}")
        result.append(f"**Read Only:** {'Yes' if getattr(field, 'read_only', False) else 'No'}")
        
        allowed_values = getattr(field, "allowed_values", None)
        if allowed_values and len(allowed_values) > 0:
            result.append("\n## Allowed Values")
            for value in allowed_values:
                result.append(f"- {value}")
        
        default_value = getattr(field, "default_value", None)
        if default_value is not None:
            result.append(f"\n**Default Value:** {default_value}")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving field '{field_name}' for work item type '{type_name}' in project '{project}': {str(e)}"


def register_tools(mcp) -> None:
    """
    Register work item types and fields tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_work_item_types(project: str) -> str:
        """
        Gets a list of all work item types in a project.
        
        Use this tool when you need to:
        - See what work item types are available in a project
        - Get reference names for work item types to use in other operations
        - Plan work item creation by understanding available types
        
        Args:
            project: Project ID or project name
            
        Returns:
            A formatted table of all work item types with names, reference names,
            and descriptions
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_types_impl(project, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_work_item_type(project: str, type_name: str) -> str:
        """
        Gets detailed information about a specific work item type.
        
        Use this tool when you need to:
        - Get complete details about a work item type
        - Understand the states and transitions for a work item type
        - Learn about the color and icon for a work item type
        
        Args:
            project: Project ID or project name
            type_name: The name of the work item type
            
        Returns:
            Detailed information about the work item type including states,
            color, icon, and reference name
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_type_impl(project, type_name, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_work_item_type_fields(project: str, type_name: str) -> str:
        """
        Gets a list of all fields for a specific work item type.
        
        Use this tool when you need to:
        - See what fields are available for a work item type
        - Find required fields for creating work items of a specific type
        - Get reference names for fields to use in queries or updates
        
        Args:
            project: Project ID or project name
            type_name: The name of the work item type
            
        Returns:
            A formatted table of all fields with names, reference names,
            types, and required/read-only status
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_type_fields_impl(project, type_name, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_work_item_type_field(project: str, type_name: str, field_name: str) -> str:
        """
        Gets detailed information about a specific field in a work item type.
        
        Use this tool when you need to:
        - Get complete details about a work item field
        - Check allowed values for a field
        - Verify if a field is required or read-only
        
        Args:
            project: Project ID or project name
            type_name: The name of the work item type
            field_name: The reference name or display name of the field
            
        Returns:
            Detailed information about the field including type, allowed values,
            and constraints
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_type_field_impl(project, type_name, field_name, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"