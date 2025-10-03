#!/bin/bash
# filepath: setup_environment.sh
# MCP Azure DevOps Environment Setup Script
# This script helps you set up all required environments for the MCP Azure DevOps project

# Display welcome message
echo -e "\033[0;32mWelcome to MCP Azure DevOps Environment Setup Script\033[0m"
echo -e "\033[0;32mThis script will help you set up required environments and dependencies\033[0m"
echo -e "\033[0;32m===============================================\033[0m"

# Detect which Python command is available
pythonCommand=null
pythonVersion=null

# Try to detect 'python3' command
if command -v python3 &> /dev/null; then
    pythonCommand="python3"
    pythonVersion=$(python3 --version)
    echo -e "\033[0;32mDetected 'python3' command. Using Python version: $pythonVersion\033[0m"
# If 'python3' fails, try 'python' command
elif command -v python &> /dev/null; then
    pythonCommand="python"
    pythonVersion=$(python --version)
    echo -e "\033[0;32mDetected 'python' command. Using Python version: $pythonVersion\033[0m"
else
    echo -e "\033[0;33mPython command not found\033[0m"
fi

# Exit if no Python command found
if [ "$pythonCommand" = "null" ]; then
    echo -e "\033[0;31mError: No Python command found. Please install Python 3.9+ and ensure it's in your PATH.\033[0m"
    echo -e "\033[0;36mYou can download Python from: https://www.python.org/downloads/\033[0m"
    exit 1
fi

# Check Python version
pythonVersionNumber=$(echo $pythonVersion | sed 's/Python //')
majorVersion=$(echo $pythonVersionNumber | cut -d. -f1)
minorVersion=$(echo $pythonVersionNumber | cut -d. -f2)

if [ $majorVersion -lt 3 ] || ([ $majorVersion -eq 3 ] && [ $minorVersion -lt 9 ]); then
    echo -e "\033[0;33mWarning: Python 3.9+ version is required\033[0m"
    echo -e "\033[0;33mPlease install a newer version of Python and run this script again\033[0m"
    exit 1
fi

# Install project dependencies
echo -e "\033[0;36mInstalling project dependencies...\033[0m"
$pythonCommand -m pip install --upgrade pip
$pythonCommand -m pip install -e ".[dev]"

# Check pipx installation
echo -e "\033[0;36mChecking pipx installation status...\033[0m"
pipxInstalled=false
if command -v pipx &> /dev/null; then
    pipxInstalled=true
    pipxVersion=$(pipx --version)
    echo -e "\033[0;32mInstalled pipx version: $pipxVersion\033[0m"
else
    echo -e "\033[0;33mpipx not found, installing...\033[0m"
fi

if [ "$pipxInstalled" = "false" ]; then
    $pythonCommand -m pip install --user pipx
    $pythonCommand -m pipx ensurepath
    echo -e "\033[0;32mpipx installation successful!\033[0m"
fi

# Check uv installation
echo -e "\033[0;36mChecking uv installation status...\033[0m"
uvInstalled=false
if command -v uv &> /dev/null; then
    uvInstalled=true
    uvVersion=$(uv --version)
    echo -e "\033[0;32mInstalled uv version: $uvVersion\033[0m"
else
    echo -e "\033[0;33muv not found, installing...\033[0m"
fi

if [ "$uvInstalled" = "false" ]; then
    $pythonCommand -m pipx install uv
    echo -e "\033[0;32muv installation successful!\033[0m"
fi

# Set up .env file
echo -e "\033[0;36mSetting up environment variables...\033[0m"
read -p "Please enter your Azure DevOps Personal Access Token (PAT): " pat
read -p "Please enter your Azure DevOps organization URL (e.g., https://dev.azure.com/your-organisation): " orgUrl

# Check if input is valid
if [ -z "$pat" ] || [ -z "$orgUrl" ]; then
    echo -e "\033[0;31mError: PAT and organization URL cannot be empty\033[0m"
    exit 1
fi

# Create .env file
envContent="AZURE_DEVOPS_PAT=$pat
AZURE_DEVOPS_ORGANIZATION_URL=$orgUrl"

# Ensure target directory exists
envPath="./src/mcp_azure_devops/.env"
envDir=$(dirname "$envPath")

mkdir -p "$envDir"
echo "$envContent" > "$envPath"

echo -e "\033[0;32mSuccessfully created .env file!\033[0m"

# Add server settings to Claude Desktop config
echo -e "\033[0;36mSetting up Claude Desktop...\033[0m"

# Get project absolute path
projectPath=$(pwd)
srcPath="$projectPath/src/mcp_azure_devops"

# Check if uv is installed
uvPath=""
if command -v uv &> /dev/null; then
    uvPath=$(which uv)
    echo -e "\033[0;32mFound uv path: $uvPath\033[0m"
else
    echo -e "\033[0;33mWarning: Could not find uv executable. Will use default mcp command installation\033[0m"
fi

# Claude Desktop config path (Mac)
claudeConfigPath="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Ensure config directory exists
claudeConfigDir=$(dirname "$claudeConfigPath")
mkdir -p "$claudeConfigDir"

# Read existing config or create new config
if [ -f "$claudeConfigPath" ]; then
    if ! claudeConfig=$(cat "$claudeConfigPath"); then
        echo -e "\033[0;33mWarning: Failed to parse existing Claude Desktop config file, will create new config\033[0m"
        claudeConfig='{"mcpServers":{}}'
    else
        echo -e "\033[0;32mRead existing Claude Desktop config file\033[0m"
    fi
else
    echo -e "\033[0;33mClaude Desktop config file not found, will create new config\033[0m"
    claudeConfig='{"mcpServers":{}}'
fi

# Create Azure DevOps Assistant config
if [ -n "$uvPath" ]; then
    # Use found uv path
    azureDevOpsConfig='{
        "command": "'$uvPath'",
        "args": [
            "--directory",
            "'$srcPath'",
            "run",
            "--with",
            "mcp[cli]",
            "mcp",
            "run",
            "'$srcPath'/server.py"
        ]
    }'
else
    # Use detected Python command
    azureDevOpsConfig='{
        "command": "uv",
        "args": [
            "--directory",
            "'$srcPath'",
            "run",
            "--with",
            "mcp[cli]",
            "mcp",
            "run",
            "'$srcPath'/server.py"
        ]
    }'
fi

# Update config file (using temporary file for simple JSON modification)
tempConfig=$(mktemp)
echo "$claudeConfig" | python3 -c "
import json, sys
config = json.load(sys.stdin)
if 'mcpServers' not in config:
    config['mcpServers'] = {}
config['mcpServers']['Azure DevOps Assistant'] = json.loads('$azureDevOpsConfig')
json.dump(config, sys.stdout, indent=4)
" > "$tempConfig"

# Save config file
cp "$tempConfig" "$claudeConfigPath"
rm "$tempConfig"

echo -e "\033[0;32mSuccessfully updated Claude Desktop config, and added Azure DevOps Assistant\033[0m"

# Installation complete
echo -e "\033[0;32m===============================================\033[0m"
echo -e "\033[0;32mEnvironment setup complete!\033[0m"
echo -e "\033[0;32mYou can now use the following command to run the server:\033[0m"
echo -e "\033[0;36mDevelopment mode (with MCP Inspector): mcp dev src/mcp_azure_devops/server.py\033[0m"
echo -e "\033[0;36mAutomatically installed in Claude Desktop, service name: 'Azure DevOps Assistant'\033[0m"
echo -e "\033[0;32m===============================================\033[0m"
