import pytest
from unittest.mock import MagicMock
from azure.devops.v7_1.work_item_tracking.models import WorkItem, WorkItemReference, Wiql
from mcp_azure_devops.features.work_items.tools import format_work_items, _query_work_items_impl

# Tests for format_work_items
def test_format_work_items_empty_list():
    """Test formatting with empty list returns empty string."""
    assert format_work_items([]) == ""

def test_format_work_items_with_none():
    """Test formatting with None items is handled properly."""
    # Create a proper mock with None fields instead of passing None directly
    none_item = MagicMock(spec=WorkItem)
    none_item.fields = None
    assert format_work_items([none_item]) == ""
    
    work_item = MagicMock(spec=WorkItem)
    work_item.id = 123
    work_item.fields = None
    assert format_work_items([work_item]) == ""

def test_format_work_items_single_item():
    """Test formatting a single work item."""
    work_item = MagicMock(spec=WorkItem)
    work_item.id = 123
    work_item.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Test Bug",
        "System.State": "Active"
    }
    
    expected = "Bug 123: Test Bug (Active)"
    assert format_work_items([work_item]) == expected

def test_format_work_items_multiple_items():
    """Test formatting multiple work items."""
    work_item1 = MagicMock(spec=WorkItem)
    work_item1.id = 123
    work_item1.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Test Bug",
        "System.State": "Active"
    }
    
    work_item2 = MagicMock(spec=WorkItem)
    work_item2.id = 456
    work_item2.fields = {
        "System.WorkItemType": "Task",
        "System.Title": "Test Task",
        "System.State": "Closed"
    }
    
    expected = "Bug 123: Test Bug (Active)\nTask 456: Test Task (Closed)"
    assert format_work_items([work_item1, work_item2]) == expected

def test_format_work_items_missing_fields():
    """Test formatting work items with missing fields."""
    work_item = MagicMock(spec=WorkItem)
    work_item.id = 123
    work_item.fields = {}
    
    expected = "Unknown 123: Untitled (Unknown)"
    assert format_work_items([work_item]) == expected

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
    expected = "Bug 123: Test Bug (Active)\nTask 456: Test Task (Closed)"
    
    assert result == expected
