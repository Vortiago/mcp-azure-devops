"""
Formatting utilities for Azure DevOps work items.

This module provides functions to format work items for display.
"""
from azure.devops.v7_1.work_item_tracking.models import WorkItem


def _format_header(work_item: WorkItem, fields: dict) -> list[str]:
    """
    Format the header section of a work item.
    
    Args:
        work_item: The work item object
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with header information
    """
    title = fields.get("System.Title", "Untitled")
    item_type = fields.get("System.WorkItemType", "Unknown")
    state = fields.get("System.State", "Unknown")
    project = fields.get("System.TeamProject", "Unknown")
    
    header = [f"# Work Item {work_item.id}: {title}",
              f"Type: {item_type}",
              f"State: {state}"]
    
    # Add revision number
    if hasattr(work_item, 'rev'):
        header.append(f"Revision: {work_item.rev}")
    
    header.append(f"Project: {project}")
    
    # Add link to the work item (if available)
    try:
        if hasattr(work_item, '_links') and work_item._links:
            if (hasattr(work_item._links, 'html') and 
                    hasattr(work_item._links.html, 'href')):
                header.append(f"Web URL: {work_item._links.html.href}")
    except Exception:
        # If any error occurs, just skip adding the URL
        pass
    
    return header


def _format_description_sections(fields: dict) -> list[str]:
    """
    Format the description-related sections.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with description sections
    """
    sections = []
    
    # Add description
    if "System.Description" in fields:
        sections.append("\n## Description")
        sections.append(fields["System.Description"])
    
    # Add acceptance criteria if available
    if "Microsoft.VSTS.Common.AcceptanceCriteria" in fields:
        sections.append("\n## Acceptance Criteria")
        sections.append(fields["Microsoft.VSTS.Common.AcceptanceCriteria"])
    
    # Add repro steps if available
    if "Microsoft.VSTS.TCM.ReproSteps" in fields:
        sections.append("\n## Repro Steps")
        sections.append(fields["Microsoft.VSTS.TCM.ReproSteps"])
    
    # Add system info if available (for bugs)
    if "Microsoft.VSTS.TCM.SystemInfo" in fields:
        sections.append("\n## System Information")
        sections.append(fields["Microsoft.VSTS.TCM.SystemInfo"])
    
    return sections


def _format_people_info(fields: dict) -> list[str]:
    """
    Format information about people associated with the work item.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with people information
    """
    people_info = []
    
    if "System.AssignedTo" in fields:
        assigned_to = fields['System.AssignedTo']
        # Handle the AssignedTo object which could be a dict or dict-like 
        # object
        if (hasattr(assigned_to, 'display_name') and 
                hasattr(assigned_to, 'unique_name')):
            # If it's an object with directly accessible properties
            people_info.append(
                f"Assigned To: {assigned_to.display_name} "
                f"({assigned_to.unique_name})")
        elif isinstance(assigned_to, dict):
            # If it's a dictionary
            display_name = assigned_to.get('displayName', '')
            unique_name = assigned_to.get('uniqueName', '')
            people_info.append(f"Assigned To: {display_name} ({unique_name})")
        else:
            # Fallback to display the raw value if we can't parse it
            people_info.append(f"Assigned To: {assigned_to}")
    
    # Add created by information
    if "System.CreatedBy" in fields:
        created_by = fields['System.CreatedBy']
        if hasattr(created_by, 'display_name'):
            people_info.append(f"Created By: {created_by.display_name}")
        elif isinstance(created_by, dict) and 'displayName' in created_by:
            people_info.append(f"Created By: {created_by['displayName']}")
        else:
            people_info.append(f"Created By: {created_by}")
    
    # Add activated by information (if available)
    if "Microsoft.VSTS.Common.ActivatedBy" in fields:
        activated_by = fields['Microsoft.VSTS.Common.ActivatedBy']
        if hasattr(activated_by, 'display_name'):
            people_info.append(f"Activated By: {activated_by.display_name}")
        elif isinstance(activated_by, dict) and 'displayName' in activated_by:
            people_info.append(f"Activated By: {activated_by['displayName']}")
        else:
            people_info.append(f"Activated By: {activated_by}")
    
    # Add resolved by information (if available)
    if "Microsoft.VSTS.Common.ResolvedBy" in fields:
        resolved_by = fields['Microsoft.VSTS.Common.ResolvedBy']
        if hasattr(resolved_by, 'display_name'):
            people_info.append(f"Resolved By: {resolved_by.display_name}")
        elif isinstance(resolved_by, dict) and 'displayName' in resolved_by:
            people_info.append(f"Resolved By: {resolved_by['displayName']}")
        else:
            people_info.append(f"Resolved By: {resolved_by}")
    
    return people_info


def _format_dates(fields: dict) -> list[str]:
    """
    Format date information for the work item.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with date information
    """
    date_info = []
    
    # Add created date
    if "System.CreatedDate" in fields:
        date_info.append(f"Created Date: {fields['System.CreatedDate']}")
    
    # Add state change date (if available)
    if "Microsoft.VSTS.Common.StateChangeDate" in fields:
        date_info.append(
            f"State Changed: "
            f"{fields['Microsoft.VSTS.Common.StateChangeDate']}")
    
    # Add activated date (if available)
    if "Microsoft.VSTS.Common.ActivatedDate" in fields:
        date_info.append(
            f"Activated Date: {fields['Microsoft.VSTS.Common.ActivatedDate']}")
    
    # Add resolved date (if available)
    if "Microsoft.VSTS.Common.ResolvedDate" in fields:
        date_info.append(
            f"Resolved Date: {fields['Microsoft.VSTS.Common.ResolvedDate']}")
    
    # Add last updated information
    if "System.ChangedDate" in fields:
        changed_date = fields['System.ChangedDate']
        
        # Add the changed by information if available
        if "System.ChangedBy" in fields:
            changed_by = fields['System.ChangedBy']
            if hasattr(changed_by, 'display_name'):
                date_info.append(
                    f"Last updated {changed_date} by "
                    f"{changed_by.display_name}")
            elif isinstance(changed_by, dict) and 'displayName' in changed_by:
                date_info.append(
                    f"Last updated {changed_date} by "
                    f"{changed_by['displayName']}")
            else:
                date_info.append(
                    f"Last updated {changed_date} by {changed_by}")
        else:
            date_info.append(f"Last updated: {changed_date}")
    
    return date_info


def _format_categorization(fields: dict) -> list[str]:
    """
    Format categorization information for the work item.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with categorization information
    """
    categorization = []
    
    if "System.IterationPath" in fields:
        categorization.append(f"Iteration: {fields['System.IterationPath']}")
    
    if "System.AreaPath" in fields:
        categorization.append(f"Area: {fields['System.AreaPath']}")
    
    # Add value area (if available)
    if "Microsoft.VSTS.Common.ValueArea" in fields:
        categorization.append(
            f"Value Area: {fields['Microsoft.VSTS.Common.ValueArea']}")
    
    # Add risk (if available)
    if "Microsoft.VSTS.Common.Risk" in fields:
        categorization.append(f"Risk: {fields['Microsoft.VSTS.Common.Risk']}")
    
    # Add severity (if available)
    if "Microsoft.VSTS.Common.Severity" in fields:
        categorization.append(
            f"Severity: {fields['Microsoft.VSTS.Common.Severity']}")
    
    # Add tags
    if "System.Tags" in fields and fields["System.Tags"]:
        categorization.append(f"Tags: {fields['System.Tags']}")
    
    return categorization


def _format_metrics(fields: dict) -> list[str]:
    """
    Format metric information for the work item.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with metric information
    """
    metrics = []
    
    # Add priority
    if "Microsoft.VSTS.Common.Priority" in fields:
        metrics.append(f"Priority: {fields['Microsoft.VSTS.Common.Priority']}")
    
    # Add effort/story points (could be in different fields depending on 
    # process template)
    if "Microsoft.VSTS.Scheduling.Effort" in fields:
        metrics.append(f"Effort: {fields['Microsoft.VSTS.Scheduling.Effort']}")
    if "Microsoft.VSTS.Scheduling.StoryPoints" in fields:
        metrics.append(
            f"Story Points: {fields['Microsoft.VSTS.Scheduling.StoryPoints']}")
    
    return metrics


def _format_related_items(work_item: WorkItem) -> list[str]:
    """
    Format information about related work items using links.
    
    Args:
        work_item: The work item object
        
    Returns:
        List of strings with related work items information
    """
    related_items = []
    
    # Check if work item has links
    if hasattr(work_item, 'relations') and work_item.relations:
        # Check if there are work item links
        links_section = []
        
        links_section.append("\n## Related Items")
        for link in work_item.relations:
            # Look for the related work items link collection
            related_items.append(f"- {link.rel} URL: {link.url}")
            if hasattr(link, 'attributes') and link.attributes:
                related_items.append(f"  :: Attributes: {link.attributes}")
    
    
    return related_items


def _format_state_info(fields: dict) -> list[str]:
    """
    Format state-related information for the work item.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with state information
    """
    state_info = []
    
    # Add reason (if available)
    if "System.Reason" in fields:
        state_info.append(f"Reason: {fields['System.Reason']}")
    
    return state_info


def _format_scheduling_info(fields: dict) -> list[str]:
    """
    Format scheduling information for the work item.
    
    Args:
        fields: Dictionary of work item fields
        
    Returns:
        List of strings with scheduling information
    """
    scheduling_info = []
    
    # Add start date (if available)
    if "Microsoft.VSTS.Scheduling.StartDate" in fields:
        scheduling_info.append(
            f"Start Date: {fields['Microsoft.VSTS.Scheduling.StartDate']}")
    
    # Add finish date (if available)
    if "Microsoft.VSTS.Scheduling.FinishDate" in fields:
        scheduling_info.append(
            f"Finish Date: {fields['Microsoft.VSTS.Scheduling.FinishDate']}")
    
    # Add remaining work (if available)
    if "Microsoft.VSTS.Scheduling.RemainingWork" in fields:
        scheduling_info.append(
            f"Remaining Work: "
            f"{fields['Microsoft.VSTS.Scheduling.RemainingWork']} hours")
    
    # Add completed work (if available)
    if "Microsoft.VSTS.Scheduling.CompletedWork" in fields:
        scheduling_info.append(
            f"Completed Work: "
            f"{fields['Microsoft.VSTS.Scheduling.CompletedWork']} hours")
    
    return scheduling_info


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
    details = []
    
    # Build the work item information in sections
    details.extend(_format_header(work_item, fields))
    details.extend(_format_description_sections(fields))
    
    # Add additional details section
    details.append("\n## Additional Details")
    
    details.extend(_format_people_info(fields))
    details.extend(_format_dates(fields))
    details.extend(_format_state_info(fields))
    details.extend(_format_board_info(fields))
    details.extend(_format_scheduling_info(fields))
    details.extend(_format_categorization(fields))
    details.extend(_format_metrics(fields))
    details.extend(_format_build_info(fields))
    details.extend(_format_related_items(work_item))
    
    return "\n".join(details)
