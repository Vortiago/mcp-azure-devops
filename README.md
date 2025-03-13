# MCP Azure DevOps Server

A Model Context Protocol (MCP) server enabling AI assistants to interact with Azure DevOps services.

## Overview

This project implements a Model Context Protocol (MCP) server that allows AI assistants (like Claude) to interact with Azure DevOps, providing a bridge between natural language interactions and the Azure DevOps REST API.

## Features

- **Work Item Management**: Create, update, and query work items
- **Pipeline Operations**: Query pipeline status and trigger new pipeline runs
- **Pull Request Handling**: Create, update, and review Pull Requests
- **Sprint Management**: Plan and manage sprints and iterations
- **Branch Policy Administration**: Configure and manage branch policies
- **Team Management**: Work with teams and project structures

## How It Works

This MCP server is built using:

1. **MCP Python SDK**: Provides the framework for creating a Model Context Protocol server
2. **Azure DevOps Python API**: Handles all interactions with Azure DevOps services

The server exposes Azure DevOps functionality through:

- **Resources**: Provide data like work item details, PR information, pipeline status
- **Tools**: Allow execution of actions like creating work items or triggering pipelines
- **Prompts**: Guide interactions with specific Azure DevOps workflows

## Project Structure

The project follows a modern Python package structure with a `src` layout:

```
mcp-azure-devops/
├── src/
│   └── mcp_azure_devops/
│       ├── __init__.py
│       ├── server.py
│       ├── resources/
│       │   ├── __init__.py
│       │   ├── work_items.py
│       │   ├── pipelines.py
│       │   └── pull_requests.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── work_item_tools.py
│       │   ├── pipeline_tools.py
│       │   └── pr_tools.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── azure_devops.py
│       └── utils/
│           ├── __init__.py
│           └── api_helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_work_items.py
│   └── test_pipelines.py
├── docs/
├── README.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.9+
- Azure DevOps account with appropriate permissions
- Personal Access Token (PAT) with necessary scopes for Azure DevOps API access

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/mcp-azure-devops.git
cd mcp-azure-devops

# Install in development mode
pip install -e ".[dev]"
```

### Configuration

Create a `.env` file in the project root with the following variables:

```
AZURE_DEVOPS_PAT=your_personal_access_token
AZURE_DEVOPS_ORGANIZATION=your_organization_name
```

### Running the Server

```bash
# Development mode with the MCP Inspector
mcp dev src/mcp_azure_devops/server.py

# Install in Claude Desktop
mcp install src/mcp_azure_devops/server.py --name "Azure DevOps Assistant"
```

## Usage Examples

### Query Work Items

```
Show me all active bugs assigned to me in the current sprint
```

### Create a Pull Request

```
Create a pull request from feature/new-login-page to main with the title "Implement new login page"
```

### Check Pipeline Status

```
What's the status of the latest build for the main branch?
```

## Understanding Azure DevOps Resources

In the context of this project, "Azure DevOps resources" refers to two things:

1. **Azure DevOps Entities**: The various objects and data structures within Azure DevOps that this server interacts with:
   - Work items (bugs, tasks, user stories, epics)
   - Repositories and branches
   - Pull requests and code reviews
   - Build and release pipelines
   - Project and team configurations
   - Test plans and test results
   - Dashboards and reports

2. **MCP Resources**: In the Model Context Protocol, resources are data providers (similar to GET endpoints in a REST API). The `resources/` module in this project implements MCP resources that fetch data from Azure DevOps and make it available to AI assistants in their context window.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [Azure DevOps Python API](https://github.com/microsoft/azure-devops-python-api)
