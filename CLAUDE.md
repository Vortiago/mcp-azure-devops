# MCP Azure DevOps Server Guide

This guide helps Claude implement and modify the MCP Azure DevOps server codebase effectively.

## 1. Purpose & Overview

This MCP server enables AI assistants to interact with Azure DevOps by:
- Connecting to Azure DevOps services via REST API and Python SDK
- Exposing Azure DevOps data (work items, repositories, pipelines, PRs)
- Providing tools to create and modify Azure DevOps objects
- Including prompts for common workflows
- Using PAT authentication for secure interactions

## 2. Core Concepts

### Azure DevOps & MCP Integration

This project bridges two systems:

1. **Azure DevOps Objects**:
   - Work items (bugs, tasks, user stories, epics)
   - Repositories and branches
   - Pull requests and code reviews
   - Pipelines (build and release)
   - Projects and teams

2. **MCP Components**:
   - **Resources**: Read-only data providers (like GET endpoints)
   - **Tools**: Action performers that modify data (like POST/PUT/DELETE endpoints)
   - **Prompts**: Templates for guiding interactions

## 3. Implementation Guidelines

### Resources Implementation
- Create resource classes for each Azure DevOps entity type
- Provide read-only access to Azure DevOps data
- Follow existing patterns in `resources/` directory
- Example implementations: `WorkItemResource`, `PipelineResource`

### Tools Implementation
- Create tool classes for actions that modify Azure DevOps objects
- Each tool should have a single responsibility
- Handle authentication and errors properly
- Example implementations: `CreateWorkItemTool`, `TriggerPipelineTool`

### Prompts Implementation
- Create prompts for guiding complex workflows
- Focus on tasks that benefit from AI assistance
- Structure to collect necessary information before action

### Development Workflow
1. Find relevant Azure DevOps API documentation in `docs/` directory
2. Review request format, parameters, and URL structure
3. Use Azure DevOps Python SDK for implementation
4. Write tests for your implementation
5. Follow existing patterns and code style

## 4. Technical Requirements

### Code Style
- PEP 8 conventions
- Type hints for all functions
- Google-style docstrings
- Async/await for I/O operations
- Small, focused functions

### Development Tools
- Install: `uv pip install -e ".[dev]"`
- Run server: `mcp dev src/mcp_azure_devops/server.py`
- Run tests: `uv run pytest tests/`
- Format: `uv run ruff format .`
- Type check: `uv run pyright`

### Critical Requirements
- Line length: 79 characters
- Import sorting: standard library → third-party → local
- Proper error handling with specific exceptions
- Test coverage for edge cases
- New features require tests