"""
Work item types and metadata operations for Azure DevOps.

This module provides MCP tools for retrieving work item types, templates, and fields.
"""
from typing import Optional

from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)


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
            state_info = f"- **{state.name}** (Category: {state.state_category}, Color: {state.color})"
            order = getattr(state, "order", None)
            if order is not None:
                state_info += f", Order: {order}"
            result.append(state_info)
    
    return "\n".join(result)


def _format_work_item_field(field):
    """Format work item field data for display."""
    result = [f"# Field: {field.name}"]
    
    for attr in ["reference_name", "description"]:
        value = getattr(field, attr, None)
        if value:
            result.append(f"**{attr.capitalize()}:** {value}")
    
    field_type = getattr(field, "type", None)
    if field_type:
        result.append(f"**Type:** {field_type}")
    
    for attr in ["read_only", "required"]:
        value = getattr(field, attr, None)
        if value is not None:
            result.append(f"**{attr.capitalize()}:** {value}")
    
    allowed_values = getattr(field, "allowed_values", None)
    if allowed_values:
        result.append("\n## Allowed Values")
        for value in allowed_values:
            result.append(f"- {value}")
    
    return "\n".join(result)


def _format_work_item_template(template):
    """Format work item template data for display."""
    result = [f"# Template: {template.name}"]
    
    for attr in ["description", "work_item_type_name", "id"]:
        value = getattr(template, attr, None)
        if value:
            result.append(f"**{attr.replace('_', ' ').capitalize()}:** {value}")
    
    fields = getattr(template, "fields", None)
    if fields:
        result.append("\n## Default Field Values")
        for field, value in fields.items():
            result.append(f"- **{field}**: {value}")
    
    return "\n".join(result)


def _get_work_item_types_impl(project: str, wit_client: WorkItemTrackingClient) -> str:
    """
    Implementation of work item types retrieval.
    
    Args:
        project: Project name or ID
        wit_client: Work item tracking client
    
    Returns:
        Formatted string containing work item types information
    """
    work_item_types = wit_client.get_work_item_types(project)
    
    if not work_item_types:
        return f"No work item types found in project {project}."
    
    # Format simple list overview first
    result = [f"# Work Item Types in Project: {project}\n"]
    result.append("| Name | Reference Name | Description |")
    result.append("| ---- | -------------- | ----------- |")
    
    for wit in work_item_types:
        description = getattr(wit, "description", "N/A")
        ref_name = getattr(wit, "reference_name", "N/A")
        result.append(f"| {wit.name} | {ref_name} | {description} |")
    
    return "\n".join(result)


def _get_work_item_type_impl(project: str, type_name: str, 
                             wit_client: WorkItemTrackingClient) -> str:
    """
    Implementation of work item type detail retrieval.
    
    Args:
        project: Project name or ID
        type_name: Work item type name
        wit_client: Work item tracking client
    
    Returns:
        Formatted string containing work item type details
    """
    work_item_type = wit_client.get_work_item_type(project, type_name)
    
    if not work_item_type:
        return f"Work item type '{type_name}' not found in project {project}."
    
    return _format_work_item_type(work_item_type)


def _get_work_item_type_fields_impl(project: str, type_name: str, 
                                    wit_client: WorkItemTrackingClient) -> str:
    """
    Implementation of work item type fields retrieval.
    
    Args:
        project: Project name or ID
        type_name: Work item type name
        wit_client: Work item tracking client
    
    Returns:
        Formatted string containing work item type fields
    """
    try:
        fields = wit_client.get_work_item_type_fields_with_references(project, type_name, expand="all")
        
        if not fields:
            return f"No fields found for work item type '{type_name}' in project {project}."
        
        # Format simple list overview first
        result = [f"# Fields for Work Item Type: {type_name}\n"]
        result.append("| Name | Reference Name | Type | Required | Read Only |")
        result.append("| ---- | -------------- | ---- | -------- | --------- |")
        
        for field in fields:
            required = "Yes" if getattr(field, "always_required", False) else "No"
            read_only = "Yes" if getattr(field, "read_only", False) else "No"
            field_type = getattr(field, "type", "N/A")
            result.append(f"| {field.name} | {field.reference_name} | {field_type} | {required} | {read_only} |")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving fields for work item type '{type_name}' in project '{project}': {str(e)}"


def _get_work_item_type_field_impl(project: str, type_name: str, field_name: str,
                                   wit_client: WorkItemTrackingClient) -> str:
    """
    Implementation of work item type field detail retrieval.
    
    Args:
        project: Project name or ID
        type_name: Work item type name
        field_name: Field reference name or display name
        wit_client: Work item tracking client
    
    Returns:
        Formatted string containing work item type field details
    """
    try:
        field = wit_client.get_work_item_type_field_with_references(
            project, type_name, field_name, expand="all")
        
        if not field:
            return f"Field '{field_name}' not found for work item type '{type_name}' in project '{project}'."
        
        return _format_work_item_field(field)
    except Exception as e:
        return f"Error retrieving field '{field_name}' for work item type '{type_name}' in project '{project}': {str(e)}"


def _create_team_context(team_context_dict):
    """Create a TeamContext object from a dictionary."""
    from azure.devops.v7_1.work_item_tracking.models import TeamContext
    return TeamContext(
        project=team_context_dict.get('project'),
        project_id=team_context_dict.get('project_id'),
        team=team_context_dict.get('team'),
        team_id=team_context_dict.get('team_id')
    )


def _get_work_item_templates_impl(team_context: dict, work_item_type: Optional[str] ,
                                 wit_client: WorkItemTrackingClient) -> str:
    """
    Implementation of work item templates retrieval.
    
    Args:
        team_context: Team context dictionary with project and team information
        work_item_type: Optional work item type to filter templates
        wit_client: Work item tracking client
    
    Returns:
        Formatted string containing work item templates
    """
    try:
        team_ctx = _create_team_context(team_context)
        templates = wit_client.get_templates(team_ctx, work_item_type)
        
        if not templates:
            filter_msg = f" for work item type '{work_item_type}'" if work_item_type else ""
            return f"No templates found{filter_msg} in team {team_context.get('team') or team_context.get('team_id')}."
        
        # Format simple list overview first
        project_display = team_context.get('project') or team_context.get('project_id')
        team_display = team_context.get('team') or team_context.get('team_id')
        result = [f"# Work Item Templates for Team: {team_display} (Project: {project_display})\n"]
        
        if work_item_type:
            result[0] += f" (Filtered by type: {work_item_type})"
        
        result.append("| Name | Work Item Type | Description |")
        result.append("| ---- | -------------- | ----------- |")
        
        for template in templates:
            description = getattr(template, "description", "N/A")
            wit_name = getattr(template, "work_item_type_name", "N/A")
            result.append(f"| {template.name} | {wit_name} | {description} |")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving templates: {str(e)}"


def _get_work_item_template_impl(team_context: dict, template_id: str,
                                wit_client: WorkItemTrackingClient) -> str:
    """
    Implementation of work item template detail retrieval.
    
    Args:
        team_context: Team context dictionary with project and team information
        template_id: Template ID
        wit_client: Work item tracking client
    
    Returns:
        Formatted string containing work item template details
    """
    try:
        team_ctx = _create_team_context(team_context)
        template = wit_client.get_template(team_ctx, template_id)
        
        if not template:
            return f"Template with ID '{template_id}' not found."
        
        return _format_work_item_template(template)
    except Exception as e:
        return f"Error retrieving template '{template_id}': {str(e)}"


def register_tools(mcp) -> None:
    """
    Register work item types and metadata tools with the MCP server.
    
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
    
    @mcp.tool()
    def get_work_item_templates(team_context: dict, work_item_type: Optional[str]) -> str:
        """
        Gets a list of all work item templates for a team.
        
        Use this tool when you need to:
        - Find available templates for creating work items
        - Get template IDs for use in other operations
        - Filter templates by work item type
        
        Args:
            team_context: Dictionary containing team information with keys:
                project: Project name (Optional if project_id is provided)
                project_id: Project ID (Optional if project is provided)
                team: Team name (Optional if team_id is provided)
                team_id: Team ID (Optional if team is provided)
            work_item_type: Optional work item type name to filter templates
            
        Returns:
            A formatted table of all templates with names, work item types,
            and descriptions
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_templates_impl(team_context, work_item_type, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_work_item_template(team_context: dict, template_id: str) -> str:
        """
        Gets detailed information about a specific work item template.
        
        Use this tool when you need to:
        - View default field values in a template
        - Understand what a template pre-populates in a work item
        - Get complete details about a template
        
        Args:
            team_context: Dictionary containing team information with keys:
                project: Project name (Optional if project_id is provided)
                project_id: Project ID (Optional if project is provided)
                team: Team name (Optional if team_id is provided)
                team_id: Team ID (Optional if team is provided)
            template_id: The ID of the template
            
        Returns:
            Detailed information about the template including default field values
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_template_impl(team_context, template_id, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
