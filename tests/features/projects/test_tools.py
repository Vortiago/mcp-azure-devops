import pytest
from unittest.mock import MagicMock
from azure.devops.v7_1.core.models import TeamProjectReference
from mcp_azure_devops.features.projects.tools import _get_projects_impl

def test_get_projects_impl_with_results():
    """Test getting projects with results."""
    mock_client = MagicMock()
    
    # Mock project results
    mock_project1 = MagicMock(spec=TeamProjectReference)
    mock_project1.name = "Project 1"
    mock_project1.id = "proj-id-1"
    mock_project1.description = "This is project 1"
    mock_project1.state = "wellFormed"
    mock_project1.visibility = "private"
    mock_project1.url = "https://dev.azure.com/test/project1"
    
    mock_project2 = MagicMock(spec=TeamProjectReference)
    mock_project2.name = "Project 2"
    mock_project2.id = "proj-id-2"
    mock_project2.state = "wellFormed"
    
    mock_client.get_projects.return_value = [mock_project1, mock_project2]
    
    result = _get_projects_impl(mock_client)
    
    # Check that the result contains the expected project information
    assert "# Project: Project 1" in result
    assert "ID: proj-id-1" in result
    assert "Description: This is project 1" in result
    assert "State: wellFormed" in result
    assert "Visibility: private" in result
    assert "URL: https://dev.azure.com/test/project1" in result
    
    assert "# Project: Project 2" in result
    assert "ID: proj-id-2" in result
    assert "State: wellFormed" in result

def test_get_projects_impl_no_results():
    """Test getting projects with no results."""
    mock_client = MagicMock()
    mock_client.get_projects.return_value = []
    
    result = _get_projects_impl(mock_client)
    
    assert result == "No projects found."

def test_get_projects_impl_error():
    """Test error handling in get_projects_impl."""
    mock_client = MagicMock()
    mock_client.get_projects.side_effect = Exception("Test error")
    
    result = _get_projects_impl(mock_client)
    
    assert "Error retrieving projects: Test error" in result

def test_get_projects_impl_with_filters():
    """Test getting projects with filters applied."""
    mock_client = MagicMock()
    
    # Mock project results
    mock_project = MagicMock(spec=TeamProjectReference)
    mock_project.name = "Filtered Project"
    mock_project.id = "proj-id-filtered"
    
    mock_client.get_projects.return_value = [mock_project]
    
    result = _get_projects_impl(mock_client, state_filter="wellFormed", top=5)
    
    # Check that the filter parameters were passed to the client
    mock_client.get_projects.assert_called_with(state_filter="wellFormed", top=5)
    
    # Check result contains the filtered project
    assert "# Project: Filtered Project" in result
