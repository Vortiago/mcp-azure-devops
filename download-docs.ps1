<#
.SYNOPSIS
    Downloads external documentation from predefined URLs into the docs/external directory.

.DESCRIPTION
    This script downloads content from a list of URLs and saves them to the docs/external directory.
    It's designed to help download reference documentation that can be used as context for LLMs.
#>

# Define the array of documentation URLs to download with categories
$docsUrls = @(
    @{Url = "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/README.md"; Category = "mcp-sdk" },
    @{Url = "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/examples/fastmcp/simple_echo.py"; Category = "mcp-sdk" },
    @{Url = "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/examples/fastmcp/readme-quickstart.py"; Category = "mcp-sdk" },
    @{Url = "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/examples/fastmcp/complex_inputs.py"; Category = "mcp-sdk" },
    @{Url = "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/examples/fastmcp/text_me.py"; Category = "mcp-sdk" },
    @{Url = "https://raw.githubusercontent.com/microsoft/azure-devops-python-api/refs/heads/dev/README.md"; Category = "azdo-sdk" }
    # Add more URLs as needed
)

# Ensure docs/external directory exists
$externalDocsDir = Join-Path (Get-Location) "docs/external"
if (-not (Test-Path $externalDocsDir -PathType Container)) {
    Write-Host "Creating docs/external directory..."
    New-Item -Path $externalDocsDir -ItemType Directory | Out-Null
}

# Function to derive a filename from a URL
function Get-FilenameFromUrl {
    param([string]$Url)
    
    $uri = [System.Uri]$Url
    $filename = $uri.Segments[-1]
    
    # If filename is empty or just a slash, use the host plus path
    if ([string]::IsNullOrEmpty($filename) -or $filename -eq "/") {
        $filename = ($uri.Host -replace "[\.\:]", "-") + "-" + ($uri.AbsolutePath -replace "[\/\\\?\:]", "-") + ".html"
    }
    
    # Clean up filename
    $filename = $filename -replace "[^\w\d\.-]", "-"
    
    return $filename
}

# Download each URL
foreach ($item in $docsUrls) {
    $url = $item.Url
    $category = $item.Category
    $filename = Get-FilenameFromUrl -Url $url
    
    # Create category subdirectory if needed
    $categoryDir = Join-Path $externalDocsDir $category
    if (-not (Test-Path $categoryDir -PathType Container)) {
        Write-Host "Creating category directory: $category"
        New-Item -Path $categoryDir -ItemType Directory | Out-Null
    }
    
    $outPath = Join-Path $categoryDir $filename
    
    Write-Host "Downloading: $url"
    Write-Host "Category: $category"
    Write-Host "Saving to: $outPath"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $outPath
        Write-Host "Download successful" -ForegroundColor Green
    } catch {
        Write-Host "Error downloading $url : $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "All downloads completed." -ForegroundColor Green

Write-Host "Running Repomix on external repositories"

repomix --remote https://github.com/microsoft/azure-devops-python-api/ --compress -o docs/external/azdo-sdk/repomix-summary-devopssdk.xml --include "azure-devops/azure/devops/v7_1/**"
repomix --remote https://github.com/modelcontextprotocol/servers --compress -o "docs/external/mcp-sdk/repomix-summary-mcpserverexamples.xml" --include "src/sentry/**,src/fetch/**" --ignore "**/*.lock,**/Dockerfile,**/LICENSE"