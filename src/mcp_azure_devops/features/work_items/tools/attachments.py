"""
Attachment operations for Azure DevOps work items.

This module provides MCP tools for uploading and attaching files to work items.
"""
import os
from io import BytesIO
from typing import Optional, Tuple

from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)
from mcp_azure_devops.features.work_items.formatting import format_work_item


def _upload_attachment_impl(
    file_path: str,
    wit_client: WorkItemTrackingClient,
    project: Optional[str] = None
) -> Tuple[str, str]:
    """
    Upload a file attachment to Azure DevOps.

    Args:
        file_path: Local file path
        wit_client: Work item tracking client
        project: Optional project name
            
    Returns:
        Tuple[str, str]: (attachment URL, attachment name)
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get the file name
        file_name = os.path.basename(file_path)
        
        # Read file contents as bytes
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        # Create a BytesIO stream
        upload_stream = BytesIO(file_content)
        
        # Upload the attachment
        attachment = wit_client.create_attachment(
            upload_stream=upload_stream,
            file_name=file_name,
            project=project
        )
        
        return attachment.url, file_name
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"Error uploading attachment: {str(e)}")


def _update_work_item_with_attachment_impl(
    item_id: int,
    attachment_url: str,
    attachment_name: str,
    comment: Optional[str],
    wit_client: WorkItemTrackingClient
) -> str:
    """
    Update a work item with an attachment.

    Args:
        item_id: Work item ID
        attachment_url: Attachment URL
        attachment_name: Attachment name
        comment: Optional comment about the attachment
        wit_client: Work item tracking client
            
    Returns:
        Formatted string containing updated work item information
    """
    try:
        # Create the update document
        document = [{
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "AttachedFile",
                "url": attachment_url,
                "attributes": {
                    "comment": comment or f"Uploaded attachment: {attachment_name}"
                }
            }
        }]

        # Update the work item
        updated_work_item = wit_client.update_work_item(
            document=document,
            id=item_id
        )

        return format_work_item(updated_work_item)
    except Exception as e:
        return f"Error updating work item with attachment: {str(e)}"


def register_tools(mcp) -> None:
    """
    Register work item attachment tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.tool()
    def add_work_item_attachment(
        id: int,
        file_path: str,
        comment: Optional[str] = None,
        project: Optional[str] = None
    ) -> str:
        """
        Adds a file attachment to a work item.
    
        Use this tool when you need to:
        - Attach files to existing work items for reference
        - Provide screenshots, logs, or other files as evidence
        - Include documents related to a task or bug
        - Add rich content like diagrams or images to work items
        
        IMPORTANT: The attached file will be uploaded to Azure DevOps
        and will be visible to anyone with access to the work item.
        File size limits may apply based on your organization settings.
        
        Args:
            id: The work item ID to attach the file to
            file_path: Full path to the file on the local system
            comment: Optional comment explaining the attachment
            project: Optional project name
            
        Returns:
            Formatted string containing the updated work item with attachment
            information and a link to download the file
        """
        try:
            wit_client = get_work_item_client()
            
            # Upload the attachment
            attachment_url, attachment_name = _upload_attachment_impl(
                file_path,
                wit_client,
                project
            )
            
            # Update the work item
            return _update_work_item_with_attachment_impl(
                id,
                attachment_url,
                attachment_name,
                comment,
                wit_client
            )
            
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error adding attachment: {str(e)}"
