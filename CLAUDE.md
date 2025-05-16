# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

## 3. Development Commands

### Setup and Installation
```bash
# Install in development mode with all dev dependencies
uv pip install -e ".[dev]"

# Create a virtual environment (alternative)
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running the Server
```bash
# Run the server in development mode with inspector
mcp dev src/mcp_azure_devops/server.py

# Install in Claude Desktop
mcp install src/mcp_azure_devops/server.py --name "Azure DevOps Assistant"

# Run via the start script (loads env vars)
./start_server.sh
```

### Testing
```bash
# Run all tests
uv run pytest tests/

# Run a specific test file
uv run pytest tests/features/work_items/test_tools.py

# Run a specific test
uv run pytest tests/features/work_items/test_tools.py::test_query_work_items_impl_with_results
```

### Code Quality
```bash
# Format code with ruff
uv run ruff format .

# Run linter
uv run ruff check .

# Run type checking
uv run pyright
```

## 4. Core Concepts

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

## 5. Implementation Guidelines

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

## 6. Common Code Patterns

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

## 7. Testing Guidelines

### Mocking Azure DevOps API

The codebase uses unittest.mock to mock Azure DevOps API responses:

```python
from unittest.mock import MagicMock
from azure.devops.v7_1.work_item_tracking.models import WorkItem

# Create mock client
mock_client = MagicMock()

# Create mock response objects
mock_work_item = MagicMock(spec=WorkItem)
mock_work_item.id = 123
mock_work_item.fields = {
    "System.WorkItemType": "Bug",
    "System.Title": "Test Bug"
}

# Set return value for client method
mock_client.get_work_item.return_value = mock_work_item

# Test implementation function
result = _get_work_item_impl(123, mock_client)

# Verify results
assert "# Work Item 123" in result
assert "- **System.WorkItemType**: Bug" in result
```

### Test Function Pattern

Tests should cover both success and error cases:

```python
def test_get_data_success():
    """Test successful data retrieval."""
    # Setup mocks
    # Execute implementation
    # Assert results

def test_get_data_error():
    """Test error handling in data retrieval."""
    # Setup mock to raise exception
    # Execute implementation
    # Assert error message in result
```

## 8. Adding New Features

To add a new feature:

1. Create a new directory under `features/` with the appropriate structure
2. Implement feature-specific client initialization in `common.py`
3. Create tools in `tools.py` or a `tools/` directory with specific operations
4. Register the feature with the server by updating `features/__init__.py`
5. Write tests for the new feature in the `tests/` directory

## 9. Technical Requirements

### Code Style
- PEP 8 conventions
- Type hints for all functions
- Google-style docstrings
- Small, focused functions
- Line length: 79 characters
- Import sorting: standard library → third-party → local