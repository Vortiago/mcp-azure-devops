# Clean up Azure DevOps API documentation, keeping only version 7.2
# and maintaining only API sections relevant for an MCP server that interacts with
# Azure DevOps for pipelines, pull requests, work items, sprints, and team membership

$baseDir = "azuredevops"

Write-Output "Starting cleanup of Azure DevOps API documentation..."

# List of API sections to KEEP with reasons why they're useful
# Format: "foldername" - reason for keeping
$sectionsToKeep = @(
    "build"                     # Required for interacting with build pipelines
    "core"                      # Core API endpoints needed for basic Azure DevOps interactions
    "git"                       # Required for pull request management and Git repository operations
    "graph"                     # Provides team and user membership information
    "pipelines"                 # Required for pipeline management and execution
    "policy"                    # Useful for managing branch policies and pull request requirements
    "release"                   # Allows working with release pipelines in addition to build pipelines
    "work"                      # Required for sprint and iteration management
    "wit"                       # Required for work item tracking and management
    "notification"              # Allows setting up notifications for important events
    "favorite"                  # Enables functionality for users to favorite/bookmark important items
    "serviceEndpoint"           # Needed if connecting to external services or resources
    "distributedTask"           # Provides API access to agents and task execution
)

Write-Output "The following API sections will be kept:"
foreach ($section in $sectionsToKeep) {
    Write-Output "- $section"
}

# Process all directories in the base folder
foreach ($section in (Get-ChildItem -Path $baseDir -Directory)) {
    $sectionName = $section.Name
    $sectionPath = $section.FullName
    
    # Check if this section should be kept
    if ($sectionsToKeep -contains $sectionName) {
        Write-Output "Processing section to keep: $sectionName"
        $versionDirs = Get-ChildItem -Path $sectionPath -Directory
        $has72 = $false
        
        # Check if there's a version 7.2 directory
        foreach ($versionDir in $versionDirs) {
            if ($versionDir.Name -eq "7.2") {
                $has72 = $true
                break
            }
        }
        
        if ($has72) {
            # Delete all version directories except 7.2
            Write-Output "  Keeping version 7.2 for $sectionName"
            foreach ($versionDir in $versionDirs) {
                if ($versionDir.Name -ne "7.2") {
                    Write-Output "    Deleting version $($versionDir.Name)"
                    Remove-Item -Path $versionDir.FullName -Recurse -Force
                }
            }
        } else {
            Write-Output "  WARNING: No version 7.2 found for $sectionName, but keeping older versions as reference"
        }
    } else {
        # Delete entire section as it's not in our keep list
        Write-Output "Deleting unnecessary section: $sectionName"
        Remove-Item -Path $sectionPath -Recurse -Force
    }
}

Write-Output "Clean-up completed. Only relevant API sections remain, mostly with version 7.2 documentation."