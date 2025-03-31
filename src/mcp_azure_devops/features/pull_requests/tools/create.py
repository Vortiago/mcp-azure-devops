"""
Create operations for Azure DevOps pull requests.

This module provides MCP tools for creating pull requests.
"""
from typing import List, Optional
from azure.devops.v7_1.git import GitClient
from azure.devops.v7_1.git.models import GitPullRequest, IdentityRefWithVote

from mcp_azure_devops.features.pull_requests.common import (
    AzureDevOpsClientError,
    get_git_client
)
from mcp_azure_devops.features.pull_requests.formatting import format_pull_request


def _create_pull_request_impl(
    git_client: GitClient,
    title: str,
    source_branch: str,
    target_branch: str,
    repository_id: str,
    project: str,
    description: str = "",
    reviewers: Optional[List[str]] = None
) -> str:
    """
    Implementation of pull request creation.
    
    Args:
        git_client: Git client
        title: PR title
        source_branch: Source branch name
        target_branch: Target branch name
        repository_id: Repository ID
        project: Project name
        description: PR description (optional)
        reviewers: List of reviewer emails or IDs (optional)
    
    Returns:
        Formatted string containing pull request information
    """
    try:
        # Ensure branches have refs/heads/ prefix
        source_ref = source_branch if source_branch.startswith('refs/') else f'refs/heads/{source_branch}'
        target_ref = target_branch if target_branch.startswith('refs/') else f'refs/heads/{target_branch}'
        
        # Create the PR object
        pull_request = GitPullRequest(
            source_ref_name=source_ref,
            target_ref_name=target_ref,
            title=title,
            description=description
        )
        
        # Add reviewers if provided
        if reviewers:
            reviewer_refs = []
            for reviewer in reviewers:
                reviewer_refs.append(IdentityRefWithVote(id=reviewer))
            pull_request.reviewers = reviewer_refs
        
        # Create the pull request
        new_pr = git_client.create_pull_request(
            pull_request,
            repository_id=repository_id,
            project=project
        )
        
        return format_pull_request(new_pr)
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to create pull request: {str(e)}")


def register_tools(mcp) -> None:
    """
    Register pull request creation tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def create_pull_request(
        project: str,
        repository_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str = "",
        reviewers: Optional[List[str]] = None
    ) -> str:
        """
        Create a new Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Initiate a code review for changes
        - Merge code from a feature branch to a target branch
        - Document changes with title and description
        - Assign specific reviewers to a code change
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            title: PR title
            source_branch: Source branch name
            target_branch: Target branch name
            description: PR description (optional)
            reviewers: List of reviewer emails or IDs (optional)
        
        Returns:
            Formatted string containing pull request information including ID,
            status, branches, creator, and URL
        """
        try:
            git_client = get_git_client()
            return _create_pull_request_impl(
                git_client=git_client,
                title=title,
                source_branch=source_branch,
                target_branch=target_branch,
                repository_id=repository_id,
                project=project,
                description=description,
                reviewers=reviewers
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
