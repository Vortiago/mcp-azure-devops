"""
Utility functions for Azure DevOps work item tools.

This module provides shared utility functions used across work item tools.
"""
from typing import Optional


def sanitize_description_html(description: Optional[str]) -> Optional[str]:
    """
    Check and automatically convert description text to HTML format, preserving line breaks.
    
    Args:
        description: Original description text, can be plain text or HTML
        
    Returns:
        Processed HTML text with preserved line formatting
    """
    if not description:
        return description
        
    desc_stripped = description.strip()
    if desc_stripped.startswith('<') and '>' in desc_stripped and (
        '<html' in desc_stripped.lower() or '<p>' in desc_stripped.lower() or '<div' in desc_stripped.lower()
    ):
        return description
    
    # Convert line breaks to HTML break tags
    description_html = description.replace('\n', '<br>')
    return f"<div>{description_html}</div>"
