"""
Read operations for Azure DevOps pull requests.

This module provides MCP tools for retrieving pull request information.
"""
from typing import Optional, List
from azure.devops.v7_1.git import GitClient
from azure.devops.v7_1.git.models import GitPullRequestSearchCriteria

from mcp_azure_devops.features.pull_requests.common import (
    AzureDevOpsClientError,
    get_git_client
)
from mcp_azure_devops.features.pull_requests.formatting import (
    format_pull_request,
    format_commit
)


def _get_pull_request_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str
) -> str:
    """
    Implementation of pull request retrieval.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
    
    Returns:
        Formatted string containing pull request information
    """
    try:
        pr = git_client.get_pull_request(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            project=project
        )
        return format_pull_request(pr)
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to get pull request: {str(e)}")


def _list_pull_requests_impl(
    git_client: GitClient,
    repository_id: str,
    project: str,
    status: Optional[str] = None,
    creator_id: Optional[str] = None,
    reviewer_id: Optional[str] = None,
    target_branch: Optional[str] = None
) -> str:
    """
    Implementation of pull requests listing.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        project: Project name
        status: Filter by status (active, abandoned, completed, all)
        creator_id: Filter by creator ID
        reviewer_id: Filter by reviewer ID
        target_branch: Filter by target branch name
    
    Returns:
        Formatted string containing pull request information
    """
    try:
        # Create search criteria
        search_criteria = GitPullRequestSearchCriteria()
        
        if status:
            search_criteria.status = status
        if creator_id:
            search_criteria.creator_id = creator_id
        if reviewer_id:
            search_criteria.reviewer_id = reviewer_id
        if target_branch:
            search_criteria.target_ref_name = target_branch if target_branch.startswith('refs/') else f"refs/heads/{target_branch}"
        
        # Get pull requests
        pull_requests = git_client.get_pull_requests(
            repository_id=repository_id,
            search_criteria=search_criteria,
            project=project
        )
        
        if not pull_requests:
            return "No pull requests found."
        
        formatted_prs = []
        for pr in pull_requests:
            formatted_prs.append(format_pull_request(pr))
        
        return "\n\n".join(formatted_prs)
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to list pull requests: {str(e)}")


def _get_pull_request_commits_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str
) -> str:
    """
    Implementation for getting commits in a PR.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
    
    Returns:
        Formatted string containing commit information
    """
    try:
        commits = git_client.get_pull_request_commits(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            project=project
        )
        
        if not commits:
            return f"No commits found in pull request #{pull_request_id}."
        
        result = f"Commits in PR #{pull_request_id}:\n\n"
        for i, commit in enumerate(commits, 1):
            result += f"{i}. {format_commit(commit)}\n\n"
        
        return result
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to get pull request commits: {str(e)}")


def _get_pull_request_changes_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str
) -> str:
    """
    Implementation for getting changes in a PR.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
    
    Returns:
        Formatted string containing file change information
    """
    try:
        # Get the iterations
        iterations = git_client.get_pull_request_iterations(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            project=project
        )
        
        if not iterations:
            return f"No iterations found for pull request #{pull_request_id}."
        
        # Get changes for the latest iteration
        latest_iteration = iterations[-1]
        changes = git_client.get_pull_request_iteration_changes(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            iteration_id=latest_iteration.id,
            project=project
        )
        
        if not changes or not changes.changes:
            return f"No file changes found in pull request #{pull_request_id}."
        
        result = f"File changes in PR #{pull_request_id}:\n\n"
        
        additions = 0
        deletions = 0
        files_changed = 0
        
        for i, change in enumerate(changes.changes, 1):
            files_changed += 1
            change_type = change.change_type if hasattr(change, 'change_type') else 'unknown'
            
            item = change.item if hasattr(change, 'item') else None
            path = item.path if item and hasattr(item, 'path') else 'unknown'
            
            result += f"{i}. {path}\n"
            result += f"   Change type: {change_type}\n"
            
            if hasattr(change, 'line_count_additions'):
                additions += change.line_count_additions or 0
                result += f"   Additions: {change.line_count_additions or 0}\n"
                
            if hasattr(change, 'line_count_deletions'):
                deletions += change.line_count_deletions or 0
                result += f"   Deletions: {change.line_count_deletions or 0}\n"
            
            result += "\n"
        
        # Add summary
        result += f"Summary: {files_changed} files changed, {additions} additions, {deletions} deletions."
        
        return result
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to get pull request changes: {str(e)}")


def register_tools(mcp) -> None:
    """
    Register pull request read tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_pull_request(
        project: str,
        repository_id: str,
        pull_request_id: int
    ) -> str:
        """
        Get details of a specific Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - View detailed information about a specific pull request
        - Check the status of a pull request
        - See which branches are involved in a pull request
        - Get the URL for a specific pull request
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing pull request information including ID,
            status, branches, creator, creation date, and URL
        """
        try:
            git_client = get_git_client()
            return _get_pull_request_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def list_pull_requests(
        project: str,
        repository_id: str,
        status: Optional[str] = None,
        creator_id: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        target_branch: Optional[str] = None
    ) -> str:
        """
        List Pull Requests in Azure DevOps with optional filtering.
        
        Use this tool when you need to:
        - View all pull requests in a repository
        - Find pull requests with a specific status (active, abandoned, completed)
        - Filter pull requests by creator or reviewer
        - Find pull requests targeting a specific branch
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            status: Filter by status (active, abandoned, completed, all) (optional)
            creator_id: Filter by creator ID (optional)
            reviewer_id: Filter by reviewer ID (optional)
            target_branch: Filter by target branch name (optional)
        
        Returns:
            Formatted string containing a list of pull requests with their details
        """
        try:
            git_client = get_git_client()
            return _list_pull_requests_impl(
                git_client=git_client,
                repository_id=repository_id,
                project=project,
                status=status,
                creator_id=creator_id,
                reviewer_id=reviewer_id,
                target_branch=target_branch
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_pull_request_commits(
        project: str,
        repository_id: str,
        pull_request_id: int
    ) -> str:
        """
        Get all commits in a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - View the list of commits included in a pull request
        - Check which changes are part of a pull request
        - See the commit history for a pull request
        - Check who authored commits in a pull request
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing commit information for the pull request
        """
        try:
            git_client = get_git_client()
            return _get_pull_request_commits_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_pull_request_changes(
        project: str,
        repository_id: str,
        pull_request_id: int
    ) -> str:
        """
        Get all file changes in a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - View which files were modified in a pull request
        - See the number of additions and deletions in each file
        - Get a summary of changes in a pull request
        - Check how many files were changed in a pull request
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing file change information for the pull request
        """
        try:
            git_client = get_git_client()
            return _get_pull_request_changes_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
