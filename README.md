# MCP Azure DevOps Server

A Model Context Protocol (MCP) server enabling AI assistants to interact with Azure DevOps services.

## Overview

This project implements a Model Context Protocol (MCP) server that allows AI assistants (like Claude) to interact with Azure DevOps, providing a bridge between natural language interactions and the Azure DevOps REST API.

## Features

Currently implemented:
- **Work Item Management**: Query work items using WIQL

Planned features:
- **Work Item Management**: Create and update work items
- **Pipeline Operations**: Query pipeline status and trigger new pipeline runs
- **Pull Request Handling**: Create, update, and review Pull Requests
- **Sprint Management**: Plan and manage sprints and iterations
- **Branch Policy Administration**: Configure and manage branch policies

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

# Install from PyPi
pip install mcp_azure_devops
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

### Create a Pull Request (Coming Soon)

```
Create a pull request from feature/new-login-page to main with the title "Implement new login page"
```

### Check Pipeline Status (Coming Soon)

```
What's the status of the latest build for the main branch?
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [Azure DevOps Python API](https://github.com/microsoft/azure-devops-python-api)
