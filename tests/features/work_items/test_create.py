from unittest.mock import MagicMock, patch

from azure.devops.v7_1.work_item_tracking.models import WorkItem

from mcp_azure_devops.features.work_items.tools.create import (
    _add_link_to_work_item_impl,
    _build_field_document,
    _build_link_document,
    _create_work_item_impl,
    _ensure_system_prefix,
    _get_organization_url,
    _prepare_standard_fields,
    _update_work_item_impl,
)


def test_build_field_document():
    """Test building JSON patch document from fields dictionary."""
    # Simple field values
    fields = {
        "System.Title": "Test Bug",
        "System.Description": "This is a test bug",
        "System.State": "Active",
    }
    
    document = _build_field_document(fields)
    
    # Verify document structure
    assert len(document) == 3
    
    # Check first operation
    assert document[0].op == "add"
    assert document[0].path == "/fields/System.Title"
    assert document[0].value == "Test Bug"
    
    # Test with replace operation
    document = _build_field_document(fields, "replace")
    assert document[0].op == "replace"
    
    # Test with field name without /fields/ prefix
    fields = {"Title": "Test Bug"}
    document = _build_field_document(fields)
    assert document[0].path == "/fields/Title"


@patch("mcp_azure_devops.features.work_items.tools.create.os")
def test_get_organization_url(mock_os):
    """Test retrieving organization URL from environment."""
    # Test with trailing slash
    mock_os.environ.get.return_value = "https://dev.azure.com/org/"
    url = _get_organization_url()
    assert url == "https://dev.azure.com/org"
    
    # Test without trailing slash
    mock_os.environ.get.return_value = "https://dev.azure.com/org"
    url = _get_organization_url()
    assert url == "https://dev.azure.com/org"
    
    # Test with empty value
    mock_os.environ.get.return_value = ""
    url = _get_organization_url()
    assert url == ""


def test_build_link_document():
    """Test building link document for work item relationships."""
    target_id = 123
    link_type = "System.LinkTypes.Hierarchy-Reverse"
    org_url = "https://dev.azure.com/org"
    
    document = _build_link_document(target_id, link_type, org_url)
    
    # Verify document structure
    assert len(document) == 1
    assert document[0].op == "add"
    assert document[0].path == "/relations/-"
    assert document[0].value["rel"] == link_type
    assert document[0].value["url"] == "https://dev.azure.com/org/_apis/wit/workItems/123"


def test_create_work_item_impl():
    """Test creating a work item."""
    # Arrange
    mock_client = MagicMock()
    
    # Create mock for new work item
    mock_work_item = MagicMock(spec=WorkItem)
    mock_work_item.id = 123
    mock_work_item.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Test Bug",
        "System.State": "New",
        "System.TeamProject": "Test Project",
    }
    
    mock_client.create_work_item.return_value = mock_work_item
    
    # Fields to create work item
    fields = {
        "System.Title": "Test Bug",
        "System.Description": "This is a test bug",
    }
    
    # Act
    result = _create_work_item_impl(
        fields=fields,
        project="Test Project",
        work_item_type="Bug",
        wit_client=mock_client
    )
    
    # Assert
    mock_client.create_work_item.assert_called_once()
    assert "# Work Item 123" in result
    assert "**System.WorkItemType**: Bug" in result
    assert "**System.Title**: Test Bug" in result
    assert "**System.State**: New" in result
    
    # Verify document passed to create_work_item
    args, kwargs = mock_client.create_work_item.call_args
    document = kwargs.get("document") or args[0]
    assert len(document) == 2  # Two fields in our test
    assert kwargs.get("project") == "Test Project"
    assert kwargs.get("type") == "Bug"


@patch("mcp_azure_devops.features.work_items.tools.create._get_organization_url")
def test_create_work_item_impl_with_parent(mock_get_org_url):
    """Test creating a work item with parent relationship."""
    # Arrange
    mock_client = MagicMock()
    
    # Create mock for new work item
    mock_work_item = MagicMock(spec=WorkItem)
    mock_work_item.id = 123
    mock_work_item.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Test Bug",
        "System.State": "New",
        "System.TeamProject": "Test Project",
    }
    
    # Setup organization URL
    mock_get_org_url.return_value = "https://dev.azure.com/org"
    
    # Setup mock returns for create and update
    mock_client.create_work_item.return_value = mock_work_item
    mock_client.update_work_item.return_value = mock_work_item
    
    # Fields to create work item
    fields = {
        "System.Title": "Test Bug",
        "System.Description": "This is a test bug",
    }
    
    # Act
    result = _create_work_item_impl(
        fields=fields,
        project="Test Project",
        work_item_type="Bug",
        wit_client=mock_client,
        parent_id=456
    )
    
    # Assert
    mock_client.create_work_item.assert_called_once()
    mock_client.update_work_item.assert_called_once()
    
    # Verify update_work_item was called with link document
    args, kwargs = mock_client.update_work_item.call_args
    document = kwargs.get("document") or args[0]
    assert document[0].path == "/relations/-"
    assert document[0].value["rel"] == "System.LinkTypes.Hierarchy-Reverse"
    
    # Check result formatting
    assert "# Work Item 123" in result
    assert "**System.Title**: Test Bug" in result


def test_update_work_item_impl():
    """Test updating a work item."""
    # Arrange
    mock_client = MagicMock()
    
    # Create mock for updated work item
    mock_work_item = MagicMock(spec=WorkItem)
    mock_work_item.id = 123
    mock_work_item.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Updated Bug",
        "System.State": "Active",
        "System.TeamProject": "Test Project",
    }
    
    mock_client.update_work_item.return_value = mock_work_item
    
    # Fields to update
    fields = {
        "System.Title": "Updated Bug",
        "System.State": "Active",
    }
    
    # Act
    result = _update_work_item_impl(
        id=123,
        fields=fields,
        wit_client=mock_client,
        project="Test Project"
    )
    
    # Assert
    mock_client.update_work_item.assert_called_once()
    assert "# Work Item 123" in result
    assert "**System.Title**: Updated Bug" in result
    assert "**System.WorkItemType**: Bug" in result
    assert "**System.State**: Active" in result
    
    # Verify document passed to update_work_item
    args, kwargs = mock_client.update_work_item.call_args
    document = kwargs.get("document") or args[0]
    assert len(document) == 2  # Two fields in our test
    assert all(op.op == "replace" for op in document)  # All operations should be replace
    assert kwargs.get("id") == 123
    assert kwargs.get("project") == "Test Project"


def test_add_link_to_work_item_impl():
    """Test adding a link between work items."""
    # Arrange
    mock_client = MagicMock()
    
    # Create mock for updated work item
    mock_work_item = MagicMock(spec=WorkItem)
    mock_work_item.id = 123
    mock_work_item.fields = {
        "System.WorkItemType": "Bug",
        "System.Title": "Test Bug",
        "System.State": "Active",
        "System.TeamProject": "Test Project",
    }
    
    mock_client.update_work_item.return_value = mock_work_item
    
    # Act with patch for organization URL
    with patch("mcp_azure_devops.features.work_items.tools.create._get_organization_url",
              return_value="https://dev.azure.com/org"):
        result = _add_link_to_work_item_impl(
            source_id=123,
            target_id=456,
            link_type="System.LinkTypes.Hierarchy-Reverse",
            wit_client=mock_client,
            project="Test Project"
        )
    
    # Assert
    mock_client.update_work_item.assert_called_once()
    
    # Verify document passed to update_work_item
    args, kwargs = mock_client.update_work_item.call_args
    document = kwargs.get("document") or args[0]
    assert document[0].path == "/relations/-"
    assert document[0].value["rel"] == "System.LinkTypes.Hierarchy-Reverse"
    assert document[0].value["url"] == "https://dev.azure.com/org/_apis/wit/workItems/456"
    
    # Check result formatting
    assert "# Work Item 123" in result
    assert "**System.Title**: Test Bug" in result
    assert "**System.State**: Active" in result


def test_prepare_standard_fields():
    """Test preparing standard fields dictionary."""
    # Test with all fields specified
    fields = _prepare_standard_fields(
        title="Test Bug",
        description="This is a test bug",
        state="Active",
        assigned_to="user@example.com",
        iteration_path="Project\\Sprint 1",
        area_path="Project\\Area",
        story_points=5.5,
        priority=1,
        tags="tag1; tag2"
    )
    
    # Verify fields
    assert fields["System.Title"] == "Test Bug"
    assert fields["System.Description"] == "This is a test bug"
    assert fields["System.State"] == "Active"
    assert fields["System.AssignedTo"] == "user@example.com"
    assert fields["System.IterationPath"] == "Project\\Sprint 1"
    assert fields["System.AreaPath"] == "Project\\Area"
    assert fields["Microsoft.VSTS.Scheduling.StoryPoints"] == "5.5"
    assert fields["Microsoft.VSTS.Common.Priority"] == "1"
    assert fields["System.Tags"] == "tag1; tag2"
    
    # Test with subset of fields
    fields = _prepare_standard_fields(
        title="Test Bug",
        state="Active"
    )
    
    assert len(fields) == 2
    assert "System.Title" in fields
    assert "System.State" in fields
    assert "System.Description" not in fields


def test_ensure_system_prefix():
    """Test ensuring field names have proper prefix."""
    # Test with already prefixed fields
    assert _ensure_system_prefix("System.Title") == "System.Title"
    assert _ensure_system_prefix("Microsoft.VSTS.Common.Priority") == "Microsoft.VSTS.Common.Priority"
    
    # Test with common short names
    assert _ensure_system_prefix("title") == "System.Title"
    assert _ensure_system_prefix("description") == "System.Description"
    assert _ensure_system_prefix("assignedTo") == "System.AssignedTo"
    assert _ensure_system_prefix("iterationPath") == "System.IterationPath"
    assert _ensure_system_prefix("area_path") == "System.AreaPath"
    assert _ensure_system_prefix("storyPoints") == "Microsoft.VSTS.Scheduling.StoryPoints"
    assert _ensure_system_prefix("priority") == "Microsoft.VSTS.Common.Priority"
    
    # Test with unknown field - should return as is
    assert _ensure_system_prefix("CustomField") == "CustomField"
