"""
Work item templates operations for Azure DevOps.

This module provides MCP tools for retrieving work item templates.
"""
from typing import Optional

from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)


def _format_table(headers, rows):
    """Format data as a markdown table."""
    result = []
    result.append("| " + " | ".join(headers) + " |")
    result.append("| " + " | ".join(["----"] * len(headers)) + " |")
    result.extend(rows)
    return "\n".join(result)


def _format_work_item_template(template):
    """Format work item template data for display."""
    result = [f"# Template: {template.name}"]
    
    for attr in ["description", "work_item_type_name", "id"]:
        value = getattr(template, attr, None)
        if value:
            result.append(f"{attr.replace('_', ' ').capitalize()}: {value}")
    
    fields = getattr(template, "fields", None)
    if fields:
        result.append("\n## Default Field Values")
        for field, value in fields.items():
            result.append(f"- {field}: {value}")
    
    return "\n".join(result)


def _create_team_context(team_context_dict):
    """Create a TeamContext object from a dictionary."""
    from azure.devops.v7_1.work_item_tracking.models import TeamContext
    return TeamContext(
        project=team_context_dict.get('project'),
        project_id=team_context_dict.get('project_id'),
        team=team_context_dict.get('team'),
        team_id=team_context_dict.get('team_id')
    )


def _get_work_item_templates_impl(
    team_context: dict, 
    work_item_type: Optional[str],
    wit_client: WorkItemTrackingClient
) -> str:
    """Implementation of work item templates retrieval."""
    try:
        team_ctx = _create_team_context(team_context)
        templates = wit_client.get_templates(team_ctx, work_item_type)
        
        team_display = team_context.get('team') or team_context.get('team_id')
        
        if not templates:
            scope = (f"work item type '{work_item_type}' in " 
                    if work_item_type else "")
            return f"No templates found for {scope}team {team_display}."
        
        # Create header
        project_display = (team_context.get('project') or 
                          team_context.get('project_id'))
        header = (f"# Work Item Templates for Team: {team_display} "
                 f"(Project: {project_display})")
        if work_item_type:
            header += f" (Filtered by type: {work_item_type})"
        
        headers = ["Name", "Work Item Type", "Description"]
        
        # Use list comprehension for table rows
        rows = [
            f"| {template.name} | " 
            f"{getattr(template, 'work_item_type_name', 'N/A')} | " +
            f"{getattr(template, 'description', 'N/A')} |"
            for template in templates
        ]
        
        return f"{header}\n\n" + _format_table(headers, rows)
    except Exception as e:
        return f"Error retrieving templates: {str(e)}"


def _get_work_item_template_impl(team_context: dict, template_id: str,
                                wit_client: WorkItemTrackingClient) -> str:
    """Implementation of work item template detail retrieval."""
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
    Register work item templates tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_work_item_templates(
        team_context: dict, 
        work_item_type: Optional[str]
    ) -> str:
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
            return _get_work_item_templates_impl(
                team_context, work_item_type, wit_client)
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
            Detailed information about the template including default field 
            values
        """
        try:
            wit_client = get_work_item_client()
            return _get_work_item_template_impl(
                team_context, template_id, wit_client)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
