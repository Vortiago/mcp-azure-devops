"""
Azure DevOps client utilities.

This module provides helper functions for connecting to Azure DevOps.
"""
import os
from typing import Optional, Tuple

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get Azure DevOps credentials from environment variables.
    
    Returns:
        Tuple containing (pat, organization_url)
    """
    pat = os.environ.get("AZURE_DEVOPS_PAT")
    organization_url = os.environ.get("AZURE_DEVOPS_ORGANIZATION_URL")
    return pat, organization_url


def get_connection() -> Optional[Connection]:
    """
    Create a connection to Azure DevOps.
    
    Returns:
        Connection object or None if credentials are missing
    """
    pat, organization_url = get_credentials()
    
    if not pat or not organization_url:
        return None
    
    credentials = BasicAuthentication('', pat)
    return Connection(base_url=organization_url, creds=credentials)
