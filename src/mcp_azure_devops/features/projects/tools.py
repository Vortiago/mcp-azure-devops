"""
Project tools for Azure DevOps.

This module provides MCP tools for working with Azure DevOps projects.
"""
from typing import Optional

from azure.devops.v7_1.core import CoreClient
from azure.devops.v7_1.core.models import TeamProjectReference

from mcp_azure_devops.features.projects.common import (
    AzureDevOpsClientError,
    get_core_client,
)


def _format_project(project: TeamProjectReference) -> str:
    """
    Format project information.
    
    Args:
        project: Project object to format
        
    Returns:
        String with project details
    """
    # Basic information that should always be available
    formatted_info = [f"# Project: {project.name}"]
    formatted_info.append(f"ID: {project.id}")
    
    # Add description if available
    if hasattr(project, "description") and project.description:
        formatted_info.append(f"Description: {project.description}")
    
    # Add state if available
    if hasattr(project, "state") and project.state:
        formatted_info.append(f"State: {project.state}")
    
    # Add visibility if available
    if hasattr(project, "visibility") and project.visibility:
        formatted_info.append(f"Visibility: {project.visibility}")
    
    # Add URL if available
    if hasattr(project, "url") and project.url:
        formatted_info.append(f"URL: {project.url}")
    
    # Add last update time if available
    if hasattr(project, "last_update_time") and project.last_update_time:
        formatted_info.append(f"Last Updated: {project.last_update_time}")
    
    return "\n".join(formatted_info)


def _get_projects_impl(
    core_client: CoreClient,
    state_filter: Optional[str] = None,
    top: Optional[int] = None
) -> str:
    """
    Implementation of projects retrieval.
    
    Args:
        core_client: Core client
        state_filter: Filter on team projects in a specific state
        top: Maximum number of projects to return
            
    Returns:
        Formatted string containing project information
    """
    try:
        projects = core_client.get_projects(state_filter=state_filter, top=top)
        
        if not projects:
            return "No projects found."
        
        formatted_projects = []
        for project in projects:
            formatted_projects.append(_format_project(project))
        
        return "\n\n".join(formatted_projects)
            
    except Exception as e:
        return f"Error retrieving projects: {str(e)}"


def register_tools(mcp) -> None:
    """
    Register project tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_projects(
        state_filter: Optional[str] = None,
        top: Optional[int] = None
    ) -> str:
        """
        Retrieves all projects accessible to the authenticated user 
        in the Azure DevOps organization.
        
        Use this tool when you need to:
        - Get an overview of all available projects
        - Find project IDs for use in other operations
        - Check project states and visibility settings
        - Locate specific projects by name
        
        Args:
            state_filter: Filter on team projects in a specific state 
                (e.g., "WellFormed", "Deleting")
            top: Maximum number of projects to return
                
        Returns:
            Formatted string containing project information including names,
            IDs, descriptions, states, and visibility settings, formatted as
            markdown with each project clearly separated
        """
        try:
            core_client = get_core_client()
            return _get_projects_impl(core_client, state_filter, top)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
