"""
Team tools for Azure DevOps.

This module provides MCP tools for working with Azure DevOps teams.
"""
from typing import Optional

from azure.devops.v7_1.core import CoreClient
from azure.devops.v7_1.core.models import WebApiTeam
from azure.devops.v7_1.work.models import TeamContext

from mcp_azure_devops.features.teams.common import (
    AzureDevOpsClientError,
    get_core_client,
    get_work_client,
)


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


def _format_team_member(team_member) -> str:
    """
    Format team member information.
    
    Args:
        team_member: Team member object to format
        
    Returns:
        String with team member details
    """
    formatted_info = []
    
    # Get identity information
    if hasattr(team_member, "identity") and team_member.identity:
        identity = team_member.identity
        # Use display name if available, otherwise use ID
        if hasattr(identity, "display_name") and identity.display_name:
            formatted_info.append(f"# Member: {identity.display_name}")
        else:
            formatted_info.append(f"# Member ID: {identity.id}")
            
        # Add ID
        if hasattr(identity, "id") and identity.id:
            formatted_info.append(f"ID: {identity.id}")
            
        # Add descriptor
        if hasattr(identity, "descriptor") and identity.descriptor:
            formatted_info.append(f"Descriptor: {identity.descriptor}")
            
        # Add unique name (email/username)
        if hasattr(identity, "unique_name") and identity.unique_name:
            formatted_info.append(f"Email/Username: {identity.unique_name}")
    else:
        formatted_info.append("# Unknown Member")
    
    # Add team admin status
    if hasattr(team_member, "is_team_admin"):
        is_admin = "Yes" if team_member.is_team_admin else "No"
        formatted_info.append(f"Team Administrator: {is_admin}")
    
    return "\n".join(formatted_info)


def _format_team_area_path(team_field_values) -> str:
    """
    Format team area path information.
    
    Args:
        team_field_values: Team field values object to format
        
    Returns:
        String with team area path details
    """
    formatted_info = ["# Team Area Paths"]
    
    # Add default area path
    if (hasattr(team_field_values, "default_value") and 
            team_field_values.default_value):
        formatted_info.append(
            f"Default Area Path: {team_field_values.default_value}")
    
    # Add all area paths
    if hasattr(team_field_values, "values") and team_field_values.values:
        formatted_info.append("\n## All Area Paths:")
        for area_path in team_field_values.values:
            value_str = f"- {area_path.value}"
            if (hasattr(area_path, "include_children") and 
                    area_path.include_children):
                value_str += " (Including sub-areas)"
            formatted_info.append(value_str)
    
    return "\n".join(formatted_info)


def _format_team_iteration(iteration) -> str:
    """
    Format team iteration information.
    
    Args:
        iteration: Team iteration object to format
        
    Returns:
        String with team iteration details
    """
    formatted_info = [f"# Iteration: {iteration.name}"]
    
    # Add ID
    if hasattr(iteration, "id") and iteration.id:
        formatted_info.append(f"ID: {iteration.id}")
    
    # Add path
    if hasattr(iteration, "path") and iteration.path:
        formatted_info.append(f"Path: {iteration.path}")
    
    # Add attributes if available
    if hasattr(iteration, "attributes") and iteration.attributes:
        attributes = iteration.attributes
        
        # Add start date
        if hasattr(attributes, "start_date") and attributes.start_date:
            formatted_info.append(f"Start Date: {attributes.start_date}")
        
        # Add finish date
        if hasattr(attributes, "finish_date") and attributes.finish_date:
            formatted_info.append(f"Finish Date: {attributes.finish_date}")
        
        # Add time frame
        if hasattr(attributes, "time_frame") and attributes.time_frame:
            formatted_info.append(f"Time Frame: {attributes.time_frame}")
    
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
        user_is_member_of: If true, then return all teams requesting user is
                          member. Otherwise return all teams user has read 
                          access.
        top: Maximum number of teams to return
        skip: Number of teams to skip
            
    Returns:
        Formatted string containing team information
    """
    try:
        # Call the SDK function - note we're mapping user_is_member_of to mine
        # param
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


def _get_team_members_impl(
    core_client: CoreClient,
    project_id: str,
    team_id: str,
    top: Optional[int] = None,
    skip: Optional[int] = None
) -> str:
    """
    Implementation of team members retrieval.
    
    Args:
        core_client: Core client
        project_id: The name or ID (GUID) of the team project the team 
                    belongs to
        team_id: The name or ID (GUID) of the team
        top: Maximum number of members to return
        skip: Number of members to skip
            
    Returns:
        Formatted string containing team members information
    """
    try:
        team_members = core_client.get_team_members_with_extended_properties(
            project_id=project_id,
            team_id=team_id,
            top=top,
            skip=skip
        )
        
        if not team_members:
            return (f"No members found for team {team_id} in "
                    f"project {project_id}.")
        
        formatted_members = []
        for member in team_members:
            formatted_members.append(_format_team_member(member))
        
        return "\n\n".join(formatted_members)
            
    except Exception as e:
        return f"Error retrieving team members: {str(e)}"


def _get_team_area_paths_impl(
    work_client,
    project_name_or_id: str,
    team_name_or_id: str
) -> str:
    """
    Implementation of team area paths retrieval.
    
    Args:
        work_client: Work client
        project_name_or_id: The name or ID of the team project
        team_name_or_id: The name or ID of the team
            
    Returns:
        Formatted string containing team area path information
    """
    try:
        # Create a TeamContext object
        team_context = TeamContext(
            project=project_name_or_id,
            team=team_name_or_id
        )
        
        # Get the team field values
        team_field_values = work_client.get_team_field_values(team_context)
        
        if not team_field_values:
            return (f"No area paths found for team {team_name_or_id} "
                    f"in project {project_name_or_id}.")
        
        return _format_team_area_path(team_field_values)
            
    except Exception as e:
        return f"Error retrieving team area paths: {str(e)}"


def _get_team_iterations_impl(
    work_client,
    project_name_or_id: str,
    team_name_or_id: str,
    current: Optional[bool] = None
) -> str:
    """
    Implementation of team iterations retrieval.
    
    Args:
        work_client: Work client
        project_name_or_id: The name or ID of the team project
        team_name_or_id: The name or ID of the team
        current: If True, return only the current iteration
            
    Returns:
        Formatted string containing team iteration information
    """
    try:
        # Create a TeamContext object
        team_context = TeamContext(
            project=project_name_or_id,
            team=team_name_or_id
        )
        
        # Set timeframe parameter if current is True
        timeframe = "Current" if current else None
        
        # Get the team iterations
        team_iterations = work_client.get_team_iterations(
            team_context=team_context,
            timeframe=timeframe
        )
        
        if not team_iterations:
            return (f"No iterations found for team {team_name_or_id} "
                    f"in project {project_name_or_id}.")
        
        formatted_iterations = []
        for iteration in team_iterations:
            formatted_iterations.append(_format_team_iteration(iteration))
        
        return "\n\n".join(formatted_iterations)
            
    except Exception as e:
        return f"Error retrieving team iterations: {str(e)}"


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
        Retrieves all teams in the Azure DevOps organization.
        
        Use this tool when you need to:
        - Get an overview of all teams across projects
        - Find team IDs for use in other operations
        - Determine which teams exist in the organization
        - Locate specific teams by name
        
        Args:
            user_is_member_of: If true, return only teams where the current 
                user is a member. Otherwise return all teams the user 
                has read access to.
            top: Maximum number of teams to return
            skip: Number of teams to skip
                
        Returns:
            Formatted string containing team information including names,
            IDs, descriptions, and associated projects, formatted as
            markdown with each team clearly separated
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
    
    @mcp.tool()
    def get_team_members(
        project_id: str,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None
    ) -> str:
        """
        Retrieves the membership roster for a specific team.
        
        Use this tool when you need to:
        - See who belongs to a particular team
        - Find team administrators
        - Check user assignments across teams
        - Determine team size and composition
        
        Args:
            project_id: The name or ID (GUID) of the team project the team 
                belongs to
            team_id: The name or ID (GUID) of the team
            top: Maximum number of members to return
            skip: Number of members to skip
                
        Returns:
            Formatted string containing team members information including
            display names, emails, IDs, and administrator status, formatted
            as markdown with each member clearly separated
        """
        try:
            core_client = get_core_client()
            return _get_team_members_impl(
                core_client,
                project_id,
                team_id,
                top,
                skip
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_team_area_paths(
        project_name_or_id: str,
        team_name_or_id: str
    ) -> str:
        """
        Retrieves the area paths assigned to a specific team.
        
        Use this tool when you need to:
        - Understand a team's areas of responsibility
        - Check default area path assignments
        - Determine how work is classified and routed to teams
        - Set up board and backlog configurations
        
        IMPORTANT: Area paths in Azure DevOps determine which work items appear
        on a team's backlogs and boards. The default area path is used when
        creating new work items through a team's interface.
        
        Args:
            project_name_or_id: The name or ID of the team project
            team_name_or_id: The name or ID of the team
                
        Returns:
            Formatted string containing team area path information including
            the default area path and all assigned paths, with indicators for
            paths that include sub-areas
        """
        try:
            work_client = get_work_client()
            return _get_team_area_paths_impl(
                work_client,
                project_name_or_id,
                team_name_or_id
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
    
    @mcp.tool()
    def get_team_iterations(
        project_name_or_id: str,
        team_name_or_id: str,
        current: Optional[bool] = None
    ) -> str:
        """
        Retrieves the iterations (sprints) assigned to a specific team.
        
        Use this tool when you need to:
        - View a team's sprint schedule
        - Find date ranges for iterations
        - Determine which iteration is currently active
        - Plan work based on team's iteration calendar
        
        IMPORTANT: Iterations in Azure DevOps define time periods for planning
        and tracking work. They determine sprint dates and are used for
        capacity planning, burndown charts, and velocity calculations.
        
        Args:
            project_name_or_id: The name or ID of the team project
            team_name_or_id: The name or ID of the team
            current: If True, return only the current iteration
                
        Returns:
            Formatted string containing team iteration information including
            names, date ranges, and time frames (past/current/future),
            formatted as markdown
        """
        try:
            work_client = get_work_client()
            return _get_team_iterations_impl(
                work_client,
                project_name_or_id,
                team_name_or_id,
                current
            )
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
