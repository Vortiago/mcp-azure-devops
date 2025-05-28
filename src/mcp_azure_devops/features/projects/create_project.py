# Archivo: src/mcp_azure_devops/features/projects/create_project.py

from typing import Optional, Dict, Any

def create_project(
    core_client,
    name: str,
    description: Optional[str] = None,
    source_control_type: str = "Git",
    process_template_id: Optional[str] = None,
    visibility: str = "private"
) -> Dict[str, Any]:
    """
    Creates a new project in Azure DevOps.
    
    Args:
        core_client: The Azure DevOps core client
        name: Name of the project to create
        description: Optional description for the project
        source_control_type: Source control type (Git or Tfvc)
        process_template_id: Process template ID to use. If None, default template will be used.
        visibility: Project visibility (private or public)
        
    Returns:
        A dictionary containing the operation details
    """
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