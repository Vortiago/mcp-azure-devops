def list_process_templates(core_client):
    """
    Lists all available process templates in Azure DevOps.
    
    Args:
        core_client: The Azure DevOps core client
        
    Returns:
        List of process templates
    """
    # Get processes
    processes = core_client.get_processes()
    return processes