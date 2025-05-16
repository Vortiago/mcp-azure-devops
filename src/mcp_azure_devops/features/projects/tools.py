"""
Project tools for Azure DevOps.

This module provides MCP tools for working with Azure DevOps projects.
"""
from typing import Optional, Dict, Any

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

def _create_project_impl(
    core_client: CoreClient,
    name: str,
    description: Optional[str] = None,
    source_control_type: str = "Git",
    process_template_id: Optional[str] = None,
    visibility: str = "private"
) -> Dict[str, Any]:
    """
    Implementation of project creation.
    
    Args:
        core_client: Core client
        name: Name of the project to create
        description: Optional description of the project
        source_control_type: Type of version control to use (Git or Tfvc)
        process_template_id: ID of the process template to use (if None, default will be used)
        visibility: Project visibility (private or public)
        
    Returns:
        Dictionary containing the operation details
    """
    try:
        # Create capabilities dictionary
        capabilities = {
            "versioncontrol": {
                "sourceControlType": source_control_type
            }
        }
        
        # Set process template capability if provided
        if process_template_id:
            capabilities["processTemplate"] = {
                "templateTypeId": process_template_id
            }
        
        # Create project properties dictionary
        project_properties = {
            "name": name,
            "description": description,
            "capabilities": capabilities,
            "visibility": visibility
        }
        
        # Queue project creation
        operation_reference = core_client.queue_create_project(project_properties)
        
        # Return operation reference details
        return {
            "id": operation_reference.id,
            "status": operation_reference.status,
            "url": operation_reference.url
        }
    except Exception as e:
        return f"Error creating project: {str(e)}"

def _check_operation_status_impl(
    core_client: CoreClient,
    operation_id: str
) -> Dict[str, Any]:
    """
    Implementation of operation status checking.
    
    Args:
        core_client: Core client
        operation_id: ID of the operation to check
        
    Returns:
        Dictionary containing the operation details
    """
    try:
        operation = core_client.get_operation(operation_id)
        return {
            "id": operation.id,
            "status": operation.status,
            "created": operation.created_date,
            "modified": operation.last_modified_date,
            "url": operation.url,
            "detailed_message": operation.detailed_message
        }
    except Exception as e:
        return f"Error checking operation status: {str(e)}"

def _list_process_templates_impl(
    core_client: CoreClient
) -> str:
    """
    Implementation of process template listing.

    Args:
        core_client: Core client
        
    Returns:
        Formatted string containing all available process templates with their IDs
    """
    try:
        templates = core_client.list_process_templates()
        return "\n".join([
            f"- **{template.name}**: {template.id} ({template.description})"
            for template in templates
        ])
    except Exception as e:
        return f"Error listing process templates: {str(e)}"


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
        
    @mcp.tool()
    def create_project(
        name: str, 
        description: str = None, 
        source_control_type: str = "Git", 
        process_template_id: str = None, 
        visibility: str = "private"
    ):
        """
        Creates a new project in Azure DevOps.
        
        Use this tool when you need to:
        - Create a new project in your Azure DevOps organization
        - Set up a project with specific version control and process templates
        - Establish a new workspace for team collaboration
        
        IMPORTANT: You must have permissions to create projects in the organization.
        
        Args:
            name: The name of the project to create
            description: Optional description of the project
            source_control_type: Type of version control to use (Git or Tfvc)
            process_template_id: ID of the process template to use (if None, default will be used)
            visibility: Project visibility (private or public)
            
        Returns:
            A formatted string containing the details of the project creation operation,
            including the operation ID, status, and URL to check the operation status
        """
        try:
            # Get core client
            core_client = get_core_client()
            
            # Verify user has permission to create projects
            try:
                # Try to get projects as a simple permission check
                # If this fails with authorization error, user doesn't have permission
                core_client.get_projects(top=1)
            except Exception as e:
                if 'authorized' in str(e).lower() or 'permission' in str(e).lower():
                    return "Error: You do not have permission to create projects in this organization. Please contact your Azure DevOps administrator for assistance."
                # If it's not a permission error, continue with project creation
            
            # Create the project using the implementation function
            operation = _create_project_impl(
                core_client,
                name=name,
                description=description,
                source_control_type=source_control_type,
                process_template_id=process_template_id,
                visibility=visibility
            )
            
            # Check if operation is a string (error message)
            if isinstance(operation, str):
                return f"Error: {operation}"
                
            # Format and return the response
            return f"""
# Project Creation Initiated: {name}

The project creation has been queued in Azure DevOps.

**Operation Details:**
- Operation ID: {operation['id']}
- Status: {operation['status']}
- Status URL: {operation['url']}

Project creation may take a few minutes to complete. You can check the status using the `check_project_creation_status` tool with the Operation ID.
"""
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error creating project: {str(e)}"

    @mcp.tool()
    def check_project_creation_status(operation_id: str):
        """
        Checks the status of a project creation operation.
        
        Use this tool when you need to:
        - Follow up on a project creation operation
        - Check if a project has been successfully created
        - Troubleshoot a project creation that may have failed
        
        Args:
            operation_id: The ID of the operation to check
            
        Returns:
            A formatted string containing the current status of the operation
        """
        try:
            # Get the core client
            core_client = get_core_client()
            
            # Check the operation status
            operation = _check_operation_status_impl(core_client, operation_id)
            
            # Check if operation is a string (error message)
            if isinstance(operation, str):
                return f"Error: {operation}"
            
            # Format and return the response
            status_message = f"""
# Operation Status: {operation['status']}

**Operation Details:**
- Operation ID: {operation['id']}
- Status: {operation['status']}
- Created: {operation['created']}
- Modified: {operation['modified']}
- URL: {operation['url']}
"""
            
            # Add completion message if available
            if 'detailed_message' in operation and operation['detailed_message']:
                status_message += f"\n**Completion Message:** {operation['detailed_message']}\n"
                
            # Add status-specific guidance
            if operation['status'].lower() == 'succeeded':
                status_message += "\nThe project has been successfully created. You can now use it in Azure DevOps."
            elif operation['status'].lower() == 'failed':
                status_message += "\nThe project creation has failed. Please check the completion message for details or contact your Azure DevOps administrator."
            elif operation['status'].lower() == 'in progress':
                status_message += "\nThe project creation is still in progress. Please check again later using this tool with the same operation ID."
            
            return status_message
            
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error checking operation status: {str(e)}"

    @mcp.tool()
    def get_process_templates():
        """
        Lists all available process templates that can be used when creating projects.
        
        Use this tool when you need to:
        - Find available process templates before creating a project
        - Get the ID of a specific process template
        - See which process templates are available in your organization
        
        Returns:
            A formatted string containing all available process templates with their IDs
        """
        try:
            # Get the core client
            core_client = get_core_client()
            
            # Get the process templates
            templates = _list_process_templates_impl(core_client)
            
            # Check if templates is a string (error message)
            if isinstance(templates, str) and "Error" in templates:
                return templates
            
            # Format the output for better readability
            return f"""
# Available Process Templates

Use these templates when creating projects with the `create_project` tool by specifying the process_template_id parameter.

{templates}
"""
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error retrieving process templates: {str(e)}"
