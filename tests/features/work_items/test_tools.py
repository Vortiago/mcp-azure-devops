from unittest.mock import MagicMock

from azure.devops.v7_1.work_item_tracking.models import (
    WorkItem,
    WorkItemReference,
)

from mcp_azure_devops.features.work_items.tools.comments import (
    _get_work_item_comments_impl,
)
from mcp_azure_devops.features.work_items.tools.query import (
    _query_work_items_impl,
)
from mcp_azure_devops.features.work_items.tools.read import _get_work_item_impl


# Tests for _query_work_items_impl
def test_query_work_items_impl_no_results():
    """Test query with no results."""
    mock_client = MagicMock()
    mock_query_result = MagicMock()
    mock_query_result.work_items = []
    mock_client.query_by_wiql.return_value = mock_query_result
    
    result = _query_work_items_impl("SELECT * FROM WorkItems", 10, mock_client)
    assert result == "No work items found matching the query."

def test_query_work_items_impl_with_results():
    """Test query with results."""
    mock_client = MagicMock()
    
    # Mock query result
    mock_query_result = MagicMock()
    mock_work_item_ref1 = MagicMock(spec=WorkItemReference)
    mock_work_item_ref1.id = "123"
    mock_work_item_ref2 = MagicMock(spec=WorkItemReference)
    mock_work_item_ref2.id = "456"
    mock_query_result.work_items = [mock_work_item_ref1, mock_work_item_ref2]
    mock_client.query_by_wiql.return_value = mock_query_result
    
    # Mock work items
    mock_work_item1 = MagicMock(spec=WorkItem)
    mock_work_item1.id = 123
    mock_work_item1.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Test Bug",
        "System.State": "Active"
    }
    
    mock_work_item2 = MagicMock(spec=WorkItem)
    mock_work_item2.id = 456
    mock_work_item2.fields = {
        "System.WorkItemType": "Task",
        "System.Title": "Test Task",
        "System.State": "Closed"
    }
    
    mock_client.get_work_items.return_value = [mock_work_item1, mock_work_item2]
    
    result = _query_work_items_impl("SELECT * FROM WorkItems", 10, mock_client)
    
    # Check that the result contains the expected basic info formatting
    assert "# Work Item 123: Test Bug" in result
    assert "Type: Bug" in result
    assert "State: Active" in result
    assert "# Work Item 456: Test Task" in result
    assert "Type: Task" in result
    assert "State: Closed" in result


# Tests for _get_work_item_impl
def test_get_work_item_impl_basic():
    """Test retrieving basic work item info."""
    mock_client = MagicMock()
    
    # Mock work item
    mock_work_item = MagicMock(spec=WorkItem)
    mock_work_item.id = 123
    mock_work_item.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Test Bug",
        "System.State": "Active",
        "System.TeamProject": "Test Project"
    }
    mock_client.get_work_item.return_value = mock_work_item
    
    result = _get_work_item_impl(123, mock_client)
    
    # Check that the result contains expected basic info
    assert "# Work Item 123: Test Bug" in result
    assert "Type: Bug" in result
    assert "State: Active" in result
    assert "Project: Test Project" in result

def test_get_work_item_impl_detailed():
    """Test retrieving detailed work item info."""
    mock_client = MagicMock()
    
    # Mock work item with more fields for detailed view
    mock_work_item = MagicMock(spec=WorkItem)
    mock_work_item.id = 123
    mock_work_item.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Test Bug",
        "System.State": "Active",
        "System.TeamProject": "Test Project",
        "System.Description": "This is a description",
        "System.AssignedTo": {"displayName": "Test User", "uniqueName": "test@example.com"},
        "System.CreatedBy": {"displayName": "Creator User"},
        "System.CreatedDate": "2023-01-01",
        "System.IterationPath": "Project\\Sprint 1",
        "System.AreaPath": "Project\\Area",
        "System.Tags": "tag1; tag2",
    }
    mock_client.get_work_item.return_value = mock_work_item
    
    result = _get_work_item_impl(123, mock_client)
    
    # Check that the result contains both basic and detailed info
    assert "# Work Item 123: Test Bug" in result
    assert "Type: Bug" in result
    assert "Description" in result
    assert "This is a description" in result
    assert "Assigned To: Test User (test@example.com)" in result
    assert "Created By: Creator User" in result
    assert "Iteration: Project\\Sprint 1" in result

def test_get_work_item_impl_error():
    """Test error handling in get_work_item_impl."""
    mock_client = MagicMock()
    mock_client.get_work_item.side_effect = Exception("Test error")
    
    result = _get_work_item_impl(123, mock_client)
    
    assert "Error retrieving work item 123: Test error" in result

# Tests for _get_work_item_comments_impl
def test_get_work_item_comments_impl():
    """Test retrieving work item comments."""
    mock_client = MagicMock()
    
    # Mock work item for project lookup
    mock_work_item = MagicMock(spec=WorkItem)
    mock_work_item.fields = {"System.TeamProject": "Test Project"}
    mock_client.get_work_item.return_value = mock_work_item
    
    # Mock comments
    mock_comment1 = MagicMock()
    mock_comment1.text = "This is comment 1"
    mock_created_by = MagicMock()
    mock_created_by.display_name = "Comment User"
    mock_comment1.created_by = mock_created_by
    mock_comment1.created_date = "2023-01-02"
    
    mock_comments = MagicMock()
    mock_comments.comments = [mock_comment1]
    mock_client.get_comments.return_value = mock_comments
    
    result = _get_work_item_comments_impl(123, mock_client)
    
    assert "## Comment by Comment User on 2023-01-02" in result
    assert "This is comment 1" in result

def test_get_work_item_comments_impl_no_comments():
    """Test retrieving work item with no comments."""
    mock_client = MagicMock()
    
    # Mock work item for project lookup
    mock_work_item = MagicMock(spec=WorkItem)
    mock_work_item.fields = {"System.TeamProject": "Test Project"}
    mock_client.get_work_item.return_value = mock_work_item
    
    # Mock empty comments
    mock_comments = MagicMock()
    mock_comments.comments = []
    mock_client.get_comments.return_value = mock_comments
    
    result = _get_work_item_comments_impl(123, mock_client)
    
    assert "No comments found for this work item." in result
