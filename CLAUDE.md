# MCP Azure DevOps Server - Working Guidelines

The information in this document is critical when working with this code base. Treat it as guidelines and follow it exactly.

## Commands

- Install dependencies: `uv pip install -e ".[dev]"`
- Development server: `mcp dev src/mcp_azure_devops/server.py`
- Run tests: `uv run pytest tests/`
- Run single test: `uv run pytest tests/test_file.py::test_function`

## Code Style

- Follow PEP 8 conventions for Python code
- Use type hints for all function parameters and return values
- Import ordering: standard library, third-party packages, local modules
- Class/function naming: CamelCase for classes, snake_case for functions/variables
- Use descriptive variable names that reflect purpose
- Document functions with docstrings (Google style preferred)
- Error handling: use try/except with specific exceptions
- Prefer async/await for I/O operations with Azure DevOps API
- Keep functions small and focused on a single responsibility

## Development Principles

- Functions must be focused and small
- Follow existing patterns exactly
- Use Clean Code patterns where no existing pattern exists
- Async testing: use anyio, not asyncio
- Test coverage: include edge cases and error conditions
- New features require tests
- Bug fixes require regression tests

## Code Formatting

- Tool: ruff
- Format: `uv run ruff format .`
- Check: `uv run ruff check .`
- Fix: `uv run ruff check . --fix`
- Critical issues:
  - Line length (79 chars)
  - Import sorting (I001)
  - Unused imports
- Line wrapping:
  - Strings: use parentheses
  - Function calls: multi-line with proper indent
  - Imports: split into multiple lines

## Type Checking

- Tool: `uv run pyright`
- Requirements:
  - Explicit None checks for Optional
  - Type narrowing for strings
  - Version warnings can be ignored if checks pass

## Local API Reference Files

The repository contains a comprehensive set of JSON files that document Azure DevOps REST API endpoints with examples. These are located in the `docs/azuredevops-restapi/` directory and organized by service area.
It also contains SDK documentation for the Python SDK that is the primary method of accessing azure devops.

- **File structure and naming**:
  - Files are organized by service (git, core, work, etc.) and API version folders
  - HTTP verb is included in the filename (e.g., `GET__git_repositories.json`, `POST__git_repositories.json`)
  - Paths reflect the actual API endpoint structure

- **File contents**:
  - Each file contains a complete example of a REST API request and response
  - The `x-ms-vss-request-method` property indicates the HTTP method
  - The `x-ms-vss-request-url` property shows the complete endpoint URL
  - The `parameters` section lists required query parameters
  - The `responses` section contains example response bodies with status codes

- **How to use these files**:
  - Examine these files to understand the expected request/response format
  - Use them to create models for request and response objects
  - Reference for parameter requirements and validation
  - Use as templates for mocking API responses in tests
  - Follow the patterns shown in these files when implementing new endpoints

- **When implementing a new endpoint**:
  1. Find the corresponding JSON file in the docs directory
  2. Review the request format, parameters, and URL structure
  3. Use the Azure DevOps Python SDK for interacting with Azure DevOps.
  
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
  