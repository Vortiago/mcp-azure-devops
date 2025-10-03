"""
Attachment operations for Azure DevOps work items.

This module provides MCP tools for uploading and attaching files to work items.
"""
import os
import re
from io import BytesIO
from typing import Optional, Tuple, List, Dict, Union

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
        item_id: The work item ID (integer). Example: 502199
                This should be a positive integer representing the unique
                identifier of the work item in Azure DevOps.
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


def _get_work_item_attachments_impl(
    item_id: int,
    wit_client: WorkItemTrackingClient,
    project: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Get all attachments for a work item, including those embedded in HTML fields.

    Args:
        item_id: The work item ID (integer). Example: 502199
                This should be a positive integer representing the unique
                identifier of the work item in Azure DevOps.
        wit_client: Work item tracking client
        project: Optional project name
            
    Returns:
        List of dictionaries with attachment details    
    """
    try:
        # Get the work item with all fields
        work_item = wit_client.get_work_item(item_id, expand="all")
        
        attachments = []
        
        # Check for formal attachments in relations
        if hasattr(work_item, 'relations') and work_item.relations:
            for relation in work_item.relations:
                if relation.rel == "AttachedFile":
                    attachments.append({
                        'url': relation.url,
                        'name': relation.attributes.get('name', 'Unknown'),
                        'comment': relation.attributes.get('comment', ''),
                        'type': 'formal_attachment'
                    })
        
        # Check for embedded images in HTML fields
        html_fields = ["System.Description", "Microsoft.VSTS.Common.AcceptanceCriteria"]
        for field in html_fields:
            if field in work_item.fields:
                html_content = work_item.fields[field]
                if html_content:
                    # Find all image URLs using regex
                    img_urls = re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*>', html_content)
                    for url in img_urls:
                        file_name = url.split('?fileName=')[-1] if '?fileName=' in url else 'embedded_image.png'
                        attachments.append({
                            'url': url,
                            'name': file_name,
                            'field': field,
                            'type': 'embedded_image'
                        })
        
        return attachments
    except Exception as e:
        raise Exception(f"Error retrieving work item attachments: {str(e)}")


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
            id: The work item ID (integer). Example: 502199
                This should be a positive integer representing the unique
                identifier of the work item in Azure DevOps.
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
            
    @mcp.tool()
    def get_work_item_attachments(
        id: int,
        project: Optional[str] = None
    ) -> str:
        """
        Retrieves all attachments from a work item, including embedded images.
        
        Use this tool when you need to:
        - Get links to files attached to a work item
        - Find image URLs embedded in work item descriptions
        - View a list of all graphical content in a work item
        - Access diagrams or screenshots included in requirements
        
        Args:
            id: The work item ID (integer). Example: 502199
                This should be a positive integer representing the unique
                identifier of the work item in Azure DevOps.
            project: Optional project name
            
        Returns:
            Formatted string containing all attachment information,
            including URLs, names, and types (formal attachments vs
            embedded images), formatted as markdown
        """
        try:
            wit_client = get_work_item_client()
            
            # Get attachments
            attachments = _get_work_item_attachments_impl(id, wit_client, project)
            
            # Format the response
            if not attachments:
                return f"No attachments or embedded images found for work item {id}."
                
            # Prepare markdown response
            result = [f"# Attachments for Work Item {id}\n"]
            
            # Group by type
            formal_attachments = [a for a in attachments if a.get('type') == 'formal_attachment']
            embedded_images = [a for a in attachments if a.get('type') == 'embedded_image']
            
            if formal_attachments:
                result.append("## Formal Attachments")
                for idx, attachment in enumerate(formal_attachments, 1):
                    result.append(f"### {idx}. {attachment['name']}")
                    result.append(f"- URL: {attachment['url']}")
                    if attachment.get('comment'):
                        result.append(f"- Comment: {attachment['comment']}")
                    result.append("")
            
            if embedded_images:
                result.append("## Embedded Images")
                for idx, image in enumerate(embedded_images, 1):
                    result.append(f"### {idx}. {image['name']}")
                    result.append(f"- URL: {image['url']}")
                    result.append(f"- Located in: {image['field']}")
                    result.append(f"- Preview: ![Image {idx}]({image['url']})")
                    result.append("")
            
            return "\n".join(result)
            
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error retrieving attachments: {str(e)}"
