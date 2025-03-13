# MCP Azure DevOps Server - Working Guidelines

The information in this document is critical when working with this code base. Treat it as guidelines and follow it exactly.

## Commands

- Install dependencies: `uv install -e ".[dev]"`
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