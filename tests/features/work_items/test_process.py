from unittest.mock import MagicMock, patch

from mcp_azure_devops.features.work_items.tools.process import (
    _get_process_details_impl,
    _get_project_process_id_impl,
    _list_processes_impl,
)


@patch("mcp_azure_devops.features.work_items.tools.process.get_core_client")
def test_get_project_process_id_impl(mock_get_core_client):
    """Test retrieving project process ID."""
    # Arrange
    mock_core_client = MagicMock()
    mock_get_core_client.return_value = mock_core_client
    
    # Mock project details
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_project.capabilities = {
        "processTemplate": {
            "templateTypeId": "process-id-123",
            "templateName": "Agile"
        }
    }
    
    mock_core_client.get_project.return_value = mock_project
    
    # Act
    result = _get_project_process_id_impl("Test Project")
    
    # Assert
    mock_core_client.get_project.assert_called_once_with("Test Project", include_capabilities=True)
    
    # Check result formatting
    assert "Process for Project: Test Project" in result
    assert "Process Name: Agile" in result
    assert "Process ID: process-id-123" in result


@patch("mcp_azure_devops.features.work_items.tools.process.get_core_client")
def test_get_project_process_id_impl_no_process(mock_get_core_client):
    """Test retrieving project process ID when no process is found."""
    # Arrange
    mock_core_client = MagicMock()
    mock_get_core_client.return_value = mock_core_client
    
    # Mock project details with no process
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_project.capabilities = {
        "processTemplate": {}  # Empty process template
    }
    
    mock_core_client.get_project.return_value = mock_project
    
    # Act
    result = _get_project_process_id_impl("Test Project")
    
    # Assert
    assert "Could not determine process ID for project Test Project" in result


@patch("mcp_azure_devops.features.work_items.tools.process.get_core_client")
def test_get_project_process_id_impl_error(mock_get_core_client):
    """Test error handling in get_project_process_id_impl."""
    # Arrange
    mock_core_client = MagicMock()
    mock_get_core_client.return_value = mock_core_client
    
    # Simulate error
    mock_core_client.get_project.side_effect = Exception("Test error")
    
    # Act
    result = _get_project_process_id_impl("Test Project")
    
    # Assert
    assert "Error retrieving process ID for project 'Test Project': Test error" in result


@patch("mcp_azure_devops.features.work_items.tools.process.get_work_item_tracking_process_client")
def test_get_process_details_impl(mock_get_process_client):
    """Test retrieving process details."""
    # Arrange
    mock_process_client = MagicMock()
    mock_get_process_client.return_value = mock_process_client
    
    # Mock process
    mock_process = MagicMock()
    mock_process.name = "Agile"
    mock_process.reference_name = "Agile"
    mock_process.type_id = "process-id-123"
    mock_process.description = "Agile process template"
    
    # Mock process properties
    mock_properties = MagicMock()
    mock_properties.is_default = True
    mock_properties.is_enabled = True
    mock_process.properties = mock_properties
    
    # Mock work item types
    mock_wit_type1 = MagicMock()
    mock_wit_type1.name = "Bug"
    mock_wit_type1.reference_name = "System.Bug"
    mock_wit_type1.description = "Represents a bug or defect"
    
    mock_wit_type2 = MagicMock()
    mock_wit_type2.name = "Task"
    mock_wit_type2.reference_name = "System.Task"
    mock_wit_type2.description = "Represents a task item"
    
    mock_process_client.get_process_by_its_id.return_value = mock_process
    mock_process_client.get_process_work_item_types.return_value = [mock_wit_type1, mock_wit_type2]
    
    # Act
    result = _get_process_details_impl("process-id-123")
    
    # Assert
    mock_process_client.get_process_by_its_id.assert_called_once_with("process-id-123")
    mock_process_client.get_process_work_item_types.assert_called_once_with("process-id-123")
    
    # Check result formatting
    assert "Process: Agile" in result
    assert "Description: Agile process template" in result
    assert "Reference Name: Agile" in result
    assert "Type ID: process-id-123" in result
    
    # Check properties section
    assert "Properties" in result
    assert "Is default: True" in result
    assert "Is enabled: True" in result
    
    # Check work item types section
    assert "Work Item Types" in result
    assert "Bug" in result
    assert "System.Bug" in result
    assert "Represents a bug or defect" in result
    assert "Task" in result
    assert "System.Task" in result
    assert "Represents a task item" in result


@patch("mcp_azure_devops.features.work_items.tools.process.get_work_item_tracking_process_client")
def test_get_process_details_impl_not_found(mock_get_process_client):
    """Test retrieving process details when process is not found."""
    # Arrange
    mock_process_client = MagicMock()
    mock_get_process_client.return_value = mock_process_client
    
    # Process not found
    mock_process_client.get_process_by_its_id.return_value = None
    
    # Act
    result = _get_process_details_impl("non-existent-id")
    
    # Assert
    assert "Process with ID 'non-existent-id' not found" in result


@patch("mcp_azure_devops.features.work_items.tools.process.get_work_item_tracking_process_client")
def test_get_process_details_impl_error(mock_get_process_client):
    """Test error handling in get_process_details_impl."""
    # Arrange
    mock_process_client = MagicMock()
    mock_get_process_client.return_value = mock_process_client
    
    # Simulate error
    mock_process_client.get_process_by_its_id.side_effect = Exception("Test error")
    
    # Act
    result = _get_process_details_impl("process-id-123")
    
    # Assert
    assert "Error retrieving process details for process ID 'process-id-123': Test error" in result


@patch("mcp_azure_devops.features.work_items.tools.process.get_work_item_tracking_process_client")
def test_list_processes_impl(mock_get_process_client):
    """Test listing all processes."""
    # Arrange
    mock_process_client = MagicMock()
    mock_get_process_client.return_value = mock_process_client
    
    # Mock processes
    mock_process1 = MagicMock()
    mock_process1.name = "Agile"
    mock_process1.type_id = "process-id-123"
    mock_process1.reference_name = "Agile"
    mock_process1.description = "Agile process template"
    
    mock_properties1 = MagicMock()
    mock_properties1.is_default = True
    mock_process1.properties = mock_properties1
    
    mock_process2 = MagicMock()
    mock_process2.name = "Scrum"
    mock_process2.type_id = "process-id-456"
    mock_process2.reference_name = "Scrum"
    mock_process2.description = "Scrum process template"
    
    mock_properties2 = MagicMock()
    mock_properties2.is_default = False
    mock_process2.properties = mock_properties2
    
    mock_process_client.get_list_of_processes.return_value = [mock_process1, mock_process2]
    
    # Act
    result = _list_processes_impl()
    
    # Assert
    mock_process_client.get_list_of_processes.assert_called_once()
    
    # Check result formatting
    assert "Available Processes" in result
    assert "Agile" in result
    assert "process-id-123" in result
    assert "Agile process template" in result
    assert "Yes" in result  # For is_default=True
    assert "Scrum" in result
    assert "process-id-456" in result
    assert "Scrum process template" in result
    assert "No" in result  # For is_default=False


@patch("mcp_azure_devops.features.work_items.tools.process.get_work_item_tracking_process_client")
def test_list_processes_impl_no_processes(mock_get_process_client):
    """Test listing processes when none exist."""
    # Arrange
    mock_process_client = MagicMock()
    mock_get_process_client.return_value = mock_process_client
    
    # No processes
    mock_process_client.get_list_of_processes.return_value = []
    
    # Act
    result = _list_processes_impl()
    
    # Assert
    assert "No processes found in the organization" in result


@patch("mcp_azure_devops.features.work_items.tools.process.get_work_item_tracking_process_client")
def test_list_processes_impl_error(mock_get_process_client):
    """Test error handling in list_processes_impl."""
    # Arrange
    mock_process_client = MagicMock()
    mock_get_process_client.return_value = mock_process_client
    
    # Simulate error
    mock_process_client.get_list_of_processes.side_effect = Exception("Test error")
    
    # Act
    result = _list_processes_impl()
    
    # Assert
    assert "Error retrieving processes: Test error" in result