"""
Common utilities for Azure DevOps teams features.

This module provides shared functionality used by both tools and resources.
"""
# We can reuse the core client from projects/common.py
from mcp_azure_devops.features.projects.common import get_core_client, AzureDevOpsClientError

# Export these for use in tools.py
__all__ = ['get_core_client', 'AzureDevOpsClientError']
