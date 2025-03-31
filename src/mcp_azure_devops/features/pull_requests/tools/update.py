"""
Update operations for Azure DevOps pull requests.

This module provides MCP tools for updating pull request status and information.
"""
from typing import Optional
from azure.devops.v7_1.git import GitClient
from azure.devops.v7_1.git.models import IdentityRefWithVote

from mcp_azure_devops.features.pull_requests.common import (
    AzureDevOpsClientError,
    get_git_client
)
from mcp_azure_devops.features.pull_requests.formatting import format_pull_request
from mcp_azure_devops.utils.azure_client import get_connection


def _update_pull_request_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    Implementation of pull request update.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR to update
        project: Project name
        title: New PR title (optional)
        description: New PR description (optional)
        status: New PR status (optional)
    
    Returns:
        Formatted string containing updated pull request information
    """
    try:
        # First get the existing PR
        pr = git_client.get_pull_request(
            repository_id=repository_id,
            project=project,
            pull_request_id=pull_request_id
        )
        
        # Validate status if provided
        if status and status not in ('active', 'abandoned', 'completed'):
            raise AzureDevOpsClientError(
                f"Invalid status: {status}. Must be 'active', 'abandoned', or 'completed'."
            )
        
        # Update the PR object with new values
        if title is not None:
            pr.title = title
        if description is not None:
            pr.description = description
        if status is not None:
            pr.status = status
        
        # Send the update
        updated_pr = git_client.update_pull_request(
            pr,
            repository_id=repository_id,
            project=project,
            pull_request_id=pull_request_id
        )
        
        return format_pull_request(updated_pr)
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to update pull request: {str(e)}")


def _vote_on_pull_request_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str,
    vote: int
) -> str:
    """
    Implementation of pull request voting.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
        vote: Vote value (10=approve, 5=approve with suggestions, 0=no vote, -5=wait for author, -10=reject)
    
    Returns:
        Formatted string containing voting information
    """
    try:
        # First get the current user's identity
        connection = get_connection()
        if not connection:
            raise AzureDevOpsClientError(
                "Azure DevOps PAT or organization URL not found in environment variables."
            )
        identity_client = connection.clients.get_identity_client()
        self_identity = identity_client.get_self()
        
        # Validate vote value
        valid_votes = (-10, -5, 0, 5, 10)
        if vote not in valid_votes:
            raise AzureDevOpsClientError(
                f"Invalid vote value: {vote}. Must be one of {valid_votes}."
            )
        
        # Create reviewer object with vote
        reviewer = IdentityRefWithVote(id=self_identity.id, vote=vote)
        
        # Update the vote
        result = git_client.create_pull_request_reviewer(
            reviewer,
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            reviewer_id=self_identity.id,
            project=project
        )
        
        # Format the response based on the vote value
        vote_descriptions = {
            10: "approved",
            5: "approved with suggestions",
            0: "reset their vote on",
            -5: "is waiting for the author on",
            -10: "rejected"
        }
        
        vote_description = vote_descriptions.get(vote, "voted on")
        display_name = result.display_name if hasattr(result, 'display_name') else "User"
        
        return f"{display_name} has {vote_description} pull request #{pull_request_id}."
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to vote on pull request: {str(e)}")


def _complete_pull_request_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str,
    merge_strategy: str = "squash",
    delete_source_branch: bool = False,
    merge_commit_message: Optional[str] = None
) -> str:
    """
    Implementation of pull request completion.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
        merge_strategy: Strategy to use (squash, rebase, rebaseMerge, merge)
        delete_source_branch: Whether to delete source branch after merge
        merge_commit_message: Custom merge commit message
    
    Returns:
        Formatted string containing completion information
    """
    try:
        # Validate merge strategy
        valid_strategies = ('squash', 'rebase', 'rebaseMerge', 'merge')
        if merge_strategy not in valid_strategies:
            raise AzureDevOpsClientError(
                f"Invalid merge strategy: {merge_strategy}. Must be one of {valid_strategies}."
            )
        
        # First get the current PR
        pr = git_client.get_pull_request(
            repository_id=repository_id,
            project=project,
            pull_request_id=pull_request_id
        )
        
        # Update status to completed
        pr.status = "completed"
        
        # Set merge options
        if merge_strategy:
            pr.merge_strategy = merge_strategy
        
        if delete_source_branch:
            pr.delete_source_branch = delete_source_branch
            
        if merge_commit_message:
            pr.merge_commit_message = merge_commit_message
        
        # Complete the PR
        completed_pr = git_client.update_pull_request(
            pr,
            repository_id=repository_id,
            project=project,
            pull_request_id=pull_request_id
        )
        
        # Format the response
        response_lines = [f"Pull request #{pull_request_id} has been completed successfully."]
        
        if hasattr(completed_pr, 'closed_by') and completed_pr.closed_by:
            if hasattr(completed_pr.closed_by, 'display_name'):
                response_lines.append(f"Completed by: {completed_pr.closed_by.display_name}")
        
        response_lines.append(f"Merge strategy: {merge_strategy}")
        response_lines.append(f"Source branch deleted: {delete_source_branch}")
        
        return "\n".join(response_lines)
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to complete pull request: {str(e)}")


def _abandon_pull_request_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str
) -> str:
    """
    Implementation of pull request abandonment.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
    
    Returns:
        Formatted string containing abandonment information
    """
    try:
        # First get the current PR
        pr = git_client.get_pull_request(
            repository_id=repository_id,
            project=project,
            pull_request_id=pull_request_id
        )
        
        # Update status to abandoned
        pr.status = "abandoned"
        
        # Abandon the PR
        abandoned_pr = git_client.update_pull_request(
            pr,
            repository_id=repository_id,
            project=project,
            pull_request_id=pull_request_id
        )
        
        return f"Pull request #{pull_request_id} has been abandoned successfully."
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to abandon pull request: {str(e)}")


def _reactivate_pull_request_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str
) -> str:
    """
    Implementation of pull request reactivation.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
    
    Returns:
        Formatted string containing reactivation information
    """
    try:
        # First get the current PR
        pr = git_client.get_pull_request(
            repository_id=repository_id,
            project=project,
            pull_request_id=pull_request_id
        )
        
        # Update status to active
        pr.status = "active"
        
        # Reactivate the PR
        reactivated_pr = git_client.update_pull_request(
            pr,
            repository_id=repository_id,
            project=project,
            pull_request_id=pull_request_id
        )
        
        return f"Pull request #{pull_request_id} has been reactivated successfully."
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to reactivate pull request: {str(e)}")


def register_tools(mcp) -> None:
    """
    Register pull request update tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def update_pull_request(
        project: str,
        repository_id: str,
        pull_request_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Update an existing Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Change the title or description of a pull request
        - Update the status of a pull request
        - Modify pull request metadata without changing its content
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR to update
            title: New PR title (optional)
            description: New PR description (optional)
            status: New PR status (active, abandoned) (optional)
        
        Returns:
            Formatted string containing updated pull request information
        """
        try:
            git_client = get_git_client()
            return _update_pull_request_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project,
                title=title,
                description=description,
                status=status
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def approve_pull_request(
        project: str,
        repository_id: str,       
        pull_request_id: int
    ) -> str:
        """
        Approve a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Give approval for changes in a pull request
        - Signal that code is ready to be merged
        - Complete a code review with approval
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string confirming the approval
        """
        try:
            git_client = get_git_client()
            return _vote_on_pull_request_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project,
                vote=10  # 10 = Approve
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def reject_pull_request(
        project: str,
        repository_id: str,
        pull_request_id: int
    ) -> str:
        """
        Reject a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Indicate that changes are not acceptable
        - Request significant revisions to code
        - Block a pull request from being merged
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string confirming the rejection
        """
        try:
            git_client = get_git_client()
            return _vote_on_pull_request_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project,
                vote=-10  # -10 = Reject
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def complete_pull_request(
        project: str,
        repository_id: str,
        pull_request_id: int,
        merge_strategy: str = "squash",
        delete_source_branch: bool = False,
        merge_commit_message: Optional[str] = None
    ) -> str:
        """
        Complete (merge) a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Merge approved changes into the target branch
        - Complete the code review process
        - Finalize a pull request and apply changes
        - Optionally delete the source branch after merging
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
            merge_strategy: Merge strategy (squash, rebase, rebaseMerge, merge) (optional)
            delete_source_branch: Whether to delete source branch after merge (optional)
            merge_commit_message: Custom merge commit message (optional)
        
        Returns:
            Formatted string confirming the completion
        """
        try:
            git_client = get_git_client()
            return _complete_pull_request_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project,
                merge_strategy=merge_strategy,
                delete_source_branch=delete_source_branch,
                merge_commit_message=merge_commit_message
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def abandon_pull_request(
        project: str,
        repository_id: str,
        pull_request_id: int
    ) -> str:
        """
        Abandon a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Discard a pull request without merging it
        - Mark a pull request as no longer needed
        - Close a pull request that won't be completed
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string confirming the abandonment
        """
        try:
            git_client = get_git_client()
            return _abandon_pull_request_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def reactivate_pull_request(
        project: str,
        repository_id: str,
        pull_request_id: int
    ) -> str:
        """
        Reactivate an abandoned Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Restore a previously abandoned pull request
        - Resume work on a pull request that was closed
        - Re-open a pull request for further consideration
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string confirming the reactivation
        """
        try:
            git_client = get_git_client()
            return _reactivate_pull_request_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
