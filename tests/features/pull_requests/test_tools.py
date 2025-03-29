import unittest
from unittest.mock import MagicMock, patch
import pytest

# Import the module to test
from mcp_azure_devops.features.pull_requests.tools import (
    _format_pull_request,
    _create_pull_request_impl, 
    _update_pull_request_impl,
    _list_pull_requests_impl,
    _get_pull_request_impl,
    _add_comment_impl,
    _approve_pull_request_impl,
    _reject_pull_request_impl,
    _complete_pull_request_impl,
)

from mcp_azure_devops.features.pull_requests.common import AzureDevOpsClient, AzureDevOpsClientError


class TestPRFormatting(unittest.TestCase):
    def test_format_pull_request_basic(self):
        """Test formatting with basic PR information."""
        pr = {
            "title": "Test PR",
            "pullRequestId": 123,
            "sourceRefName": "refs/heads/feature/branch",
            "targetRefName": "refs/heads/main",
            "url": "https://dev.azure.com/org/project/_git/repo/pullrequest/123"
        }
        
        result = _format_pull_request(pr)
        
        self.assertIn("Pull Request: Test PR", result)
        self.assertIn("ID: 123", result)
        self.assertIn("Source Branch: feature/branch", result)
        self.assertIn("Target Branch: main", result)
        self.assertIn("URL: https://dev.azure.com/org/project/_git/repo/pullrequest/123", result)
    
    def test_format_pull_request_full(self):
        """Test formatting with all PR details."""
        pr = {
            "title": "Test PR",
            "pullRequestId": 123,
            "status": "active",
            "sourceRefName": "refs/heads/feature/branch",
            "targetRefName": "refs/heads/main",
            "createdBy": {"displayName": "John Doe"},
            "creationDate": "2025-03-28T12:00:00Z",
            "description": "This is a test pull request description",
            "url": "https://dev.azure.com/org/project/_git/repo/pullrequest/123"
        }
        
        result = _format_pull_request(pr)
        
        self.assertIn("Pull Request: Test PR", result)
        self.assertIn("ID: 123", result)
        self.assertIn("Status: active", result)
        self.assertIn("Source Branch: feature/branch", result)
        self.assertIn("Target Branch: main", result)
        self.assertIn("Creation", result)  # Test for creationDate
        self.assertIn("Description: This is a test pull request description", result)
    
    def test_format_pull_request_long_description(self):
        """Test formatting with truncated description."""
        long_description = "x" * 200  # Create a string longer than 100 chars
        pr = {
            "title": "Test PR",
            "pullRequestId": 123,
            "description": long_description,
        }
        
        result = _format_pull_request(pr)
        
        self.assertIn("Description:", result)
        self.assertIn("...", result)
        self.assertTrue(len(result.split("Description: ")[1]) < len(long_description))


class TestCreatePullRequest(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=AzureDevOpsClient)
        
    def test_create_pull_request_success(self):
        """Test successful PR creation."""
        self.client.create_pull_request.return_value = {
            "title": "Test PR",
            "pullRequestId": 123,
            "sourceRefName": "refs/heads/feature/branch",
            "targetRefName": "refs/heads/main"
        }
        
        result = _create_pull_request_impl(
            client=self.client,
            title="Test PR",
            description="Test description",
            source_branch="feature/branch",
            target_branch="main",
            reviewers=["user@example.com"]
        )
        
        self.client.create_pull_request.assert_called_once_with(
            title="Test PR",
            description="Test description",
            source_branch="feature/branch",
            target_branch="main",
            reviewers=["user@example.com"]
        )
        self.assertIn("Pull Request: Test PR", result)
        self.assertIn("ID: 123", result)
    
    def test_create_pull_request_error(self):
        """Test error handling in PR creation."""
        self.client.create_pull_request.side_effect = Exception("API Error")
        
        result = _create_pull_request_impl(
            client=self.client,
            title="Test PR",
            description="Test description",
            source_branch="feature/branch",
            target_branch="main"
        )
        
        self.assertIn("Error creating pull request", result)
        self.assertIn("API Error", result)


class TestUpdatePullRequest(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=AzureDevOpsClient)
        
    def test_update_pull_request_success(self):
        """Test successful PR update."""
        self.client.update_pull_request.return_value = {
            "title": "Updated Title",
            "pullRequestId": 123,
            "description": "Updated description",
            "status": "active"
        }
        
        result = _update_pull_request_impl(
            client=self.client,
            pull_request_id=123,
            title="Updated Title",
            description="Updated description"
        )
        
        self.client.update_pull_request.assert_called_once_with(
            pull_request_id=123,
            update_data={"title": "Updated Title", "description": "Updated description"}
        )
        self.assertIn("Pull Request: Updated Title", result)
        self.assertIn("ID: 123", result)
    
    def test_update_pull_request_no_params(self):
        """Test PR update with no parameters."""
        result = _update_pull_request_impl(
            client=self.client,
            pull_request_id=123
        )
        
        self.assertIn("Error: No update parameters", result)
        self.client.update_pull_request.assert_not_called()
    
    def test_update_pull_request_error(self):
        """Test error handling in PR update."""
        self.client.update_pull_request.side_effect = Exception("API Error")
        
        result = _update_pull_request_impl(
            client=self.client,
            pull_request_id=123,
            title="Updated Title"
        )
        
        self.assertIn("Error updating pull request", result)
        self.assertIn("API Error", result)


class TestListPullRequests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=AzureDevOpsClient)
        
    def test_list_pull_requests_success(self):
        """Test successful PR listing."""
        self.client.get_pull_requests.return_value = [
            {
                "title": "PR 1",
                "pullRequestId": 123,
                "status": "active"
            },
            {
                "title": "PR 2",
                "pullRequestId": 124,
                "status": "completed"
            }
        ]
        
        result = _list_pull_requests_impl(
            client=self.client,
            status="all"
        )
        
        self.client.get_pull_requests.assert_called_once_with(
            status="all",
            creator=None,
            reviewer=None,
            target_branch=None
        )
        self.assertIn("PR 1", result)
        self.assertIn("PR 2", result)
        self.assertIn("ID: 123", result)
        self.assertIn("ID: 124", result)
    
    def test_list_pull_requests_empty(self):
        """Test PR listing with no results."""
        self.client.get_pull_requests.return_value = []
        
        result = _list_pull_requests_impl(
            client=self.client,
            status="all"
        )
        
        self.assertIn("No pull requests found", result)
    
    def test_list_pull_requests_error(self):
        """Test error handling in PR listing."""
        self.client.get_pull_requests.side_effect = Exception("API Error")
        
        result = _list_pull_requests_impl(
            client=self.client,
            status="active"
        )
        
        self.assertIn("Error retrieving pull requests", result)
        self.assertIn("API Error", result)


class TestGetPullRequest(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=AzureDevOpsClient)
        
    def test_get_pull_request_success(self):
        """Test successful PR retrieval."""
        self.client.get_pull_request.return_value = {
            "title": "Test PR",
            "pullRequestId": 123,
            "status": "active"
        }
        
        result = _get_pull_request_impl(
            client=self.client,
            pull_request_id=123
        )
        
        self.client.get_pull_request.assert_called_once_with(
            pull_request_id=123
        )
        self.assertIn("Pull Request: Test PR", result)
        self.assertIn("ID: 123", result)
    
    def test_get_pull_request_error(self):
        """Test error handling in PR retrieval."""
        self.client.get_pull_request.side_effect = Exception("API Error")
        
        result = _get_pull_request_impl(
            client=self.client,
            pull_request_id=123
        )
        
        self.assertIn("Error retrieving pull request", result)
        self.assertIn("API Error", result)


class TestAddComment(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=AzureDevOpsClient)
        
    def test_add_comment_success(self):
        """Test successful comment addition."""
        self.client.add_comment.return_value = {
            "id": 456,
            "comments": [{"id": 789}]
        }
        
        result = _add_comment_impl(
            client=self.client,
            pull_request_id=123,
            content="Test comment"
        )
        
        self.client.add_comment.assert_called_once_with(
            pull_request_id=123,
            content="Test comment"
        )
        self.assertIn("Comment added successfully", result)
        self.assertIn("Thread ID: 456", result)
        self.assertIn("Comment ID: 789", result)
    
    def test_add_comment_error(self):
        """Test error handling in comment addition."""
        self.client.add_comment.side_effect = Exception("API Error")
        
        result = _add_comment_impl(
            client=self.client,
            pull_request_id=123,
            content="Test comment"
        )
        
        self.assertIn("Error adding comment", result)
        self.assertIn("API Error", result)


class TestApprovePullRequest(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=AzureDevOpsClient)
        
    def test_approve_pull_request_success(self):
        """Test successful PR approval."""
        self.client.set_vote.return_value = {
            "displayName": "John Doe"
        }
        
        result = _approve_pull_request_impl(
            client=self.client,
            pull_request_id=123
        )
        
        self.client.set_vote.assert_called_once_with(
            pull_request_id=123,
            vote=10
        )
        self.assertIn("Pull request 123 approved by John Doe", result)
    
    def test_approve_pull_request_error(self):
        """Test error handling in PR approval."""
        self.client.set_vote.side_effect = Exception("API Error")
        
        result = _approve_pull_request_impl(
            client=self.client,
            pull_request_id=123
        )
        
        self.assertIn("Error approving pull request", result)
        self.assertIn("API Error", result)


class TestRejectPullRequest(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=AzureDevOpsClient)
        
    def test_reject_pull_request_success(self):
        """Test successful PR rejection."""
        self.client.set_vote.return_value = {
            "displayName": "John Doe"
        }
        
        result = _reject_pull_request_impl(
            client=self.client,
            pull_request_id=123
        )
        
        self.client.set_vote.assert_called_once_with(
            pull_request_id=123,
            vote=-10
        )
        self.assertIn("Pull request 123 rejected by John Doe", result)
    
    def test_reject_pull_request_error(self):
        """Test error handling in PR rejection."""
        self.client.set_vote.side_effect = Exception("API Error")
        
        result = _reject_pull_request_impl(
            client=self.client,
            pull_request_id=123
        )
        
        self.assertIn("Error rejecting pull request", result)
        self.assertIn("API Error", result)


class TestCompletePullRequest(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=AzureDevOpsClient)
        
    def test_complete_pull_request_success(self):
        """Test successful PR completion."""
        self.client.complete_pull_request.return_value = {
            "closedBy": {"displayName": "John Doe"}
        }
        
        result = _complete_pull_request_impl(
            client=self.client,
            pull_request_id=123,
            merge_strategy="squash",
            delete_source_branch=True
        )
        
        self.client.complete_pull_request.assert_called_once_with(
            pull_request_id=123,
            merge_strategy="squash",
            delete_source_branch=True
        )
        self.assertIn("Pull request 123 completed successfully by John Doe", result)
        self.assertIn("Merge strategy: squash", result)
        self.assertIn("Source branch deleted: True", result)
    
    def test_complete_pull_request_error(self):
        """Test error handling in PR completion."""
        self.client.complete_pull_request.side_effect = Exception("API Error")
        
        result = _complete_pull_request_impl(
            client=self.client,
            pull_request_id=123
        )
        
        self.assertIn("Error completing pull request", result)
        self.assertIn("API Error", result)

if __name__ == '__main__':
    unittest.main()