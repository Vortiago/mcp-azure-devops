"""
Team tools for Azure DevOps.

This module provides MCP tools for working with Azure DevOps teams.
"""
from typing import Optional
from azure.devops.v7_1.core.models import WebApiTeam
from azure.devops.v7_1.core import CoreClient
from mcp_azure_devops.features.teams.common import get_core_client, AzureDevOpsClientError


def _format_team(team: WebApiTeam) -> str:
    """
    Format team information.
    
    Args:
        team: Team object to format
        
    Returns:
        String with team details
    """
    # Basic information that should always be available
    formatted_info = [f"# Team: {team.name}"]
    formatted_info.append(f"ID: {team.id}")
    
    # Add description if available
    if hasattr(team, "description") and team.description:
        formatted_info.append(f"Description: {team.description}")
    
    # Add project information if available
    if hasattr(team, "project_name") and team.project_name:
        formatted_info.append(f"Project: {team.project_name}")
    
    if hasattr(team, "project_id") and team.project_id:
        formatted_info.append(f"Project ID: {team.project_id}")
    
    
    return "\n".join(formatted_info)


def _get_all_teams_impl(
    core_client: CoreClient,
    user_is_member_of: Optional[bool] = None,
    top: Optional[int] = None,
    skip: Optional[int] = None,
    expand_identity: Optional[bool] = None
) -> str:
    """
    Implementation of teams retrieval.
    
    Args:
        core_client: Core client
        user_is_member_of: If true, then return all teams requesting user is member.
                          Otherwise return all teams user has read access.
        top: Maximum number of teams to return
        skip: Number of teams to skip
            
    Returns:
        Formatted string containing team information
    """
    try:
        # Call the SDK function - note we're mapping user_is_member_of to mine parameter
        teams = core_client.get_all_teams(
            mine=user_is_member_of,
            top=top,
            skip=skip
        )
        
        if not teams:
            return "No teams found."
        
        formatted_teams = []
        for team in teams:
            formatted_teams.append(_format_team(team))
        
        return "\n\n".join(formatted_teams)
            
    except Exception as e:
        return f"Error retrieving teams: {str(e)}"


def register_tools(mcp) -> None:
    """
    Register team tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def get_all_teams(
        user_is_member_of: Optional[bool] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None
    ) -> str:
        """
        Get a list of all teams in the organization.
        
        Args:
            user_is_member_of: If true, return only teams where the current user is a member.
                              Otherwise return all teams the user has read access to.
            top: Maximum number of teams to return
            skip: Number of teams to skip
                
        Returns:
            Formatted string containing team information
        """
        try:
            core_client = get_core_client()
            return _get_all_teams_impl(
                core_client, 
                user_is_member_of,
                top,
                skip
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
