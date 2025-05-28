import pytest
from unittest.mock import MagicMock, patch

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


class TestPRFormatting:
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
        
        assert "Pull Request: Test PR" in result
        assert "ID: 123" in result
        assert "Source Branch: feature/branch" in result
        assert "Target Branch: main" in result
        assert "URL: https://dev.azure.com/org/project/_git/repo/pullrequest/123" in result
    
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
        
        assert "Pull Request: Test PR" in result
        assert "ID: 123" in result
        assert "Status: active" in result
        assert "Source Branch: feature/branch" in result
        assert "Target Branch: main" in result
        assert "Creation" in result  # Test for creationDate
        assert "Description: This is a test pull request description" in result
    
    def test_format_pull_request_long_description(self):
        """Test formatting with truncated description."""
        long_description = "x" * 200  # Create a string longer than 100 chars
        pr = {
            "title": "Test PR",
            "pullRequestId": 123,
            "description": long_description,
        }
        
        result = _format_pull_request(pr)
        
        assert "Description:" in result
        assert "..." in result
        assert len(result.split("Description: ")[1]) < len(long_description)


class TestCreatePullRequest:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=AzureDevOpsClient)
        
    def test_create_pull_request_success(self, client):
        """Test successful PR creation."""
        client.create_pull_request.return_value = {
            "title": "Test PR",
            "pullRequestId": 123,
            "sourceRefName": "refs/heads/feature/branch",
            "targetRefName": "refs/heads/main"
        }
        
        result = _create_pull_request_impl(
            client=client,
            title="Test PR",
            description="Test description",
            source_branch="feature/branch",
            target_branch="main",
            reviewers=["user@example.com"]
        )
        
        client.create_pull_request.assert_called_once_with(
            title="Test PR",
            description="Test description",
            source_branch="feature/branch",
            target_branch="main",
            reviewers=["user@example.com"]
        )
        assert "Pull Request: Test PR" in result
        assert "ID: 123" in result
    
    def test_create_pull_request_error(self, client):
        """Test error handling in PR creation."""
        client.create_pull_request.side_effect = Exception("API Error")
        
        result = _create_pull_request_impl(
            client=client,
            title="Test PR",
            description="Test description",
            source_branch="feature/branch",
            target_branch="main"
        )
        
        assert "Error creating pull request" in result
        assert "API Error" in result


class TestUpdatePullRequest:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=AzureDevOpsClient)
        
    def test_update_pull_request_success(self, client):
        """Test successful PR update."""
        client.update_pull_request.return_value = {
            "title": "Updated Title",
            "pullRequestId": 123,
            "description": "Updated description",
            "status": "active"
        }
        
        result = _update_pull_request_impl(
            client=client,
            pull_request_id=123,
            title="Updated Title",
            description="Updated description"
        )
        
        client.update_pull_request.assert_called_once_with(
            pull_request_id=123,
            update_data={"title": "Updated Title", "description": "Updated description"}
        )
        assert "Pull Request: Updated Title" in result
        assert "ID: 123" in result
    
    def test_update_pull_request_no_params(self, client):
        """Test PR update with no parameters."""
        result = _update_pull_request_impl(
            client=client,
            pull_request_id=123
        )
        
        assert "Error: No update parameters" in result
        client.update_pull_request.assert_not_called()
    
    def test_update_pull_request_error(self, client):
        """Test error handling in PR update."""
        client.update_pull_request.side_effect = Exception("API Error")
        
        result = _update_pull_request_impl(
            client=client,
            pull_request_id=123,
            title="Updated Title"
        )
        
        assert "Error updating pull request" in result
        assert "API Error" in result


class TestListPullRequests:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=AzureDevOpsClient)
        
    def test_list_pull_requests_success(self, client):
        """Test successful PR listing."""
        client.get_pull_requests.return_value = [
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
            client=client,
            status="all"
        )
        
        client.get_pull_requests.assert_called_once_with(
            status="all",
            creator=None,
            reviewer=None,
            target_branch=None
        )
        assert "PR 1" in result
        assert "PR 2" in result
        assert "ID: 123" in result
        assert "ID: 124" in result
    
    def test_list_pull_requests_empty(self, client):
        """Test PR listing with no results."""
        client.get_pull_requests.return_value = []
        
        result = _list_pull_requests_impl(
            client=client,
            status="all"
        )
        
        assert "No pull requests found" in result
    
    def test_list_pull_requests_error(self, client):
        """Test error handling in PR listing."""
        client.get_pull_requests.side_effect = Exception("API Error")
        
        result = _list_pull_requests_impl(
            client=client,
            status="active"
        )
        
        assert "Error retrieving pull requests" in result
        assert "API Error" in result


class TestGetPullRequest:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=AzureDevOpsClient)
        
    def test_get_pull_request_success(self, client):
        """Test successful PR retrieval."""
        client.get_pull_request.return_value = {
            "title": "Test PR",
            "pullRequestId": 123,
            "status": "active"
        }
        
        result = _get_pull_request_impl(
            client=client,
            pull_request_id=123
        )
        
        client.get_pull_request.assert_called_once_with(
            pull_request_id=123
        )
        assert "Pull Request: Test PR" in result
        assert "ID: 123" in result
    
    def test_get_pull_request_error(self, client):
        """Test error handling in PR retrieval."""
        client.get_pull_request.side_effect = Exception("API Error")
        
        result = _get_pull_request_impl(
            client=client,
            pull_request_id=123
        )
        
        assert "Error retrieving pull request" in result
        assert "API Error" in result


class TestAddComment:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=AzureDevOpsClient)
        
    def test_add_comment_success(self, client):
        """Test successful comment addition."""
        client.add_comment.return_value = {
            "id": 456,
            "comments": [{"id": 789}]
        }
        
        result = _add_comment_impl(
            client=client,
            pull_request_id=123,
            content="Test comment"
        )
        
        client.add_comment.assert_called_once_with(
            pull_request_id=123,
            content="Test comment"
        )
        assert "Comment added successfully" in result
        assert "Thread ID: 456" in result
        assert "Comment ID: 789" in result
    
    def test_add_comment_error(self, client):
        """Test error handling in comment addition."""
        client.add_comment.side_effect = Exception("API Error")
        
        result = _add_comment_impl(
            client=client,
            pull_request_id=123,
            content="Test comment"
        )
        
        assert "Error adding comment" in result
        assert "API Error" in result


class TestApprovePullRequest:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=AzureDevOpsClient)
        
    def test_approve_pull_request_success(self, client):
        """Test successful PR approval."""
        client.set_vote.return_value = {
            "displayName": "John Doe"
        }
        
        result = _approve_pull_request_impl(
            client=client,
            pull_request_id=123
        )
        
        client.set_vote.assert_called_once_with(
            pull_request_id=123,
            vote=10
        )
        assert "Pull request 123 approved by John Doe" in result
    
    def test_approve_pull_request_error(self, client):
        """Test error handling in PR approval."""
        client.set_vote.side_effect = Exception("API Error")
        
        result = _approve_pull_request_impl(
            client=client,
            pull_request_id=123
        )
        
        assert "Error approving pull request" in result
        assert "API Error" in result


class TestRejectPullRequest:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=AzureDevOpsClient)
        
    def test_reject_pull_request_success(self, client):
        """Test successful PR rejection."""
        client.set_vote.return_value = {
            "displayName": "John Doe"
        }
        
        result = _reject_pull_request_impl(
            client=client,
            pull_request_id=123
        )
        
        client.set_vote.assert_called_once_with(
            pull_request_id=123,
            vote=-10
        )
        assert "Pull request 123 rejected by John Doe" in result
    
    def test_reject_pull_request_error(self, client):
        """Test error handling in PR rejection."""
        client.set_vote.side_effect = Exception("API Error")
        
        result = _reject_pull_request_impl(
            client=client,
            pull_request_id=123
        )
        
        assert "Error rejecting pull request" in result
        assert "API Error" in result


class TestCompletePullRequest:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=AzureDevOpsClient)
        
    def test_complete_pull_request_success(self, client):
        """Test successful PR completion."""
        client.complete_pull_request.return_value = {
            "closedBy": {"displayName": "John Doe"}
        }
        
        result = _complete_pull_request_impl(
            client=client,
            pull_request_id=123,
            merge_strategy="squash",
            delete_source_branch=True
        )
        
        client.complete_pull_request.assert_called_once_with(
            pull_request_id=123,
            merge_strategy="squash",
            delete_source_branch=True
        )
        assert "Pull request 123 completed successfully by John Doe" in result
        assert "Merge strategy: squash" in result
        assert "Source branch deleted: True" in result
    
    def test_complete_pull_request_error(self, client):
        """Test error handling in PR completion."""
        client.complete_pull_request.side_effect = Exception("API Error")
        
        result = _complete_pull_request_impl(
            client=client,
            pull_request_id=123
        )
        
        assert "Error completing pull request" in result
        assert "API Error" in result