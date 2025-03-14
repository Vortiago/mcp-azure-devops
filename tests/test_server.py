"""
Tests for the Azure DevOps MCP Server.
"""
import pytest
from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from mcp_azure_devops.server import mcp


# Mark all tests with anyio for async testing
@pytest.mark.anyio
async def test_server_initialization():
    """Test that the server initializes correctly and returns capabilities."""
    async with client_session(mcp._mcp_server) as client:
        # Initialize the connection
        init_result = await client.initialize()
        
        # Check that initialization was successful
        assert init_result is not None
        
        # Check server name in serverInfo
        assert init_result.serverInfo.name == "Azure DevOps"
        
        # Check that the server has capabilities
        capabilities = init_result.capabilities
        assert capabilities is not None
        
        # Check for specific capabilities we expect
        assert capabilities.prompts is not None
        assert capabilities.resources is not None
        assert capabilities.tools is not None