"""
Common utilities for Azure DevOps pull request features.

This module provides shared functionality used by both tools and resources.
"""
from typing import Dict, List, Optional, Any, Union
import base64
import requests
import json
from urllib.parse import quote
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
    
    def __init__(self, organization: str, project: str, repo: str, personal_access_token: str):
        """
        Initialize the Azure DevOps client.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            repo: Azure DevOps repository name
            personal_access_token: PAT with appropriate permissions
        """
        self.organization = organization
        self.project = project
        self.repo = repo
        self.personal_access_token = personal_access_token
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repo}"
        self.api_version = "api-version=7.1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self._encode_pat(personal_access_token)}"
        }
    
    def _encode_pat(self, pat: str) -> str:
        """
        Encode the Personal Access Token for API authentication.
        
        Args:
            pat: Personal Access Token
            
        Returns:
            Encoded PAT for use in Authorization header
        """
        return base64.b64encode(f":{pat}".encode()).decode()
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response object from requests
            
        Returns:
            JSON response if successful
            
        Raises:
            AzureDevOpsClientError: With appropriate error message on failure
        """
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        
        error_message = f"API request failed with status code {response.status_code}"
        try:
            error_details = response.json()
            if "message" in error_details:
                error_message += f": {error_details['message']}"
        except Exception:
            error_message += f": {response.text}"
        
        raise AzureDevOpsClientError(error_message)
    
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
        url = f"{self.base_url}/pullrequests?{self.api_version}"
        
        # Build the request body as a string
        json_data = {
            "sourceRefName": f"refs/heads/{source_branch}",
            "targetRefName": f"refs/heads/{target_branch}",
            "title": title,
            "description": description
        }
        
        # Add reviewers as a separate step if needed
        if reviewers:
            reviewer_objects = []
            for reviewer in reviewers:
                reviewer_objects.append({"id": str(reviewer)})
            
            json_str = json.dumps(json_data)
            json_dict = json.loads(json_str)
            json_dict["reviewers"] = reviewer_objects
            
            # Send the request with the modified JSON
            response = requests.post(url, headers=self.headers, json=json_dict)
        else:
            # Send the request without reviewers
            response = requests.post(url, headers=self.headers, json=json_data)
        
        return self._handle_response(response)
    
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
        url = f"{self.base_url}/pullrequests/{pull_request_id}?{self.api_version}"
        
        response = requests.patch(url, headers=self.headers, json=update_data)
        return self._handle_response(response)
    
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
        url = f"{self.base_url}/pullrequests?{self.api_version}"
        
        params = []
        if status:
            params.append(f"searchCriteria.status={status}")
        if creator:
            params.append(f"searchCriteria.creatorId={creator}")
        if reviewer:
            params.append(f"searchCriteria.reviewerId={reviewer}")
        if target_branch:
            params.append(f"searchCriteria.targetRefName=refs/heads/{quote(target_branch)}")
        
        if params:
            url += "&" + "&".join(params)
        
        response = requests.get(url, headers=self.headers)
        result = self._handle_response(response)
        return result.get("value", [])
    
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
        url = f"{self.base_url}/pullrequests/{pull_request_id}?{self.api_version}"
        
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)
    
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
        if comment_thread_id:
            # Add to existing thread
            url = f"{self.base_url}/pullrequests/{pull_request_id}/threads/{comment_thread_id}/comments?{self.api_version}"
            data = {
                "content": content
            }
            if parent_comment_id:
                data["parentCommentId"] = str(parent_comment_id)
        else:
            # Create new thread
            url = f"{self.base_url}/pullrequests/{pull_request_id}/threads?{self.api_version}"
            data = {
                "comments": [{
                    "content": content
                }],
                "status": "active"
            }
        
        response = requests.post(url, headers=self.headers, json=data)
        return self._handle_response(response)
    
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
        url = f"{self.base_url}/pullrequests/{pull_request_id}/reviewers/me?{self.api_version}"
        
        data = {
            "vote": vote
        }
        
        response = requests.put(url, headers=self.headers, json=data)
        return self._handle_response(response)
    
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
        url = f"{self.base_url}/pullrequests/{pull_request_id}?{self.api_version}"
        
        data = {
            "status": "completed",
            "completionOptions": {
                "mergeStrategy": merge_strategy,
                "deleteSourceBranch": delete_source_branch
            }
        }
        
        response = requests.patch(url, headers=self.headers, json=data)
        return self._handle_response(response)