# MCP Azure DevOps Environment Setup Script
# This script helps you set up all required environments for the MCP Azure DevOps project

# Display welcome message
Write-Host "Welcome to MCP Azure DevOps Environment Setup Script" -ForegroundColor Green
Write-Host "This script will help you set up required environments and dependencies" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Detect which Python command is available
$pythonCommand = $null
$pythonVersion = $null

# Try to detect 'python' command
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
        $pythonCommand = "python"
        Write-Host "Detected 'python' command. Using Python version: $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "Python command 'python' not found, trying alternative..." -ForegroundColor Yellow
}

# If 'python' fails, try 'py' command
if (-not $pythonCommand) {
    try {
        $pythonVersion = py --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
            $pythonCommand = "py"
            Write-Host "Detected 'py' command. Using Python version: $pythonVersion" -ForegroundColor Green
        }
    } catch {
        Write-Host "Python command 'py' not found either." -ForegroundColor Yellow
    }
}

# Exit if no Python command found
if (-not $pythonCommand) {
    Write-Host "Error: No Python command found. Please install Python 3.9+ and ensure it's in your PATH." -ForegroundColor Red
    Write-Host "You can download Python from: https://www.python.org/downloads/" -ForegroundColor Cyan
    exit
}

# Check Python version
$pythonVersionNumber = $pythonVersion -replace "Python ", ""
$versionParts = $pythonVersionNumber.Split(".")
$majorVersion = [int]$versionParts[0]
$minorVersion = [int]$versionParts[1]

if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 9)) {
    Write-Host "Warning: Python 3.9+ version is required" -ForegroundColor Yellow
    Write-Host "Please install a newer version of Python and run this script again" -ForegroundColor Yellow
    exit
}

# Install project dependencies
Write-Host "Installing project dependencies..." -ForegroundColor Cyan
& $pythonCommand -m pip install --upgrade pip
& $pythonCommand -m pip install -e ".[dev]"

# Check pipx installation
Write-Host "Checking pipx installation status..." -ForegroundColor Cyan
$pipxInstalled = $false
try {
    $pipxVersion = & $pythonCommand -m pipx --version 2>&1
    if ($pipxVersion -match "\d+\.\d+\.\d+") {
        $pipxInstalled = $true
        Write-Host "Installed pipx version: $pipxVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "pipx not found, installing..." -ForegroundColor Yellow
}

if (-not $pipxInstalled) {
    try {
        & $pythonCommand -m pip install --user pipx
        & $pythonCommand -m pipx ensurepath
        Write-Host "pipx installation successful!" -ForegroundColor Green
    } catch {
        Write-Host "Error: Failed to install pipx" -ForegroundColor Red
        exit
    }
}

# Check uv installation
Write-Host "Checking uv installation status..." -ForegroundColor Cyan
$uvInstalled = $false
try {
    $uvVersion = uv --version 2>&1
    if ($uvVersion -match "\d+\.\d+\.\d+") {
        $uvInstalled = $true
        Write-Host "Installed uv version: $uvVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "uv not found, installing..." -ForegroundColor Yellow
}

if (-not $uvInstalled) {
    try {
        & $pythonCommand -m pipx install uv
        Write-Host "uv installation successful!" -ForegroundColor Green
    } catch {
        Write-Host "Error: Failed to install uv" -ForegroundColor Red
        exit
    }
}

# Set up .env file
Write-Host "Setting up environment variables..." -ForegroundColor Cyan
$pat = Read-Host -Prompt "Please enter your Azure DevOps Personal Access Token (PAT)"
$orgUrl = Read-Host -Prompt "Please enter your Azure DevOps organization URL (e.g., https://dev.azure.com/your-organisation)"

# Check if input is valid
if ([string]::IsNullOrWhiteSpace($pat) -or [string]::IsNullOrWhiteSpace($orgUrl)) {
    Write-Host "Error: PAT and organization URL cannot be empty" -ForegroundColor Red
    exit
}

# Create .env file
$envContent = @"
AZURE_DEVOPS_PAT=$pat
AZURE_DEVOPS_ORGANIZATION_URL=$orgUrl
"@

# Ensure target directory exists
$envPath = ".\src\mcp_azure_devops\.env"
$envDir = Split-Path -Path $envPath -Parent

if (-not (Test-Path -Path $envDir)) {
    New-Item -ItemType Directory -Path $envDir -Force | Out-Null
}

Set-Content -Path $envPath -Value $envContent

Write-Host "Successfully created .env file!" -ForegroundColor Green

# Add server settings to Claude Desktop config
Write-Host "Setting up Claude Desktop..." -ForegroundColor Cyan

# Get project absolute path
$projectPath = Resolve-Path "."
$srcPath = Join-Path -Path $projectPath -ChildPath "src\mcp_azure_devops"

# Check if uv is installed
$uvPath = ""
try {
    # Try to find the uv executable path
    $uvCmd = Get-Command uv -ErrorAction SilentlyContinue
    if ($uvCmd) {
        $uvPath = $uvCmd.Path
        Write-Host "Found uv path: $uvPath" -ForegroundColor Green
    } else {
        # Try to find uv from common locations
        $possiblePaths = @(
            "C:\Python311\Scripts\uv.exe",
            "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\Scripts\uv.exe",
            "$env:LOCALAPPDATA\pipx\venvs\uv\Scripts\uv.exe"
        )
        
        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                $uvPath = $path
                Write-Host "Found uv path: $uvPath" -ForegroundColor Green
                break
            }
        }
        
        if (-not $uvPath) {
            Write-Host "Warning: Could not find uv executable. Will use default mcp command installation" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "Warning: Could not find uv executable. Will use default mcp command installation" -ForegroundColor Yellow
}

# Claude Desktop config path
$claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"

# Ensure config directory exists
$claudeConfigDir = Split-Path -Path $claudeConfigPath -Parent
if (-not (Test-Path -Path $claudeConfigDir)) {
    Write-Host "Creating Claude config directory: $claudeConfigDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
}

# Read existing config or create new config
if (Test-Path -Path $claudeConfigPath) {
    try {
        $claudeConfig = Get-Content -Path $claudeConfigPath -Raw | ConvertFrom-Json
        Write-Host "Read existing Claude Desktop config file" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to parse existing Claude Desktop config file, will create new config" -ForegroundColor Yellow
        $claudeConfig = @{
            mcpServers = @{}
        }
    }
} else {
    Write-Host "Claude Desktop config file not found, will create new config" -ForegroundColor Yellow
    $claudeConfig = @{
        mcpServers = @{}
    }
}

# Ensure mcpServers property exists
if (-not $claudeConfig.mcpServers) {
    $claudeConfig | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue @{}
}

# Create Azure DevOps Assistant config
if ($uvPath) {
    # Use found uv path
    $azureDevOpsConfig = @{
        command = $uvPath
        args = @(
            "--directory"
            $srcPath
            "run"
            "--with"
            "mcp[cli]"
            "mcp"
            "run"
            "$srcPath\server.py"
        )
    }
} else {
    # Use detected Python command
    $azureDevOpsConfig = @{
        command = "uv.exe"
        args = @(
            "--directory"
            $srcPath
            "run"
            "--with"
            "mcp[cli]"
            "mcp"
            "run"
            "$srcPath\server.py"
        )
    }
}

# Update config file
$claudeConfig.mcpServers."Azure DevOps Assistant" = $azureDevOpsConfig

# Save config file
$claudeConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $claudeConfigPath

Write-Host "Successfully updated Claude Desktop config, and added Azure DevOps Assistant" -ForegroundColor Green

# Installation complete
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Environment setup complete!" -ForegroundColor Green
Write-Host "You can now use the following command to run the server:" -ForegroundColor Green
Write-Host "Development mode (with MCP Inspector): mcp dev src/mcp_azure_devops/server.py" -ForegroundColor Cyan
Write-Host "Automatically installed in Claude Desktop, service name: 'Azure DevOps Assistant'" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Green