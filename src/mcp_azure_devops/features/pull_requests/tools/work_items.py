"""
Work item operations for Azure DevOps pull requests.

This module provides MCP tools for working with work items in pull requests.
"""
from typing import List
from azure.devops.v7_1.git import GitClient
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from mcp_azure_devops.features.work_items.common import get_work_item_client
from mcp_azure_devops.features.pull_requests.common import (
    AzureDevOpsClientError,
    get_git_client
)
from mcp_azure_devops.features.pull_requests.formatting import format_pull_request_work_item


def _get_pull_request_work_items_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str
) -> str:
    """
    Implementation for getting work items linked to a PR.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
    
    Returns:
        Formatted string containing linked work items information
    """
    try:
        # In the Azure DevOps SDK, getting work items is a complex operation
        # First, we need to get the PRs artifact ID
        pr = git_client.get_pull_request(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            project=project
        )
        
        if not pr:
            return f"Pull request #{pull_request_id} not found."
        
        # Use regular work item client to get associated work items
        wit_client = get_work_item_client()
        
        # The API actually uses get_pull_request_work_item_refs (unlike the name in original code)
        item_refs = git_client.get_pull_request_work_item_refs(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            project=project
        )
        
        if not item_refs:
            return f"No work items are linked to pull request #{pull_request_id}."
        
        # Extract the work item IDs
        work_item_ids = [item_ref.id for item_ref in item_refs if hasattr(item_ref, 'id')]
        
        if not work_item_ids:
            return f"No valid work item IDs found in pull request #{pull_request_id}."
        
        # Get the full work item details
        work_items = wit_client.get_work_items(ids=work_item_ids, expand="all")
        
        if not work_items:
            return f"Failed to retrieve work item details for pull request #{pull_request_id}."
        
        result = f"Work Items linked to PR #{pull_request_id}:\n\n"
        for i, item in enumerate(work_items, 1):
            if not item:
                continue
                
            # Get id and title from fields
            fields = item.fields if hasattr(item, 'fields') else {}
            item_id = item.id if hasattr(item, 'id') else "N/A"
            title = fields.get('System.Title', 'No title') if fields else 'No title'
            work_item_type = fields.get('System.WorkItemType', 'Unknown') if fields else 'Unknown'
            state = fields.get('System.State', 'Unknown') if fields else 'Unknown'
            
            result += f"{i}. ID: {item_id}\n"
            result += f"   Title: {title}\n"
            result += f"   Type: {work_item_type}\n"
            result += f"   State: {state}\n\n"
        
        return result
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to get pull request work items: {str(e)}")


def _add_work_items_to_pull_request_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str,
    work_item_ids: List[int]
) -> str:
    """
    Implementation for linking work items to a PR.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
        work_item_ids: List of work item IDs to link
    
    Returns:
        Formatted string indicating success or failure
    """
    try:
        # First ensure the PR exists
        pr = git_client.get_pull_request(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            project=project
        )
        
        if not pr:
            return f"Pull request #{pull_request_id} not found."
        
        # Check that the work items exist
        wit_client = get_work_item_client()
        work_items = wit_client.get_work_items(ids=work_item_ids, error_policy="omit")
        
        valid_work_items = [item.id for item in work_items if item]
        if not valid_work_items:
            return "None of the provided work item IDs could be found."
        
        # Using the Azure DevOps REST API via git_client, there's a method to link work items
        # We add artifacts, which are the work items, to the pull request
        for work_item_id in valid_work_items:
            # The correct method in the Azure DevOps Python SDK is:
            git_client.create_pull_request_work_items(
                work_item_ids=[work_item_id],
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project
            )
        
        work_items_str = ", ".join([str(id) for id in valid_work_items])
        return f"Successfully linked work item(s) #{work_items_str} to pull request #{pull_request_id}."
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to link work items to pull request: {str(e)}")


def register_tools(mcp) -> None:
    """
    Register pull request work item tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_pull_request_work_items(
        project: str,
        repository_id: str,
        pull_request_id: int
    ) -> str:
        """
        Get work items linked to a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - View which work items are associated with a pull request
        - Check which user stories, bugs or tasks are being addressed
        - Verify work item linkage for traceability
        - Report on pull request and work item relationships
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing linked work items information
        """
        try:
            git_client = get_git_client()
            return _get_pull_request_work_items_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def add_work_items_to_pull_request(
        project: str,
        repository_id: str,
        pull_request_id: int,
        work_item_ids: str
    ) -> str:
        """
        Link work items to a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Associate work items with a pull request
        - Connect code changes to user stories, bugs, or tasks
        - Establish traceability between code and requirements
        - Document which items are being addressed by a code change
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
            work_item_ids: Comma-separated list of work item IDs to link
        
        Returns:
            Formatted string indicating success or failure
        """
        try:
            git_client = get_git_client()
            
            # Parse the comma-separated list of work item IDs
            try:
                work_item_id_list = [int(id.strip()) for id in work_item_ids.split(",")]
                
                if not work_item_id_list:
                    return "Error: No valid work item IDs provided."
                
                return _add_work_items_to_pull_request_impl(
                    git_client=git_client,
                    repository_id=repository_id,
                    pull_request_id=pull_request_id,
                    project=project,
                    work_item_ids=work_item_id_list
                )
            except ValueError:
                return "Error: Work item IDs must be valid integers separated by commas."
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
