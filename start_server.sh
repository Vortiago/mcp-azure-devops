#!/bin/bash

# File used when I'm running the server locally during development
source .venv/bin/activate

export $(grep -v '^#' .env | xargs)

python src/mcp_azure_devops/server.py