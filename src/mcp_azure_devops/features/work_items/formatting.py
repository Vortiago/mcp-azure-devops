"""
Formatting utilities for Azure DevOps work items.

This module provides functions to format work items for display.
"""
from azure.devops.v7_1.work_item_tracking.models import WorkItem


def format_work_item(work_item: WorkItem) -> str:
    """
    Format work item information for display.
    
    Args:
        work_item: Work item object to format
        
    Returns:
        String with formatted work item details
    """
    fields = work_item.fields or {}
    title = fields.get("System.Title", "Untitled")
    item_type = fields.get("System.WorkItemType", "Unknown")
    state = fields.get("System.State", "Unknown")
    project = fields.get("System.TeamProject", "Unknown")
    
    # Build the basic header
    details = [f"# Work Item {work_item.id}: {title}",
               f"Type: {item_type}",
               f"State: {state}",
               f"Project: {project}"]
    
    # Add link to the work item (if available)
    try:
        if hasattr(work_item, '_links') and work_item._links:
            if hasattr(work_item._links, 'html') and hasattr(work_item._links.html, 'href'):
                details.append(f"Web URL: {work_item._links.html.href}")
    except Exception:
        # If any error occurs, just skip adding the URL
        pass
    
    # Add description
    if "System.Description" in fields:
        details.append("\n## Description")
        details.append(fields["System.Description"])
    
    # Add acceptance criteria if available
    if "Microsoft.VSTS.Common.AcceptanceCriteria" in fields:
        details.append("\n## Acceptance Criteria")
        details.append(fields["Microsoft.VSTS.Common.AcceptanceCriteria"])
    
    # Add repro steps if available
    if "Microsoft.VSTS.TCM.ReproSteps" in fields:
        details.append("\n## Repro Steps")
        details.append(fields["Microsoft.VSTS.TCM.ReproSteps"])
    
    # Add additional details section
    details.append("\n## Additional Details")
    
    if "System.AssignedTo" in fields:
        assigned_to = fields['System.AssignedTo']
        # Handle the AssignedTo object which could be a dict or dictionary-like object
        if hasattr(assigned_to, 'display_name') and hasattr(assigned_to, 'unique_name'):
            # If it's an object with directly accessible properties
            details.append(f"Assigned To: {assigned_to.display_name} ({assigned_to.unique_name})")
        elif isinstance(assigned_to, dict):
            # If it's a dictionary
            display_name = assigned_to.get('displayName', '')
            unique_name = assigned_to.get('uniqueName', '')
            details.append(f"Assigned To: {display_name} ({unique_name})")
        else:
            # Fallback to display the raw value if we can't parse it
            details.append(f"Assigned To: {assigned_to}")
    
    # Add created by information
    if "System.CreatedBy" in fields:
        created_by = fields['System.CreatedBy']
        if hasattr(created_by, 'display_name'):
            details.append(f"Created By: {created_by.display_name}")
        elif isinstance(created_by, dict) and 'displayName' in created_by:
            details.append(f"Created By: {created_by['displayName']}")
        else:
            details.append(f"Created By: {created_by}")
    
    # Add created date
    if "System.CreatedDate" in fields:
        details.append(f"Created Date: {fields['System.CreatedDate']}")
    
    # Add last updated information
    if "System.ChangedDate" in fields:
        changed_date = fields['System.ChangedDate']
        
        # Add the changed by information if available
        if "System.ChangedBy" in fields:
            changed_by = fields['System.ChangedBy']
            if hasattr(changed_by, 'display_name'):
                details.append(f"Last updated {changed_date} by {changed_by.display_name}")
            elif isinstance(changed_by, dict) and 'displayName' in changed_by:
                details.append(f"Last updated {changed_date} by {changed_by['displayName']}")
            else:
                details.append(f"Last updated {changed_date} by {changed_by}")
        else:
            details.append(f"Last updated: {changed_date}")
    
    if "System.IterationPath" in fields:
        details.append(f"Iteration: {fields['System.IterationPath']}")
    
    if "System.AreaPath" in fields:
        details.append(f"Area: {fields['System.AreaPath']}")
    
    # Add tags
    if "System.Tags" in fields and fields["System.Tags"]:
        details.append(f"Tags: {fields['System.Tags']}")
    
    # Add priority
    if "Microsoft.VSTS.Common.Priority" in fields:
        details.append(f"Priority: {fields['Microsoft.VSTS.Common.Priority']}")
    
    # Add effort/story points (could be in different fields depending on process template)
    if "Microsoft.VSTS.Scheduling.Effort" in fields:
        details.append(f"Effort: {fields['Microsoft.VSTS.Scheduling.Effort']}")
    if "Microsoft.VSTS.Scheduling.StoryPoints" in fields:
        details.append(f"Story Points: {fields['Microsoft.VSTS.Scheduling.StoryPoints']}")
    
    # Add related items section if available
    if hasattr(work_item, 'relations') and work_item.relations:
        details.append("\n## Related Items")
        
        for relation in work_item.relations:
            # Get the relation type (use getattr to safely handle missing attributes)
            rel_type = getattr(relation, 'rel', "Unknown relation")
            
            # Get the target URL
            target_url = getattr(relation, 'url', "Unknown URL")
            
            # Format the link based on what type it is
            link_text = target_url
            if "workitem" in target_url.lower():
                # It's a work item link - try to extract the ID
                try:
                    work_item_id = target_url.split('/')[-1]
                    if work_item_id.isdigit():
                        link_text = f"Work Item #{work_item_id}"
                except:
                    pass  # Keep the original URL if parsing fails
            
            # Check for comments in attributes
            comment = ""
            if hasattr(relation, 'attributes') and relation.attributes:
                attrs = relation.attributes
                if isinstance(attrs, dict) and 'comment' in attrs and attrs['comment']:
                    comment = f" - Comment: {attrs['comment']}"
            
            details.append(f"- {rel_type}: {link_text}{comment}")
    
    return "\n".join(details)
