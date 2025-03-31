# MCP Azure DevOps Server Guide

This guide helps AI assistants implement and modify the MCP Azure DevOps server codebase effectively.

## 1. Purpose & Overview

This MCP server enables AI assistants to interact with Azure DevOps by:
- Connecting to Azure DevOps services via REST API and Python SDK
- Exposing Azure DevOps data (work items, repositories, pipelines, PRs)
- Providing tools to create and modify Azure DevOps objects
- Including prompts for common workflows
- Using PAT authentication for secure interactions

## 2. Project Structure

```
mcp-azure-devops/
├── docs/                      # API documentation
├── src/                       # Source code
│   └── mcp_azure_devops/      # Main package
│       ├── features/          # Feature modules
│       │   ├── projects/      # Project management features
│       │   ├── teams/         # Team management features 
│       │   └── work_items/    # Work item management features
│       │       ├── tools/     # Work item operation tools
│       │       ├── common.py  # Common utilities for work items
│       │       └── formatting.py # Formatting helpers
│       ├── utils/             # Shared utilities
│       ├── __init__.py        # Package initialization
│       └── server.py          # Main MCP server
├── tests/                     # Test suite
├── .env                       # Environment variables (not in repo)
├── CLAUDE.md                  # AI assistant guide
├── LICENSE                    # MIT License
├── pyproject.toml             # Project configuration
├── README.md                  # Project documentation
└── uv.lock                    # Package dependency locks
```

## 3. Core Concepts

### Azure DevOps & MCP Integration

This project bridges two systems:

1. **Azure DevOps Objects**:
   - Work items (bugs, tasks, user stories, epics)
   - Repositories and branches
   - Pull requests and code reviews
   - Pipelines (build and release)
   - Projects and teams

2. **MCP Components**:
   - **Tools**: Action performers that modify data (like POST/PUT/DELETE endpoints)
   - **Prompts**: Templates for guiding interactions

### Authentication

The project requires these environment variables:
- `AZURE_DEVOPS_PAT`: Personal Access Token with appropriate permissions
- `AZURE_DEVOPS_ORGANIZATION_URL`: The full URL to your Azure DevOps organization

## 4. Implementation Guidelines

### Feature Structure

Each feature in the `features/` directory follows this pattern:
- `__init__.py`: Contains `register()` function to add the feature to the MCP server
- `common.py`: Shared utilities, exceptions, and helper functions
- `tools.py` or `tools/`: Functions or classes for operations (GET, POST, PUT, DELETE)

### Tool Implementation Pattern

When implementing a new tool:

1. Define a private implementation function with `_name_impl` that takes explicit client objects:
```python
def _get_data_impl(client, param1, param2):
    # Implementation
    return formatted_result
```

2. Create a public MCP tool function that handles client initialization and error handling:
```python
@mcp.tool()
def get_data(param1, param2):
    """
    Docstring following the standard pattern.
    
    Use this tool when you need to:
    - First use case
    - Second use case
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of the return value format
    """
    try:
        client = get_client()
        return _get_data_impl(client, param1, param2)
    except AzureDevOpsClientError as e:
        return f"Error: {str(e)}"
```

3. Register the tool in the feature's `__init__.py` or `register_tools()` function

### Function Docstring Pattern

All public tools must have detailed docstrings following this pattern:

```python
"""
Brief description of what the tool does.

Use this tool when you need to:
- First use case with specific example
- Second use case with specific example
- Third use case with specific example

IMPORTANT: Any special considerations or warnings.

Args:
    param1: Description of first parameter
    param2: Description of second parameter
    
Returns:
    Detailed description of what is returned and in what format
"""
```

### Error Handling

The standard error handling pattern is:

```python
try:
    # Implementation code
except AzureDevOpsClientError as e:
    return f"Error: {str(e)}"
except Exception as e:
    return f"Error doing operation: {str(e)}"
```

For specific errors, create custom exception classes in the feature's `common.py` file.

## 5. Common Code Patterns

### Client Initialization

```python
from mcp_azure_devops.utils.azure_client import get_connection

def get_work_item_client():
    """Get the Work Item Tracking client."""
    try:
        connection = get_connection()
        return connection.clients.get_work_item_tracking_client()
    except Exception as e:
        raise AzureDevOpsClientError(f"Failed to get Work Item client: {str(e)}")
```

### Response Formatting

```python
def format_result(data):
    """Format data for response."""
    formatted_info = [f"# {data.name}"]
    
    # Add additional fields with null checks
    if hasattr(data, "description") and data.description:
        formatted_info.append(f"Description: {data.description}")
    
    return "\n".join(formatted_info)
```


## 6. Adding New Features

To add a new feature:

1. Create a new directory under `features/` with the appropriate structure
2. Implement feature-specific client initialization in `common.py`
3. Create tools in `tools.py` or a `tools/` directory with specific operations
4. Register the feature with the server by updating `features/__init__.py`
5. Write tests for the new feature in the `tests/` directory

## 7. Technical Requirements

### Code Style
- PEP 8 conventions
- Type hints for all functions
- Google-style docstrings
- Small, focused functions
- Line length: 79 characters
- Import sorting: standard library → third-party → local

### Development Tools
- Install: `uv pip install -e ".[dev]"`
- Run server: `mcp dev src/mcp_azure_devops/server.py`
- Run tests: `uv run pytest tests/`
- Format: `uv run ruff format .`
- Type check: `uv run pyright`

### Testing
- Write tests for all new functionality
- Test both successful and error cases
- Mock Azure DevOps API responses for deterministic testing
- Place tests in the `tests/` directory with corresponding structure

## 8. Examples

### Example: Creating a New Tool

```python
# In src/mcp_azure_devops/features/repositories/tools.py

def _list_repositories_impl(git_client, project):
    """Implementation of listing repositories."""
    repos = git_client.get_repositories(project=project)
    
    if not repos:
        return f"No repositories found in project {project}."
    
    formatted_repos = []
    for repo in repos:
        formatted_repos.append(_format_repository(repo))
    
    return "\n\n".join(formatted_repos)

def register_tools(mcp):
    """Register repository tools with the MCP server."""
    
    @mcp.tool()
    def list_repositories(project):
        """
        Lists all Git repositories in a project.
        
        Use this tool when you need to:
        - View all repositories in a project
        - Find a specific repository by name
        - Get repository IDs for use in other operations
        
        Args:
            project: Project name or ID
            
        Returns:
            Formatted string listing all repositories with names, IDs, and URLs
        """
        try:
            git_client = get_git_client()
            return _list_repositories_impl(git_client, project)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
```

### Example: Registering a New Feature

```python
# In src/mcp_azure_devops/features/repositories/__init__.py

from mcp_azure_devops.features.repositories import tools

def register(mcp):
    """Register repository components with the MCP server."""
    tools.register_tools(mcp)

# In src/mcp_azure_devops/features/__init__.py

from mcp_azure_devops.features import projects, teams, work_items, repositories

def register_all(mcp):
    """Register all features with the MCP server."""
    work_items.register(mcp)
    projects.register(mcp)
    teams.register(mcp)
    repositories.register(mcp)  # Add the new feature
```
