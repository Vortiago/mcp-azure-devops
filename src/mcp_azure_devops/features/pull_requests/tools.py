"""
Pull request tools for Azure DevOps.

This module provides MCP tools for working with Azure DevOps pull requests.
"""
from typing import Dict, List, Optional, Any
from mcp_azure_devops.features.pull_requests.common import AzureDevOpsClient, AzureDevOpsClientError


def _format_pull_request(pr: Dict[str, Any]) -> str:
    """
    Format pull request information.
    
    Args:
        pr: Pull request object to format
    
    Returns:
        String with pull request details
    """
    formatted_info = [f"# Pull Request: {pr.get('title')}"]
    formatted_info.append(f"ID: {pr.get('pullRequestId')}")
    
    if pr.get('status'):
        formatted_info.append(f"Status: {pr.get('status')}")
    
    source_branch = pr.get('sourceRefName', '').replace('refs/heads/', '')
    target_branch = pr.get('targetRefName', '').replace('refs/heads/', '')
    formatted_info.append(f"Source Branch: {source_branch}")
    formatted_info.append(f"Target Branch: {target_branch}")
    
    created_by = pr.get('createdBy')
    if created_by is not None and 'displayName' in created_by:
        formatted_info.append(f"Creator: {created_by.get('displayName')}")
    
    if pr.get('creationDate'):
        formatted_info.append(f"Creation Date: {pr.get('creationDate')}")
    
    description = pr.get('description')
    if description is not None:
        if len(description) > 100:
            description = description[:97] + "..."
        formatted_info.append(f"Description: {description}")
    
    if pr.get('url'):
        formatted_info.append(f"URL: {pr.get('url')}")
    
    return "\n".join(formatted_info)


def _create_pull_request_impl(
    client: AzureDevOpsClient,
    title: str,
    description: str,
    source_branch: str,
    target_branch: str,
    reviewers: Optional[List[str]] = None
) -> str:
    """
    Implementation of pull request creation.
    
    Args:
        client: Azure DevOps client
        title: PR title
        description: PR description
        source_branch: Source branch name
        target_branch: Target branch name
        reviewers: List of reviewer emails or IDs
    
    Returns:
        Formatted string containing pull request information
    """
    try:
        result = client.create_pull_request(
            title=title,
            description=description,
            source_branch=source_branch,
            target_branch=target_branch,
            reviewers=reviewers
        )
        
        return _format_pull_request(result)
    except Exception as e:
        return f"Error creating pull request: {str(e)}"


def _update_pull_request_impl(
    client: AzureDevOpsClient,
    pull_request_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    Implementation of pull request update.
    
    Args:
        client: Azure DevOps client
        pull_request_id: ID of the PR to update
        title: New PR title (optional)
        description: New PR description (optional)
        status: New PR status (optional)
    
    Returns:
        Formatted string containing updated pull request information
    """
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if status is not None:
        update_data["status"] = status
    
    if not update_data:
        return "Error: No update parameters provided"
    
    try:
        result = client.update_pull_request(
            pull_request_id=pull_request_id,
            update_data=update_data
        )
        
        return _format_pull_request(result)
    except Exception as e:
        return f"Error updating pull request: {str(e)}"


def _list_pull_requests_impl(
    client: AzureDevOpsClient,
    status: Optional[str] = None,
    creator: Optional[str] = None,
    reviewer: Optional[str] = None,
    target_branch: Optional[str] = None
) -> str:
    """
    Implementation of pull requests listing.
    
    Args:
        client: Azure DevOps client
        status: Filter by status (active, abandoned, completed, all)
        creator: Filter by creator ID
        reviewer: Filter by reviewer ID
        target_branch: Filter by target branch name
    
    Returns:
        Formatted string containing pull request information
    """
    try:
        prs = client.get_pull_requests(
            status=status,
            creator=creator,
            reviewer=reviewer,
            target_branch=target_branch
        )
        
        if not prs:
            return "No pull requests found."
        
        formatted_prs = []
        for pr in prs:
            formatted_prs.append(_format_pull_request(pr))
        
        return "\n\n".join(formatted_prs)
    except Exception as e:
        return f"Error retrieving pull requests: {str(e)}"


def _get_pull_request_impl(
    client: AzureDevOpsClient,
    pull_request_id: int
) -> str:
    """
    Implementation of pull request retrieval.
    
    Args:
        client: Azure DevOps client
        pull_request_id: ID of the PR
    
    Returns:
        Formatted string containing pull request information
    """
    try:
        pr = client.get_pull_request(pull_request_id=pull_request_id)
        return _format_pull_request(pr)
    except Exception as e:
        return f"Error retrieving pull request: {str(e)}"


def _add_comment_impl(
    client: AzureDevOpsClient,
    pull_request_id: int,
    content: str
) -> str:
    """
    Implementation of comment addition.
    
    Args:
        client: Azure DevOps client
        pull_request_id: ID of the PR
        content: Comment text
    
    Returns:
        Formatted string containing comment information
    """
    try:
        result = client.add_comment(
            pull_request_id=pull_request_id,
            content=content
        )
        
        # Handle both dict and object types
        if isinstance(result, dict):
            thread_id = result.get("id")
            comments = result.get("comments", [])
        else:
            thread_id = getattr(result, 'id', None)
            comments = getattr(result, 'comments', [])
        
        # Get the first comment's ID
        comment_id = None
        if comments and len(comments) > 0:
            first_comment = comments[0]
            if isinstance(first_comment, dict):
                comment_id = first_comment.get("id")
            else:
                comment_id = getattr(first_comment, 'id', None)
        
        return f"Comment added successfully:\nThread ID: {thread_id}\nComment ID: {comment_id}\nContent: {content}"
    except Exception as e:
        return f"Error adding comment: {str(e)}"


def _approve_pull_request_impl(
    client: AzureDevOpsClient,
    pull_request_id: int
) -> str:
    """
    Implementation of pull request approval.
    
    Args:
        client: Azure DevOps client
        pull_request_id: ID of the PR
    
    Returns:
        Formatted string containing approval information
    """
    try:
        result = client.set_vote(
            pull_request_id=pull_request_id,
            vote=10  # 10 = Approve
        )
        
        return f"Pull request {pull_request_id} approved by {result.get('displayName', 'user')}"
    except Exception as e:
        return f"Error approving pull request: {str(e)}"


def _reject_pull_request_impl(
    client: AzureDevOpsClient,
    pull_request_id: int
) -> str:
    """
    Implementation of pull request rejection.
    
    Args:
        client: Azure DevOps client
        pull_request_id: ID of the PR
    
    Returns:
        Formatted string containing rejection information
    """
    try:
        result = client.set_vote(
            pull_request_id=pull_request_id,
            vote=-10  # -10 = Reject
        )
        
        return f"Pull request {pull_request_id} rejected by {result.get('displayName', 'user')}"
    except Exception as e:
        return f"Error rejecting pull request: {str(e)}"


def _complete_pull_request_impl(
    client: AzureDevOpsClient,
    pull_request_id: int,
    merge_strategy: str = "squash",
    delete_source_branch: bool = False
) -> str:
    """
    Implementation of pull request completion.
    
    Args:
        client: Azure DevOps client
        pull_request_id: ID of the PR
        merge_strategy: Strategy to use (squash, rebase, rebaseMerge, merge)
        delete_source_branch: Whether to delete source branch after merge
    
    Returns:
        Formatted string containing completion information
    """
    try:
        result = client.complete_pull_request(
            pull_request_id=pull_request_id,
            merge_strategy=merge_strategy,
            delete_source_branch=delete_source_branch
        )
        
        completed_by = result.get("closedBy", {}).get("displayName", "user")
        return f"Pull request {pull_request_id} completed successfully by {completed_by}\nMerge strategy: {merge_strategy}\nSource branch deleted: {delete_source_branch}"
    except Exception as e:
        return f"Error completing pull request: {str(e)}"
    
def _get_pull_request_work_items_impl(client: AzureDevOpsClient, pull_request_id: int) -> str:
    """Implementation for getting work items linked to a PR."""
    work_items = client.get_pull_request_work_items(pull_request_id=pull_request_id)
    
    if not work_items:
        return "No work items are linked to this pull request."
    
    result = f"Work Items linked to PR #{pull_request_id}:\n\n"
    for i, item in enumerate(work_items, 1):
        result += f"{i}. ID: {item.get('id', 'N/A')}\n"
        result += f"   Title: {item.get('title', 'N/A')}\n"
        result += f"   Type: {item.get('work_item_type', 'N/A')}\n"
        result += f"   State: {item.get('state', 'N/A')}\n\n"
    
    return result

def _add_work_items_to_pull_request_impl(
    client: AzureDevOpsClient, 
    pull_request_id: int,
    work_item_ids: List[int]
) -> str:
    """Implementation for linking work items to a PR."""
    result = client.add_work_items_to_pull_request(
        pull_request_id=pull_request_id,
        work_item_ids=work_item_ids
    )
    
    if result:
        work_items_str = ", ".join([str(id) for id in work_item_ids])
        return f"Successfully linked work item(s) #{work_items_str} to pull request #{pull_request_id}."
    else:
        return f"Failed to link work items to pull request #{pull_request_id}."

def _get_pull_request_commits_impl(client: AzureDevOpsClient, pull_request_id: int) -> str:
    """Implementation for getting commits in a PR."""
    try:
        commits = client.get_pull_request_commits(pull_request_id=pull_request_id)
        
        if not commits:
            return f"No commits found in pull request #{pull_request_id}."
        
        result = f"Commits in PR #{pull_request_id}:\n\n"
        for i, commit in enumerate(commits, 1):
            # Handle commit ID
            commit_id = commit.get('commitId', commit.get('commit_id', 'N/A'))
            
            # Handle author information with safer access
            author = commit.get('author', {})
            author_name = 'N/A'
            author_date = 'N/A'
            
            if isinstance(author, dict):
                author_name = author.get('name', 'N/A')
                # Safely get date and don't try to format it
                author_date = author.get('date', 'N/A')
            
            # Handle comment/message
            comment = commit.get('comment', commit.get('commentTruncated', 
                      commit.get('message', 'N/A')))
            
            # Format output
            result += f"{i}. Commit ID: {commit_id[:8] if commit_id != 'N/A' else 'N/A'}\n"
            result += f"   Author: {author_name}\n"
            result += f"   Date: {author_date}\n"
            result += f"   Comment: {comment[:100]}"
            if comment != 'N/A' and len(comment) > 100:
                result += "..."
            result += "\n\n"
        
        return result
    except Exception as e:
        # Add more detailed error info
        import traceback
        return f"Error processing commits for PR #{pull_request_id}: {str(e)}\n{traceback.format_exc()}"

def _get_pull_request_changes_impl(client: AzureDevOpsClient, pull_request_id: int) -> str:
    """Implementation for getting changes in a PR."""
    changes = client.get_pull_request_changes(pull_request_id=pull_request_id)
    
    if not changes or not changes.get('changes'):
        return f"No file changes found in pull request #{pull_request_id}."
    
    result = f"File changes in PR #{pull_request_id}:\n\n"
    
    for i, change in enumerate(changes.get('changes', []), 1):
        change_type = change.get('change_type', 'N/A')
        item = change.get('item', {})
        path = item.get('path', 'N/A')
        
        result += f"{i}. {path}\n"
        result += f"   Change type: {change_type}\n"
        
        if change_type == 'edit':
            result += f"   Additions: {change.get('line_count_additions', 0)}\n"
            result += f"   Deletions: {change.get('line_count_deletions', 0)}\n"
        
        result += "\n"
    
    # Add summary
    additions = sum(change.get('line_count_additions', 0) for change in changes.get('changes', []))
    deletions = sum(change.get('line_count_deletions', 0) for change in changes.get('changes', []))
    files_changed = len(changes.get('changes', []))
    
    result += f"Summary: {files_changed} files changed, {additions} additions, {deletions} deletions."
    
    return result

def _get_pull_request_thread_comments_impl(
    client: AzureDevOpsClient, 
    pull_request_id: int,
    thread_id: int
) -> str:
    """Implementation for getting comments in a PR thread."""
    comments = client.get_pull_request_thread_comments(
        pull_request_id=pull_request_id,
        thread_id=thread_id
    )
    
    if not comments:
        return f"No comments found in thread #{thread_id} of pull request #{pull_request_id}."
    
    result = f"Comments in thread #{thread_id} of PR #{pull_request_id}:\n\n"
    
    for i, comment in enumerate(comments, 1):
        author = comment.get('author', {}).get('display_name', 'Unknown')
        content = comment.get('content', 'N/A')
        date = comment.get('published_date', 'N/A')
        
        result += f"{i}. Author: {author}\n"
        result += f"   Date: {date}\n"
        result += f"   Content: {content}\n\n"
    
    return result

def _abandon_pull_request_impl(client: AzureDevOpsClient, pull_request_id: int) -> str:
    """Implementation for abandoning a PR."""
    result = client.abandon_pull_request(pull_request_id=pull_request_id)
    
    if result and result.get('status') == 'abandoned':
        return f"Successfully abandoned pull request #{pull_request_id}."
    else:
        return f"Failed to abandon pull request #{pull_request_id}."

def _reactivate_pull_request_impl(client: AzureDevOpsClient, pull_request_id: int) -> str:
    """Implementation for reactivating a PR."""
    result = client.reactivate_pull_request(pull_request_id=pull_request_id)
    
    if result and result.get('status') == 'active':
        return f"Successfully reactivated pull request #{pull_request_id}."
    else:
        return f"Failed to reactivate pull request #{pull_request_id}."

def _get_pull_request_policy_evaluations_impl(client: AzureDevOpsClient, pull_request_id: int) -> str:
    """Implementation for getting policy evaluations for a PR."""
    evaluations = client.get_pull_request_policy_evaluations(pull_request_id=pull_request_id)
    
    if not evaluations:
        return f"No policy evaluations found for pull request #{pull_request_id}."
    
    result = f"Policy evaluations for PR #{pull_request_id}:\n\n"
    
    for i, eval in enumerate(evaluations, 1):
        policy_type = eval.get('configuration', {}).get('type', {}).get('display_name', 'Unknown Policy')
        status = eval.get('status', 'Unknown')
        
        result += f"{i}. Policy: {policy_type}\n"
        result += f"   Status: {status}\n"
        
        if status == 'rejected':
            result += f"   Reason: {eval.get('context', {}).get('error_message', 'N/A')}\n"
        
        result += "\n"
    
    # Add summary
    approved = sum(1 for eval in evaluations if eval.get('status') == 'approved')
    rejected = sum(1 for eval in evaluations if eval.get('status') == 'rejected')
    pending = sum(1 for eval in evaluations if eval.get('status') == 'queued' or eval.get('status') == 'running')
    
    result += f"Summary: {approved} approved, {rejected} rejected, {pending} pending."
    
    return result                


def register_tools(mcp) -> None:
    """
    Register pull request tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def create_pull_request(
        organization: str,
        project: str,
        repo: str,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
        reviewers: Optional[List[str]] = None
    ) -> str:
        """
        Create a new Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            title: PR title
            description: PR description
            source_branch: Source branch name
            target_branch: Target branch name
            reviewers: List of reviewer emails or IDs (optional)
        
        Returns:
            Formatted string containing pull request information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _create_pull_request_impl(
                client=client,
                title=title,
                description=description,
                source_branch=source_branch,
                target_branch=target_branch,
                reviewers=reviewers
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def update_pull_request(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Update an existing Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR to update
            title: New PR title (optional)
            description: New PR description (optional)
            status: New PR status (active, abandoned) (optional)
        
        Returns:
            Formatted string containing updated pull request information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _update_pull_request_impl(
                client=client,
                pull_request_id=pull_request_id,
                title=title,
                description=description,
                status=status
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def list_pull_requests(
        organization: str,
        project: str,
        repo: str,
        status: Optional[str] = None,
        creator: Optional[str] = None,
        reviewer: Optional[str] = None,
        target_branch: Optional[str] = None
    ) -> str:
        """
        List Pull Requests in Azure DevOps with optional filtering.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            status: Filter by status (active, abandoned, completed, all) (optional)
            creator: Filter by creator ID (optional)
            reviewer: Filter by reviewer ID (optional)
            target_branch: Filter by target branch name (optional)
        
        Returns:
            Formatted string containing pull request information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _list_pull_requests_impl(
                client=client,
                status=status,
                creator=creator,
                reviewer=reviewer,
                target_branch=target_branch
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_pull_request(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int
    ) -> str:
        """
        Get details of a specific Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing pull request information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _get_pull_request_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def add_comment(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int,
        content: str
    ) -> str:
        """
        Add a comment to a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
            content: Comment text
        
        Returns:
            Formatted string containing comment information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _add_comment_impl(
                client=client,
                pull_request_id=pull_request_id,
                content=content
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def approve_pull_request(
        organization: str,
        project: str,
        repo: str,        
        pull_request_id: int
    ) -> str:
        """
        Approve a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing approval information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _approve_pull_request_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def reject_pull_request(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int
    ) -> str:
        """
        Reject a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing rejection information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo,
            )
            return _reject_pull_request_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def complete_pull_request(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int,
        merge_strategy: str = "squash",
        delete_source_branch: bool = False
    ) -> str:
        """
        Complete (merge) a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
            merge_strategy: Merge strategy (squash, rebase, rebaseMerge, merge) (optional)
            delete_source_branch: Whether to delete source branch after merge (optional)
        
        Returns:
            Formatted string containing completion information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _complete_pull_request_impl(
                client=client,
                pull_request_id=pull_request_id,
                merge_strategy=merge_strategy,
                delete_source_branch=delete_source_branch
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        
    @mcp.tool()
    def get_pull_request_work_items(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int
    ) -> str:
        """
        Get work items linked to a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name            
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing linked work items information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _get_pull_request_work_items_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        
    @mcp.tool()
    def add_work_items_to_pull_request(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int,
        work_item_ids: str
    ) -> str:
        """
        Link work items to a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
            work_item_ids: Comma-separated list of work item IDs to link
        
        Returns:
            Formatted string indicating success or failure
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            
            # Parse the comma-separated list of work item IDs
            work_item_id_list = [int(id.strip()) for id in work_item_ids.split(",")]
            
            return _add_work_items_to_pull_request_impl(
                client=client,
                pull_request_id=pull_request_id,
                work_item_ids=work_item_id_list
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except ValueError:
            return "Error: Work item IDs must be valid integers separated by commas."
        
    @mcp.tool()
    def get_pull_request_commits(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int
    ) -> str:
        """
        Get all commits in a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing commit information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _get_pull_request_commits_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        
    @mcp.tool()
    def get_pull_request_changes(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int
    ) -> str:
        """
        Get all file changes in a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing file change information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _get_pull_request_changes_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        
    @mcp.tool()
    def get_pull_request_thread_comments(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int,
        thread_id: int
    ) -> str:
        """
        Get all comments in a Pull Request thread in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
            thread_id: ID of the comment thread
        
        Returns:
            Formatted string containing comment information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _get_pull_request_thread_comments_impl(
                client=client,
                pull_request_id=pull_request_id,
                thread_id=thread_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        
    @mcp.tool()
    def abandon_pull_request(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int
    ) -> str:
        """
        Abandon a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string indicating success or failure
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _abandon_pull_request_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        
    @mcp.tool()
    def reactivate_pull_request(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int
    ) -> str:
        """
        Reactivate an abandoned Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string indicating success or failure
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _reactivate_pull_request_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        
    @mcp.tool()
    def get_pull_request_policy_evaluations(
        organization: str,
        project: str,
        repo: str,
        pull_request_id: int
    ) -> str:
        """
        Get policy evaluations for a Pull Request in Azure DevOps.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            pull_request_id: ID of the PR
        
        Returns:
            Formatted string containing policy evaluation information
        """
        try:
            client = AzureDevOpsClient(
                organization=organization,
                project=project,
                repo=repo
            )
            return _get_pull_request_policy_evaluations_impl(
                client=client,
                pull_request_id=pull_request_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"