"""
Azure DevOps client utilities.

This module provides helper functions for connecting to Azure DevOps.
"""
import os
from typing import Optional, Tuple

from azure.devops.connection import Connection
from azure.devops.v7_1.core import CoreClient
from azure.devops.v7_1.work_item_tracking_process import (
    WorkItemTrackingProcessClient,
)
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


def get_core_client() -> CoreClient:
    """
    Get the Core client for Azure DevOps.
    
    Returns:
        CoreClient instance
        
    Raises:
        Exception: If the client cannot be created
    """
    connection = get_connection()
    
    if not connection:
        raise Exception(
            "Azure DevOps PAT or organization URL not found in "
            "environment variables."
        )
    
    core_client = connection.clients.get_core_client()
    
    if not core_client:
        raise Exception("Failed to get Core client.")
    
    return core_client


def get_work_item_tracking_process_client() -> WorkItemTrackingProcessClient:
    """
    Get the Work Item Tracking Process client for Azure DevOps.
    
    Returns:
        WorkItemTrackingProcessClient instance
        
    Raises:
        Exception: If the client cannot be created
    """
    connection = get_connection()
    
    if not connection:
        raise Exception(
            "Azure DevOps PAT or organization URL not found in "
            "environment variables."
        )
    
    process_client = connection.clients.get_work_item_tracking_process_client()
    
    if not process_client:
        raise Exception("Failed to get Work Item Tracking Process client.")
    
    return process_client
