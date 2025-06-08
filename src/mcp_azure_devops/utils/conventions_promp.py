from mcp.server.fastmcp import FastMCP


def register_prompt(mcp: FastMCP) -> None:
    
    @mcp.prompt(name="create_conventions_file", 
                description="Create a starting conventions file Azure DevOps")
    def create_conventions_file() -> str:
        """
        Create a starting conventions file for Azure DevOps.
        
        Use this prompt when you need to:
        - Generate a conventions file for Azure DevOps
        - Get a template for project conventions
        - Start defining project standards and guidelines
        
        Returns:
            A formatted conventions file template
        """
        
        
        return """Create a concise Azure DevOps conventions file to 
    serve as a quick reference for our environment. 
    This should capture all important patterns and structures 
    while remaining compact enough for an LLM context.

Using the available Azure DevOps tools, please:

1. Get an overview of ALL projects (get_projects)
2. For ALL projects:
   - Identify teams (get_all_teams)
   - Get area paths and iterations for each team 
   (get_team_area_paths, get_team_iterations)
3. Capture work item configuration for EACH project:
   - Process ID and details (get_project_process_id, get_process_details)
   - Work item types (get_work_item_types)
   - For each work item type, get ALL fields 
   (get_work_item_type_fields) and clearly identify mandatory fields
   - Note differences in processes between projects

Create a concise markdown document with these sections:

1. **Projects and Teams**: 
    List of all projects and their teams
2. **Work Item Types by Process**: 
    Work item types grouped by process template, 
    including ALL fields for each type with mandatory fields clearly marked
3. **Classification Structure**: 
    Area paths and iterations for each team, 
    with team-specific structures and patterns
4. **Naming Conventions**: 
    Observed naming patterns across projects, teams, and items

Focus on identifying and documenting patterns and 
variations between projects. 
When listing field names or other details, prioritize the most important ones.
The goal is to create a reference that captures key conventions 
while staying concise."""
    