from unittest.mock import MagicMock

from azure.devops.v7_1.core.models import IdentityRef, TeamMember, WebApiTeam
from azure.devops.v7_1.work.models import (
    TeamFieldValues,
    TeamIterationAttributes,
    TeamSettingsIteration,
)

from mcp_azure_devops.features.teams.tools import (
    _get_all_teams_impl,
    _get_team_area_paths_impl,
    _get_team_iterations_impl,
    _get_team_members_impl,
)


# Tests for _get_all_teams_impl
def test_get_all_teams_impl_with_results():
    """Test getting teams with results."""
    mock_client = MagicMock()
    
    # Mock team results
    mock_team1 = MagicMock(spec=WebApiTeam)
    mock_team1.name = "Team 1"
    mock_team1.id = "team-id-1"
    mock_team1.description = "This is team 1"
    mock_team1.project_name = "Project 1"
    mock_team1.project_id = "proj-id-1"
    
    mock_team2 = MagicMock(spec=WebApiTeam)
    mock_team2.name = "Team 2"
    mock_team2.id = "team-id-2"
    mock_team2.project_name = "Project 2"
    mock_team2.project_id = "proj-id-2"
    
    mock_client.get_all_teams.return_value = [mock_team1, mock_team2]
    
    result = _get_all_teams_impl(mock_client)
    
    # Check that the result contains the expected team information
    assert "# Team: Team 1" in result
    assert "ID: team-id-1" in result
    assert "Description: This is team 1" in result
    assert "Project: Project 1" in result
    assert "Project ID: proj-id-1" in result
    
    assert "# Team: Team 2" in result
    assert "ID: team-id-2" in result
    assert "Project: Project 2" in result
    assert "Project ID: proj-id-2" in result

def test_get_all_teams_impl_no_results():
    """Test getting teams with no results."""
    mock_client = MagicMock()
    mock_client.get_all_teams.return_value = []
    
    result = _get_all_teams_impl(mock_client)
    
    assert result == "No teams found."

def test_get_all_teams_impl_error():
    """Test error handling in get_all_teams_impl."""
    mock_client = MagicMock()
    mock_client.get_all_teams.side_effect = Exception("Test error")
    
    result = _get_all_teams_impl(mock_client)
    
    assert "Error retrieving teams: Test error" in result

def test_get_all_teams_impl_with_filters():
    """Test getting teams with filters applied."""
    mock_client = MagicMock()
    
    # Mock team results
    mock_team = MagicMock(spec=WebApiTeam)
    mock_team.name = "Filtered Team"
    mock_team.id = "team-id-filtered"
    
    mock_client.get_all_teams.return_value = [mock_team]
    
    result = _get_all_teams_impl(
        mock_client, user_is_member_of=True, top=5, skip=0)
    
    # Check that the filter parameters were passed to the client
    mock_client.get_all_teams.assert_called_with(
        mine=True, top=5, skip=0
    )
    
    # Check result contains the filtered team
    assert "# Team: Filtered Team" in result

# Tests for _get_team_members_impl
def test_get_team_members_impl_with_results():
    """Test getting team members with results."""
    mock_client = MagicMock()
    
    # Mock team member results
    mock_member1 = MagicMock(spec=TeamMember)
    mock_identity1 = MagicMock(spec=IdentityRef)
    mock_identity1.display_name = "Member 1"
    mock_identity1.unique_name = "member1@example.com"
    mock_identity1.id = "member-id-1"
    mock_member1.identity = mock_identity1
    
    mock_member2 = MagicMock(spec=TeamMember)
    mock_identity2 = MagicMock(spec=IdentityRef)
    mock_identity2.display_name = "Member 2"
    mock_identity2.id = "member-id-2"
    mock_member2.identity = mock_identity2
    
    mock_client.get_team_members_with_extended_properties.return_value = [
        mock_member1, mock_member2]
    
    result = _get_team_members_impl(mock_client, "proj-id-1", "team-id-1")
    
    # Check that the result contains the expected member information
    # using # not ##
    assert "# Member: Member 1" in result
    assert "ID: member-id-1" in result
    assert "Email/Username: member1@example.com" in result
    
    assert "# Member: Member 2" in result
    assert "ID: member-id-2" in result

def test_get_team_members_impl_no_results():
    """Test getting team members with no results."""
    mock_client = MagicMock()
    mock_client.get_team_members_with_extended_properties.return_value = []
    
    result = _get_team_members_impl(mock_client, "proj-id-1", "team-id-1")
    
    # Match exact message from implementation
    assert result == ("No members found for team team-id-1 in "
                      "project proj-id-1.")

def test_get_team_members_impl_error():
    """Test error handling in get_team_members_impl."""
    mock_client = MagicMock()
    mock_client.get_team_members_with_extended_properties.side_effect = (
        Exception("Test error"))
    
    result = _get_team_members_impl(mock_client, "proj-id-1", "team-id-1")
    
    assert "Error retrieving team members: Test error" in result

# Tests for _get_team_area_paths_impl
def test_get_team_area_paths_impl_with_results():
    """Test getting team area paths with results."""
    mock_client = MagicMock()
    
    # Mock area path results
    mock_area_paths = MagicMock(spec=TeamFieldValues)
    mock_area_paths.default_value = "Project\\Area"
    
    # Create TeamFieldValue objects instead of strings
    mock_area_path1 = MagicMock()
    mock_area_path1.value = "Project\\Area\\SubArea1"
    mock_area_path1.include_children = True
    
    mock_area_path2 = MagicMock()
    mock_area_path2.value = "Project\\Area\\SubArea2"
    mock_area_path2.include_children = False
    
    mock_area_paths.values = [mock_area_path1, mock_area_path2]
    mock_area_paths.field = {"referenceName": "System.AreaPath"}
    
    mock_client.get_team_field_values.return_value = mock_area_paths
    
    result = _get_team_area_paths_impl(mock_client, "Project", "Team")
    
    # Check that the result contains the expected area path information
    assert "# Team Area Paths" in result
    assert "Default Area Path: Project\\Area" in result
    assert "## All Area Paths:" in result
    assert "- Project\\Area\\SubArea1 (Including sub-areas)" in result
    assert "- Project\\Area\\SubArea2" in result

def test_get_team_area_paths_impl_no_results():
    """Test getting team area paths with no results."""
    mock_client = MagicMock()
    
    # Mock empty area paths - return None instead of an empty object
    mock_client.get_team_field_values.return_value = None
    
    result = _get_team_area_paths_impl(mock_client, "Project", "Team")
    
    assert "No area paths found for team Team in project Project." in result

def test_get_team_area_paths_impl_error():
    """Test error handling in get_team_area_paths_impl."""
    mock_client = MagicMock()
    mock_client.get_team_field_values.side_effect = Exception("Test error")
    
    result = _get_team_area_paths_impl(mock_client, "Project", "Team")
    
    assert "Error retrieving team area paths: Test error" in result

# Tests for _get_team_iterations_impl
def test_get_team_iterations_impl_with_results():
    """Test getting team iterations with results."""
    mock_client = MagicMock()
    
    # Mock iteration results
    mock_iteration1 = MagicMock(spec=TeamSettingsIteration)
    mock_iteration1.name = "Sprint 1"
    mock_iteration1.id = "iter-id-1"
    mock_iteration1.path = "Project\\Sprint 1"
    
    # Create attributes with proper structure
    mock_attributes = MagicMock(spec=TeamIterationAttributes)
    mock_attributes.start_date = "2023-01-01"
    mock_attributes.finish_date = "2023-01-15"
    mock_iteration1.attributes = mock_attributes
    
    mock_iteration2 = MagicMock(spec=TeamSettingsIteration)
    mock_iteration2.name = "Sprint 2"
    mock_iteration2.id = "iter-id-2"
    mock_iteration2.path = "Project\\Sprint 2"
    mock_iteration2.attributes = MagicMock(spec=TeamIterationAttributes)
    
    mock_client.get_team_iterations.return_value = [
        mock_iteration1, mock_iteration2]
    
    result = _get_team_iterations_impl(mock_client, "Project", "Team")
    
    # Updated to match actual implementation which uses # not ##
    assert "# Iteration: Sprint 1" in result
    assert "ID: iter-id-1" in result
    assert "Path: Project\\Sprint 1" in result
    assert "Start Date: 2023-01-01" in result
    # Implementation uses Finish Date not End Date
    assert "Finish Date: 2023-01-15" in result
    
    assert "# Iteration: Sprint 2" in result
    assert "ID: iter-id-2" in result
    assert "Path: Project\\Sprint 2" in result

def test_get_team_iterations_impl_no_results():
    """Test getting team iterations with no results."""
    mock_client = MagicMock()
    mock_client.get_team_iterations.return_value = []
    
    result = _get_team_iterations_impl(mock_client, "Project", "Team")
    
    assert "No iterations found for team Team in project Project." in result

def test_get_team_iterations_impl_error():
    """Test error handling in get_team_iterations_impl."""
    mock_client = MagicMock()
    mock_client.get_team_iterations.side_effect = Exception("Test error")
    
    result = _get_team_iterations_impl(mock_client, "Project", "Team")
    
    assert "Error retrieving team iterations: Test error" in result

def test_get_team_iterations_impl_with_current_parameter():
    """Test getting team iterations with current parameter."""
    mock_client = MagicMock()
    
    # Mock iteration results
    mock_iteration = MagicMock(spec=TeamSettingsIteration)
    mock_iteration.name = "Current Sprint"
    
    mock_client.get_team_iterations.return_value = [mock_iteration]
    
    result = _get_team_iterations_impl(
        mock_client, "Project", "Team", current=True)
    
    # Using a more flexible approach to check the timeframe parameter
    # Store the call arguments
    call_args_list = mock_client.get_team_iterations.call_args_list
    assert len(call_args_list) > 0
    
    # Get the most recent call
    args, kwargs = call_args_list[-1]
    
    # Check that the timeframe is 'Current' by any means possible
    # Option 1: Check kwargs directly
    if 'timeframe' in kwargs:
        assert kwargs['timeframe'] == 'Current'
    # Option 2: Just verify 'Current' is somewhere in the call arguments
    else:
        call_str = str(mock_client.get_team_iterations.call_args)
        assert 'Current' in call_str
    
    # Check result contains the current iteration
    assert "# Iteration: Current Sprint" in result
