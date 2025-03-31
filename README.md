# MCP Azure DevOps Server

A Model Context Protocol (MCP) server enabling AI assistants to interact with Azure DevOps services.

## Overview

This project implements a Model Context Protocol (MCP) server that allows AI assistants (like Claude) to interact with Azure DevOps, providing a bridge between natural language interactions and the Azure DevOps REST API.

## Features

Currently implemented:

### Work Item Management
- **Query Work Items**: Search for work items using WIQL queries
- **Get Work Item Details**: View complete work item information
- **Create Work Items**: Add new tasks, bugs, user stories, and other work item types
- **Update Work Items**: Modify existing work items' fields and properties
- **Add Comments**: Post comments on work items
- **View Comments**: Retrieve the comment history for a work item
- **Parent-Child Relationships**: Establish hierarchy between work items

### Project Management
- **Get Projects**: View all accessible projects in the organization
- **Get Teams**: List all teams within the organization
- **Team Members**: View team membership information
- **Team Area Paths**: Retrieve area paths assigned to teams
- **Team Iterations**: Access team iteration/sprint configurations

Planned features:
- **Pipeline Operations**: Query pipeline status and trigger new pipeline runs
- **Pull Request Handling**: Create, update, and review Pull Requests
- **Sprint Management**: Plan and manage sprints and iterations
- **Branch Policy Administration**: Configure and manage branch policies

## Getting Started

### Prerequisites

- Python 3.10+
- Azure DevOps account with appropriate permissions
- Personal Access Token (PAT) with necessary scopes for Azure DevOps API access

### Installation

```bash
# Clone the repository
git clone https://github.com/Vortiago/mcp-azure-devops.git
cd mcp-azure-devops

# Install in development mode
uv pip install -e ".[dev]"

# Install from PyPi
pip install mcp-azure-devops
```

### Configuration

Create a `.env` file in the project root with the following variables:

```
AZURE_DEVOPS_PAT=your_personal_access_token
AZURE_DEVOPS_ORGANIZATION_URL=https://your-organization.visualstudio.com or https://dev.azure.com/your-organisation
```

Note: Make sure to provide the full URL to your Azure DevOps organization.

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

### Create a Work Item

```
Create a user story in the ProjectX with the title "Implement user authentication" and assign it to john.doe@example.com
```

### Update a Work Item

```
Change the status of bug #1234 to "Resolved" and add a comment explaining the fix
```

### Team Management

```
Show me all the team members in the "Core Development" team in the "ProjectX" project
```

### View Project Structure

```
List all projects in my organization and show me the iterations for the Development team
```

## Development

The project is structured into feature modules, each implementing specific Azure DevOps capabilities:

- `features/work_items`: Work item management functionality
- `features/projects`: Project management capabilities
- `features/teams`: Team management features
- `utils`: Common utilities and client initialization

For more information on development, see the [CLAUDE.md](CLAUDE.md) file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [Azure DevOps Python API](https://github.com/microsoft/azure-devops-python-api)
