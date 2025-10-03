"""
Unit tests for the work item attachments tools.
"""

import os
import unittest
import re
from unittest.mock import MagicMock, patch

from mcp_azure_devops.features.work_items.tools.attachments import (
    _get_work_item_attachments_impl,
)


class TestWorkItemAttachments(unittest.TestCase):
    """Tests for the work item attachments functions."""

    @patch('mcp_azure_devops.features.work_items.tools.attachments.get_work_item_client')
    def test_get_attachments_formal(self, mock_get_client):
        """Test getting formal attachments."""
        # Setup mock
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create a mock work item with formal attachments
        mock_work_item = MagicMock()
        mock_relation = MagicMock()
        mock_relation.rel = "AttachedFile"
        mock_relation.url = "https://example.com/attachment1"
        mock_relation.attributes = {
            "name": "test_file.txt",
            "comment": "Test comment"
        }
        mock_work_item.relations = [mock_relation]
        mock_work_item.fields = {}
        
        mock_client.get_work_item.return_value = mock_work_item
        
        # Call the function
        result = _get_work_item_attachments_impl(123, mock_client)
        
        # Assertions
        mock_client.get_work_item.assert_called_once_with(123, expand="all")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['url'], "https://example.com/attachment1")
        self.assertEqual(result[0]['name'], "test_file.txt")
        self.assertEqual(result[0]['comment'], "Test comment")
        self.assertEqual(result[0]['type'], "formal_attachment")
    
    @patch('mcp_azure_devops.features.work_items.tools.attachments.get_work_item_client')
    def test_get_attachments_embedded(self, mock_get_client):
        """Test getting embedded images from HTML fields."""
        # Setup mock
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create a mock work item with HTML content containing image
        mock_work_item = MagicMock()
        mock_work_item.relations = []
        mock_work_item.fields = {
            "System.Description": '<div><img src="https://91appinc.visualstudio.com/attachment?fileName=image.png" alt="Image"></div>',
            "Microsoft.VSTS.Common.AcceptanceCriteria": '<div><img src="https://91appinc.visualstudio.com/attachment2?fileName=diagram.png" alt="Diagram"></div>'
        }
        
        mock_client.get_work_item.return_value = mock_work_item
        
        # Call the function
        result = _get_work_item_attachments_impl(123, mock_client)
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], "embedded_image")
        self.assertEqual(result[0]['name'], "image.png")
        self.assertEqual(result[0]['field'], "System.Description")
        self.assertEqual(result[1]['name'], "diagram.png")
        self.assertEqual(result[1]['field'], "Microsoft.VSTS.Common.AcceptanceCriteria")
    
    @patch('mcp_azure_devops.features.work_items.tools.attachments.get_work_item_client')
    def test_get_attachments_none(self, mock_get_client):
        """Test when there are no attachments."""
        # Setup mock
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create a mock work item with no attachments
        mock_work_item = MagicMock()
        mock_work_item.relations = []
        mock_work_item.fields = {
            "System.Description": "Just text, no images",
            "Microsoft.VSTS.Common.AcceptanceCriteria": "More text"
        }
        
        mock_client.get_work_item.return_value = mock_work_item
        
        # Call the function
        result = _get_work_item_attachments_impl(123, mock_client)
        
        # Assertions
        self.assertEqual(len(result), 0)
    
    @patch('mcp_azure_devops.features.work_items.tools.attachments.get_work_item_client')
    def test_get_attachments_error(self, mock_get_client):
        """Test error handling."""
        # Setup mock to raise an exception
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_work_item.side_effect = Exception("Test error")
        
        # Call the function and verify exception is raised
        with self.assertRaises(Exception) as context:
            _get_work_item_attachments_impl(123, mock_client)
        
        self.assertIn("Error retrieving work item attachments", str(context.exception))


if __name__ == '__main__':
    unittest.main()
