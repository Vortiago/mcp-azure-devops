"""
Comment operations for Azure DevOps pull requests.

This module provides MCP tools for working with pull request comments.
"""
from typing import Optional
from azure.devops.v7_1.git import GitClient
from azure.devops.v7_1.git.models import Comment, GitPullRequestCommentThread

from mcp_azure_devops.features.pull_requests.common import (
    AzureDevOpsClientError,
    get_git_client
)


def _add_comment_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    project: str,
    content: str,
    comment_thread_id: Optional[int] = None,
    parent_comment_id: Optional[int] = None
) -> str:
    """
    Implementation of comment addition.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        project: Project name
        content: Comment text
        comment_thread_id: ID of existing thread (for replies)
        parent_comment_id: ID of parent comment (for replies)
    
    Returns:
        Formatted string containing comment information
    """
    try:
        if comment_thread_id:
            # Add comment to existing thread
            comment = Comment(content=content)
            if parent_comment_id:
                comment.parent_comment_id = parent_comment_id
            
            result = git_client.create_comment(
                comment=comment,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                thread_id=comment_thread_id,
                project=project
            )
            
            comment_id = result.id if hasattr(result, 'id') else 'Unknown'
            return f"Comment added successfully to thread #{comment_thread_id}:\nComment ID: {comment_id}\nContent: {content}"
        else:
            # Create new thread with comment
            comment = Comment(content=content)
            thread = GitPullRequestCommentThread(comments=[comment], status="active")
            
            result = git_client.create_thread(
                comment_thread=thread,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project
            )
            
            thread_id = result.id if hasattr(result, 'id') else 'Unknown'
            comment_id = result.comments[0].id if hasattr(result, 'comments') and result.comments else 'Unknown'
            
            return f"Comment thread created successfully:\nThread ID: {thread_id}\nComment ID: {comment_id}\nContent: {content}"
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to add comment: {str(e)}")


def _get_pull_request_thread_comments_impl(
    git_client: GitClient,
    repository_id: str,
    pull_request_id: int,
    thread_id: int,
    project: str
) -> str:
    """
    Implementation for getting comments in a PR thread.
    
    Args:
        git_client: Git client
        repository_id: Repository ID
        pull_request_id: ID of the PR
        thread_id: ID of the thread
        project: Project name
    
    Returns:
        Formatted string containing comment information
    """
    try:
        comments = git_client.get_comments(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            thread_id=thread_id,
            project=project
        )
        
        if not comments:
            return f"No comments found in thread #{thread_id} of pull request #{pull_request_id}."
        
        result = f"Comments in thread #{thread_id} of PR #{pull_request_id}:\n\n"
        
        for i, comment in enumerate(comments, 1):
            author = "Unknown"
            if hasattr(comment, 'author') and comment.author:
                if hasattr(comment.author, 'display_name'):
                    author = comment.author.display_name
            
            content = comment.content if hasattr(comment, 'content') else 'No content'
            
            date = "Unknown date"
            if hasattr(comment, 'published_date') and comment.published_date:
                date = comment.published_date
            
            result += f"{i}. Author: {author}\n"
            result += f"   Date: {date}\n"
            result += f"   Content: {content}\n\n"
        
        return result
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to get thread comments: {str(e)}")


def register_tools(mcp) -> None:
    """
    Register pull request comment tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def add_comment(
        project: str,
        repository_id: str,
        pull_request_id: int,
        content: str,
        comment_thread_id: Optional[int] = None,
        parent_comment_id: Optional[int] = None
    ) -> str:
        """
        Add a comment to a Pull Request in Azure DevOps.
        
        Use this tool when you need to:
        - Provide feedback on a pull request
        - Start a new discussion on a pull request
        - Reply to an existing comment thread
        - Add information or notes to a pull request
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
            content: Comment text
            comment_thread_id: ID of existing thread for replies (optional)
            parent_comment_id: ID of parent comment for nested replies (optional)
        
        Returns:
            Formatted string containing comment information
        """
        try:
            git_client = get_git_client()
            return _add_comment_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                project=project,
                content=content,
                comment_thread_id=comment_thread_id,
                parent_comment_id=parent_comment_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_pull_request_thread_comments(
        project: str,
        repository_id: str,
        pull_request_id: int,
        thread_id: int
    ) -> str:
        """
        Get all comments in a Pull Request thread in Azure DevOps.
        
        Use this tool when you need to:
        - View all comments in a specific discussion thread
        - Read feedback from reviewers
        - Check the history of a conversation on a pull request
        - Follow up on a particular discussion point
        
        Args:
            project: Azure DevOps project name
            repository_id: Azure DevOps repository ID or name
            pull_request_id: ID of the PR
            thread_id: ID of the comment thread
        
        Returns:
            Formatted string containing comments in the thread
        """
        try:
            git_client = get_git_client()
            return _get_pull_request_thread_comments_impl(
                git_client=git_client,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                thread_id=thread_id,
                project=project
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
