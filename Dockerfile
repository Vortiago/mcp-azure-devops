FROM python:3.10-slim

WORKDIR /app

# Copy necessary files for installation
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install dependencies
RUN pip install -U pip && \
    pip install -e .

# Copy tests
COPY tests/ ./tests/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run MCP server
ENTRYPOINT ["python", "src/mcp_azure_devops/server.py"]