def check_operation_status(core_client, operation_id: str):
    """
    Checks the status of an operation in Azure DevOps.
    
    Args:
        core_client: The Azure DevOps core client
        operation_id: The ID of the operation to check
        
    Returns:
        The operation details
    """
    operation = core_client.get_operation(operation_id)
    return operation