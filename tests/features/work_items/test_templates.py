from unittest.mock import MagicMock

from azure.devops.v7_1.work_item_tracking.models import WorkItemTemplate

from mcp_azure_devops.features.work_items.tools.templates import (
    _get_work_item_template_impl,
    _get_work_item_templates_impl,
)


def test_get_work_item_templates_impl_with_templates():
    """Test retrieving work item templates."""
    # Arrange
    mock_client = MagicMock()
    
    # Create mock templates
    mock_template1 = MagicMock(spec=WorkItemTemplate)
    mock_template1.id = "template1"
    mock_template1.name = "Bug Template"
    mock_template1.description = "Template for bugs"
    mock_template1.work_item_type_name = "Bug"
    mock_template1.fields = {
        "System.Title": "New Bug",
        "System.Description": "Bug description"
    }
    
    mock_template2 = MagicMock(spec=WorkItemTemplate)
    mock_template2.id = "template2"
    mock_template2.name = "Task Template"
    mock_template2.description = "Template for tasks"
    mock_template2.work_item_type_name = "Task"
    mock_template2.fields = {
        "System.Title": "New Task",
        "System.Description": "Task description"
    }
    
    mock_client.get_templates.return_value = [mock_template1, mock_template2]
    
    team_context = {
        "project": "TestProject",
        "team": "TestTeam"
    }
    
    # Act
    result = _get_work_item_templates_impl(team_context, "Bug", mock_client)
    
    # Assert
    mock_client.get_templates.assert_called_once()
    
    # Verify the table contents
    assert "Work Item Templates for Team: TestTeam" in result
    assert "Filtered by type: Bug" in result
    assert "Bug Template" in result
    assert "Template for bugs" in result
    assert "Bug" in result
    assert "Task Template" in result
    assert "Task" in result


def test_get_work_item_templates_impl_no_templates():
    """Test retrieving work item templates when none exist."""
    # Arrange
    mock_client = MagicMock()
    mock_client.get_templates.return_value = []
    
    team_context = {
        "project": "TestProject",
        "team": "TestTeam"
    }
    
    # Act
    result = _get_work_item_templates_impl(team_context, "Bug", mock_client)
    
    # Assert
    mock_client.get_templates.assert_called_once()
    assert "No templates found for work item type 'Bug'" in result
    assert "team TestTeam" in result


def test_get_work_item_template_impl():
    """Test retrieving a specific work item template."""
    # Arrange
    mock_client = MagicMock()
    
    # Create mock template
    mock_template = MagicMock(spec=WorkItemTemplate)
    mock_template.id = "template1"
    mock_template.name = "Bug Template"
    mock_template.description = "Template for bugs"
    mock_template.work_item_type_name = "Bug"
    mock_template.fields = {
        "System.Title": "New Bug",
        "System.Description": "Bug description",
        "Microsoft.VSTS.Common.Priority": 2
    }
    
    mock_client.get_template.return_value = mock_template
    
    team_context = {
        "project": "TestProject",
        "team": "TestTeam"
    }
    
    # Act
    result = _get_work_item_template_impl(
        team_context, "template1", mock_client)
    
    # Assert
    mock_client.get_template.assert_called_once()
    assert "Template: Bug Template" in result
    assert "Description: Template for bugs" in result
    assert "Work item type name: Bug" in result
    assert "Id: template1" in result
    assert "Default Field Values" in result
    assert "System.Title" in result
    assert "New Bug" in result
    assert "System.Description" in result
    assert "Bug description" in result
    assert "Microsoft.VSTS.Common.Priority" in result
    assert "2" in result


def test_get_work_item_template_impl_not_found():
    """Test retrieving a template that doesn't exist."""
    # Arrange
    mock_client = MagicMock()
    mock_client.get_template.return_value = None
    
    team_context = {
        "project": "TestProject",
        "team": "TestTeam"
    }
    
    # Act
    result = _get_work_item_template_impl(
        team_context, "non-existent", mock_client)
    
    # Assert
    mock_client.get_template.assert_called_once()
    assert "Template with ID 'non-existent' not found" in result


def test_get_work_item_template_impl_error_handling():
    """Test error handling in get_work_item_template_impl."""
    # Arrange
    mock_client = MagicMock()
    mock_client.get_template.side_effect = Exception("Test error")
    
    team_context = {
        "project": "TestProject",
        "team": "TestTeam"
    }
    
    # Act
    result = _get_work_item_template_impl(
        team_context, "template1", mock_client)
    
    # Assert
    assert "Error retrieving template 'template1': Test error" in result