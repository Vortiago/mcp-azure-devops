"""
Formatting utilities for Azure DevOps work items.

This module provides functions to format work items for display.
"""
from azure.devops.v7_1.work_item_tracking.models import WorkItem


def _format_field_value(field_value) -> str:
    """
    Format a field value based on its type.
    
    Args:
        field_value: The value to format
        
    Returns:
        Formatted string representation of the value
    """
    if field_value is None:
        return "None"
    elif isinstance(field_value, dict):
        # Handle dictionary fields like people references
        if 'displayName' in field_value:
            return f"{field_value.get('displayName')} ({field_value.get('uniqueName', '')})"
        else:
            # For other dictionaries, format as key-value pairs
            return ", ".join([f"{k}: {v}" for k, v in field_value.items()])
    elif hasattr(field_value, 'display_name') and hasattr(field_value, 'unique_name'):
        # Handle objects with display_name and unique_name
        return f"{field_value.display_name} ({field_value.unique_name})"
    elif hasattr(field_value, 'display_name'):
        # Handle objects with just display_name
        return field_value.display_name
    else:
        # For everything else, use string representation
        return str(field_value)


def _format_board_info(fields: dict) -> list[str]:
    """
    Format board-related information for the work item.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with board information
    """
    board_info = []
    
    # Add board column (if available)
    if "System.BoardColumn" in fields:
        board_info.append(f"Board Column: {fields['System.BoardColumn']}")
        
        # Add board column done state (if available)
        if "System.BoardColumnDone" in fields:
            done_state = ("Done" if fields["System.BoardColumnDone"] 
                          else "Not Done")
            board_info.append(f"Column State: {done_state}")
    
    return board_info


def _format_build_info(fields: dict) -> list[str]:
    """
    Format build-related information for the work item.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with build information
    """
    build_info = []
    
    # Add found in build (if available)
    if "Microsoft.VSTS.Build.FoundIn" in fields:
        build_info.append(
            f"Found In: {fields['Microsoft.VSTS.Build.FoundIn']}")
    
    # Add integration build (if available)
    if "Microsoft.VSTS.Build.IntegrationBuild" in fields:
        build_info.append(
            f"Integration Build: "
            f"{fields['Microsoft.VSTS.Build.IntegrationBuild']}")
    
    return build_info


def format_work_item(work_item: WorkItem) -> str:
    """
    Format work item information for display.
    
    Args:
        work_item: Work item object to format
        
    Returns:
        String with formatted work item details
    """
    fields = work_item.fields or {}
    details = [f"# Work Item {work_item.id}"]
    
    # List all fields alphabetically for consistent output
    for field_name in sorted(fields.keys()):
        field_value = fields[field_name]
        formatted_value = _format_field_value(field_value)
        details.append(f"- **{field_name}**: {formatted_value}")
    
    # Add related items if available
    if hasattr(work_item, 'relations') and work_item.relations:
        details.append("\n## Related Items")
        for link in work_item.relations:
            details.append(f"- {link.rel} URL: {link.url}")
            if hasattr(link, 'attributes') and link.attributes:
                details.append(f"  :: Attributes: {link.attributes}")
    
    return "\n".join(details)
