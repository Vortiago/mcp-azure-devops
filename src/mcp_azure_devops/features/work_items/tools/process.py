"""
Process operations for Azure DevOps.

This module provides MCP tools for retrieving process information.
"""
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


def _get_project_process_id_impl(project: str) -> str:
    """Implementation of project process ID retrieval."""
    try:
        # Get project details with process information
        core_client = get_core_client()
        project_details = core_client.get_project(
            project, include_capabilities=True)
        process_template = project_details.capabilities.get(
            "processTemplate", {})
        
        process_id = process_template.get("templateTypeId")
        process_name = process_template.get("templateName")
        
        if not process_id:
            return f"Could not determine process ID for project {project}."
        
        result = [f"# Process for Project: {project_details.name}"]
        result.append(f"Process Name: {process_name}")
        result.append(f"Process ID: {process_id}")
        
        return "\n".join(result)
    except Exception as e:
        return (f"Error retrieving process ID for project '{project}': "
                f"{str(e)}")


def _get_process_details_impl(process_id: str) -> str:
    """Implementation of process details retrieval."""
    try:
        process_client = get_work_item_tracking_process_client()
        process = process_client.get_process_by_its_id(process_id)
        
        if not process:
            return f"Process with ID '{process_id}' not found."
        
        result = [f"# Process: {process.name}"]
        
        if hasattr(process, "description") and process.description:
            result.append(f"\nDescription: {process.description}")
        
        result.append(
            f"Reference Name: {getattr(process, 'reference_name', 'N/A')}")
        result.append(f"Type ID: {getattr(process, 'type_id', 'N/A')}")
        
        # Get process properties like isDefault, isEnabled, etc.
        properties = getattr(process, "properties", None)
        if properties:
            result.append("\n## Properties")
            for attr in ["is_default", "is_enabled"]:
                value = getattr(properties, attr, None)
                if value is not None:
                    attr_name = attr.replace("_", " ").capitalize()
                    result.append(f"{attr_name}: {value}")
        
        # Get work item types for this process
        wit_types = process_client.get_process_work_item_types(process_id)
        if wit_types:
            result.append("\n## Work Item Types")
            
            headers = ["Name", "Reference Name", "Description"]
            rows = [
                f"| {wit.name} | {getattr(wit, 'reference_name', 'N/A')} | " +
                f"{getattr(wit, 'description', 'N/A')} |"
                for wit in wit_types
            ]
            
            result.append(_format_table(headers, rows))
        
        return "\n".join(result)
    except Exception as e:
        return (f"Error retrieving process details for process ID "
                f"'{process_id}': {str(e)}")


def _list_processes_impl() -> str:
    """Implementation of processes list retrieval."""
    try:
        process_client = get_work_item_tracking_process_client()
        processes = process_client.get_list_of_processes()
        
        if not processes:
            return "No processes found in the organization."
        
        result = ["# Available Processes"]
        
        headers = ["Name", "ID", "Reference Name", "Description", "Is Default"]
        rows = []
        for process in processes:
            is_default = "Yes" if getattr(process.properties, 'is_default', False) else "No"
            row = (f"| {process.name} | {process.type_id} | " +
                   f"{getattr(process, 'reference_name', 'N/A')} | " +
                   f"{getattr(process, 'description', 'N/A')} | {is_default} |")
            rows.append(row)
        
        result.append(_format_table(headers, rows))
        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving processes: {str(e)}"


def register_tools(mcp) -> None:
    """
    Register process tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_project_process_id(project: str) -> str:
        """
        Gets the process ID associated with a project.
        
        Use this tool when you need to:
        - Find out which process a project is using
        - Get the process ID for use in other process-related operations
        - Verify process information for a project
        
        Args:
            project: Project ID or project name
            
        Returns:
            Formatted information about the process including name and ID
        """
        try:
            return _get_project_process_id_impl(project)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_process_details(process_id: str) -> str:
        """
        Gets detailed information about a specific process.
        
        Use this tool when you need to:
        - View process properties and configuration
        - Get a list of work item types defined in a process
        - Check if a process is the default for the organization
        
        Args:
            process_id: The ID of the process
            
        Returns:
            Detailed information about the process including properties and
            available work item types
        """
        try:
            return _get_process_details_impl(process_id)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def list_processes() -> str:
        """
        Lists all available processes in the organization.
        
        Use this tool when you need to:
        - See what processes are available in your Azure DevOps organization
        - Find process IDs for project creation or configuration
        - Check which process is set as the default
        
        Returns:
            A formatted table of all processes with names, IDs, and 
            descriptions
        """
        try:
            return _list_processes_impl()
        except Exception as e:
            return f"Error: {str(e)}"
