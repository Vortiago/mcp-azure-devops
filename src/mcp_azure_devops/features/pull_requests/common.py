"""
Common utilities for Azure DevOps pull request features.

This module provides shared functionality used by both tools and resources.
"""
from typing import Dict, List, Optional, Any
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.git.models import (
    GitPullRequest, 
    GitPullRequestSearchCriteria,
    Comment,    
    GitPullRequestCommentThread,
    IdentityRefWithVote
)

from mcp_azure_devops.utils.azure_client import get_connection

class AzureDevOpsClientError(Exception):
    """Exception raised for errors in Azure DevOps client operations."""
    pass


def get_pull_request_client():
    """
    Get the pull request client for Azure DevOps.
    
    Returns:
        Git client instance
    
    Raises:
        AzureDevOpsClientError: If connection or client creation fails
    """
    # Get connection to Azure DevOps
    connection = get_connection()
    
    if not connection:
        raise AzureDevOpsClientError(
            "Azure DevOps PAT or organization URL not found in environment variables."
        )
    
    # Get the git client
    git_client = connection.clients.get_git_client()
    
    if git_client is None:
        raise AzureDevOpsClientError("Failed to get git client.")
    
    return git_client


class AzureDevOpsClient:
    """Client for Azure DevOps API operations related to Pull Requests."""
    
    def __init__(self, organization: str, project: str, repo: str):
        """
        Initialize the Azure DevOps client.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
        """
        self.organization = organization
        self.project = project
        self.repo = repo
        self.git_client = get_pull_request_client()
    
    def create_pull_request(self, title: str, description: str, source_branch: str,
                        target_branch: str, reviewers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new Pull Request.
        
        Args:
            title: PR title
            description: PR description
            source_branch: Source branch name
            target_branch: Target branch name
            reviewers: List of reviewer emails or IDs
            
        Returns:
            Details of the created PR
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            # Create the PR object
            pull_request = GitPullRequest(
                source_ref_name=f"refs/heads/{source_branch}",
                target_ref_name=f"refs/heads/{target_branch}",
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
            result = self.git_client.create_pull_request(
                git_pull_request=pull_request,
                repository_id=self.repo,
                project=self.project
            )
            
            return result.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to create pull request: {str(e)}")
    
    def update_pull_request(self, pull_request_id: int, 
                           update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing Pull Request.
        
        Args:
            pull_request_id: ID of the PR to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated PR details
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            # First get the existing PR
            existing_pr = self.git_client.get_pull_request(
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            # Update the PR object with new values
            for key, value in update_data.items():
                setattr(existing_pr, key, value)
            
            # Send the update
            result = self.git_client.update_pull_request(
                git_pull_request=existing_pr,
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            return result.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to update pull request: {str(e)}")
    
    def get_pull_requests(self, status: Optional[str] = None, 
                         creator: Optional[str] = None,
                         reviewer: Optional[str] = None,
                         target_branch: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List Pull Requests with optional filtering.
        
        Args:
            status: Filter by status (active, abandoned, completed, all)
            creator: Filter by creator ID
            reviewer: Filter by reviewer ID
            target_branch: Filter by target branch name
            
        Returns:
            List of matching PRs
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            # Create search criteria
            search_criteria = GitPullRequestSearchCriteria()
            
            if status:
                search_criteria.status = status
            if creator:
                search_criteria.creator_id = creator
            if reviewer:
                search_criteria.reviewer_id = reviewer
            if target_branch:
                search_criteria.target_ref_name = f"refs/heads/{target_branch}"
            
            # Get pull requests
            pull_requests = self.git_client.get_pull_requests(
                repository_id=self.repo,
                search_criteria=search_criteria,
                project=self.project
            )
            
            # Convert to list of dictionaries
            return [pr.__dict__ for pr in pull_requests]
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to get pull requests: {str(e)}")
    
    def get_pull_request(self, pull_request_id: int) -> Dict[str, Any]:
        """
        Get details of a specific Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            
        Returns:
            Pull Request details
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            result = self.git_client.get_pull_request(
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            return result.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to get pull request: {str(e)}")
    
    def add_comment(self, pull_request_id: int, content: str, 
                   comment_thread_id: Optional[int] = None,
                   parent_comment_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Add a comment to a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            content: Comment text
            comment_thread_id: ID of existing thread (for replies)
            parent_comment_id: ID of parent comment (for replies)
            
        Returns:
            Comment details
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            if comment_thread_id:
                # Add comment to existing thread
                comment = Comment(content=content)
                if parent_comment_id:
                    comment.parent_comment_id = parent_comment_id
                
                result = self.git_client.create_comment(
                    comment=comment,
                    repository_id=self.repo,
                    pull_request_id=pull_request_id,
                    thread_id=comment_thread_id,
                    project=self.project
                )
            else:
                # Create new thread with comment
                comment = Comment(content=content)
                thread = GitPullRequestCommentThread(comments=[comment], status="active")
                
                result = self.git_client.create_thread(
                    comment_thread=thread,
                    repository_id=self.repo,
                    pull_request_id=pull_request_id,
                    project=self.project
                )
            
            return result.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to add comment: {str(e)}")
    
    def set_vote(self, pull_request_id: int, vote: int) -> Dict[str, Any]:
        """
        Vote on a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            vote: Vote value (10=approve, 5=approve with suggestions, 0=no vote, -5=wait for author, -10=reject)
            
        Returns:
            Updated reviewer details
            
        Raises:
            AzureDevOpsClientError: If request fails
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
            
            # Create reviewer object with vote
            reviewer = IdentityRefWithVote(id=self_identity.id, vote=vote)
            
            # Update the vote
            result = self.git_client.create_pull_request_reviewer(
                reviewer=reviewer,
                repository_id=self.repo,
                pull_request_id=pull_request_id,
                reviewer_id=self_identity.id,
                project=self.project
            )
            
            return result.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to set vote: {str(e)}")
    
    def complete_pull_request(self, pull_request_id: int, 
                             merge_strategy: str = "squash",
                             delete_source_branch: bool = False) -> Dict[str, Any]:
        """
        Complete (merge) a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            merge_strategy: Strategy to use (squash, rebase, rebaseMerge, merge)
            delete_source_branch: Whether to delete source branch after merge
            
        Returns:
            Completed PR details
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            # First get the current PR
            pull_request = self.git_client.get_pull_request(
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            # Update status and completion options
            pull_request.status = "completed"
            pull_request.completion_options = {
                "merge_strategy": merge_strategy,
                "delete_source_branch": delete_source_branch
            }
            
            # Complete the PR
            result = self.git_client.update_pull_request(
                git_pull_request=pull_request,
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            return result.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to complete pull request: {str(e)}")
        
    def get_pull_request_work_items(self, pull_request_id: int) -> List[Dict[str, Any]]:
        """
        Get work items linked to a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            
        Returns:
            List of work items linked to the PR
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            work_items = self.git_client.get_pull_request_work_items(
                repository_id=self.repo,
                pull_request_id=pull_request_id,
                project=self.project
            )
            
            return [work_item.__dict__ for work_item in work_items]
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to get pull request work items: {str(e)}")
        
    def add_work_items_to_pull_request(self, pull_request_id: int, work_item_ids: List[int]) -> bool:
        """
        Link work items to a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            work_item_ids: List of work item IDs to link
            
        Returns:
            True if successful
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            for work_item_id in work_item_ids:
                self.git_client.create_pull_request_work_item_refs(
                    repository_id=self.repo,
                    pull_request_id=pull_request_id,
                    project=self.project,
                    work_item_ids=[work_item_id]
                )
            
            return True
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to link work items to pull request: {str(e)}")
        
    def get_pull_request_commits(self, pull_request_id: int) -> List[Dict[str, Any]]:
        """
        Get all commits in a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
                
        Returns:
            List of commits in the PR
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            # Print debug information
            print(f"Fetching commits for PR #{pull_request_id}")
            print(f"Repository ID: {self.repo}")
            print(f"Project: {self.project}")
            
            # Make the API call with correct parameters
            commits = self.git_client.get_pull_request_commits(
                repository_id=self.repo,
                pull_request_id=pull_request_id,
                project=self.project
            )
            
            # Convert the GitCommitRef objects to dictionaries properly
            result = []
            for commit in commits:
                # Convert the commit to a dictionary in a safer way
                commit_dict = {}
                
                # Common properties in GitCommitRef
                if hasattr(commit, 'commit_id'):
                    commit_dict['commitId'] = commit.commit_id
                
                if hasattr(commit, 'author'):
                    commit_dict['author'] = {
                        'name': getattr(commit.author, 'name', None),
                        'email': getattr(commit.author, 'email', None),
                        'date': getattr(commit.author, 'date', None)
                    }
                
                if hasattr(commit, 'committer'):
                    commit_dict['committer'] = {
                        'name': getattr(commit.committer, 'name', None),
                        'date': getattr(commit.committer, 'date', None)
                    }
                
                if hasattr(commit, 'comment'):
                    commit_dict['comment'] = commit.comment
                
                result.append(commit_dict)
            
            return result
        except Exception as e:
            # Add more details to help with debugging
            error_message = f"Failed to get pull request commits: {str(e)}"
            print(error_message)  # Print for immediate debugging
            raise AzureDevOpsClientError(error_message)
        
    
    def get_pull_request_changes(self, pull_request_id: int) -> Dict[str, Any]:
        """
        Get all changes (files) in a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            
        Returns:
            Changes in the PR
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            changes = self.git_client.get_pull_request_iterations_changes(
                repository_id=self.repo,
                pull_request_id=pull_request_id,
                project=self.project
            )
            
            return changes.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to get pull request changes: {str(e)}")
        
    def get_pull_request_thread_comments(self, pull_request_id: int, thread_id: int) -> List[Dict[str, Any]]:
        """
        Get all comments in a PR thread.
        
        Args:
            pull_request_id: ID of the PR
            thread_id: ID of the thread
            
        Returns:
            List of comments in the thread
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            comments = self.git_client.get_comments(
                repository_id=self.repo,
                pull_request_id=pull_request_id,
                thread_id=thread_id,
                project=self.project
            )
            
            return [comment.__dict__ for comment in comments]
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to get thread comments: {str(e)}")
        
    def abandon_pull_request(self, pull_request_id: int) -> Dict[str, Any]:
        """
        Abandon a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            
        Returns:
            Updated PR details
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            # First get the current PR
            pull_request = self.git_client.get_pull_request(
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            # Update status to abandoned
            pull_request.status = "abandoned"
            
            # Abandon the PR
            result = self.git_client.update_pull_request(
                git_pull_request=pull_request,
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            return result.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to abandon pull request: {str(e)}")
        
    def reactivate_pull_request(self, pull_request_id: int) -> Dict[str, Any]:
        """
        Reactivate an abandoned Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            
        Returns:
            Updated PR details
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            # First get the current PR
            pull_request = self.git_client.get_pull_request(
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            # Update status to active
            pull_request.status = "active"
            
            # Reactivate the PR
            result = self.git_client.update_pull_request(
                git_pull_request=pull_request,
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            return result.__dict__
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to reactivate pull request: {str(e)}")
        
    def get_pull_request_policy_evaluations(self, pull_request_id: int) -> List[Dict[str, Any]]:
        """
        Get policy evaluations for a Pull Request.
        
        Args:
            pull_request_id: ID of the PR
            
        Returns:
            List of policy evaluations
            
        Raises:
            AzureDevOpsClientError: If request fails
        """
        try:
            # Get the PR details first
            pr = self.git_client.get_pull_request(
                repository_id=self.repo,
                project=self.project,
                pull_request_id=pull_request_id
            )
            
            # Get the policy client
            connection = get_connection()
            if not connection:
                raise AzureDevOpsClientError(
                    "Azure DevOps PAT or organization URL not found in environment variables."
                )
            policy_client = connection.clients.get_policy_client()
            
            # Get policy evaluations
            evaluations = policy_client.get_policy_evaluations(
                project=self.project,
                artifact_id=f"vstfs:///Git/PullRequestId/{pr.repository.project.id}/{pull_request_id}"
            )
            
            return [evaluation.__dict__ for evaluation in evaluations]
        except Exception as e:
            raise AzureDevOpsClientError(f"Failed to get policy evaluations: {str(e)}")