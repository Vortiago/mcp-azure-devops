"""
Formatting utilities for Azure DevOps pull request features.

This module provides formatting functions for pull request objects.
"""
from azure.devops.v7_1.git.models import (
    GitPullRequest,
    GitCommitRef,
    GitPullRequestCommentThread,
    IdentityRefWithVote
)


def format_pull_request(pr: GitPullRequest) -> str:
    """
    Format pull request information.
    
    Args:
        pr: Pull request object to format
    
    Returns:
        String with pull request details
    """
    formatted_info = [f"# Pull Request: {pr.title}"]
    formatted_info.append(f"ID: {pr.pull_request_id}")
    
    if pr.status:
        formatted_info.append(f"Status: {pr.status}")
    
    source_branch = pr.source_ref_name.replace('refs/heads/', '') if pr.source_ref_name else 'Unknown'
    target_branch = pr.target_ref_name.replace('refs/heads/', '') if pr.target_ref_name else 'Unknown'
    formatted_info.append(f"Source Branch: {source_branch}")
    formatted_info.append(f"Target Branch: {target_branch}")
    
    if pr.created_by and hasattr(pr.created_by, 'display_name'):
        formatted_info.append(f"Creator: {pr.created_by.display_name}")
    
    if pr.creation_date:
        formatted_info.append(f"Creation Date: {pr.creation_date}")
    
    if pr.description:
        description = pr.description
        if len(description) > 100:
            description = description[:97] + "..."
        formatted_info.append(f"Description: {description}")
    
    if pr.url:
        formatted_info.append(f"URL: {pr.url}")
    
    return "\n".join(formatted_info)


def format_commit(commit: GitCommitRef) -> str:
    """
    Format commit information.
    
    Args:
        commit: Commit object to format
    
    Returns:
        String with commit details
    """
    commit_id = commit.commit_id[:8] if commit.commit_id else 'N/A'
    
    formatted_info = [f"Commit ID: {commit_id}"]
    
    if hasattr(commit, 'author') and commit.author:
        if hasattr(commit.author, 'name') and commit.author.name:
            formatted_info.append(f"Author: {commit.author.name}")
        if hasattr(commit.author, 'date') and commit.author.date:
            formatted_info.append(f"Date: {commit.author.date}")
    
    if hasattr(commit, 'comment') and commit.comment:
        comment = commit.comment
        if len(comment) > 100:
            comment = comment[:97] + "..."
        formatted_info.append(f"Comment: {comment}")
    
    return "\n".join(formatted_info)


def format_pull_request_work_item(work_item) -> str:
    """
    Format work item information for pull requests.
    
    Args:
        work_item: Work item object to format
    
    Returns:
        String with work item details
    """
    formatted_info = [f"ID: {work_item.id}" if hasattr(work_item, 'id') else "ID: N/A"]
    
    if hasattr(work_item, 'title') and work_item.title:
        formatted_info.append(f"Title: {work_item.title}")
    
    if hasattr(work_item, 'work_item_type') and work_item.work_item_type:
        formatted_info.append(f"Type: {work_item.work_item_type}")
    
    if hasattr(work_item, 'state') and work_item.state:
        formatted_info.append(f"State: {work_item.state}")
    
    return "\n".join(formatted_info)


def format_policy_evaluation(evaluation) -> str:
    """
    Format policy evaluation information.
    
    Args:
        evaluation: Policy evaluation object to format
    
    Returns:
        String with policy evaluation details
    """
    policy_name = "Unknown Policy"
    if hasattr(evaluation, 'configuration') and evaluation.configuration:
        if hasattr(evaluation.configuration, 'type') and evaluation.configuration.type:
            if hasattr(evaluation.configuration.type, 'display_name'):
                policy_name = evaluation.configuration.type.display_name
    
    formatted_info = [f"Policy: {policy_name}"]
    
    if hasattr(evaluation, 'status') and evaluation.status:
        formatted_info.append(f"Status: {evaluation.status}")
    
    if hasattr(evaluation, 'status') and evaluation.status == 'rejected':
        if hasattr(evaluation, 'context') and evaluation.context:
            if hasattr(evaluation.context, 'error_message') and evaluation.context.error_message:
                formatted_info.append(f"Reason: {evaluation.context.error_message}")
    
    return "\n".join(formatted_info)
