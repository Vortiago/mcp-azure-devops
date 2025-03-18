import pytest
from unittest.mock import MagicMock
from azure.devops.v7_1.work_item_tracking.models import WorkItem, WorkItemReference, Wiql
from mcp_azure_devops.features.work_items.tools import _query_work_items_impl

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
