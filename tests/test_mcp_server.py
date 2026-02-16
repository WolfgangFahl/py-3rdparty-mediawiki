"""
Created on 2025-01-01

@author: wf

Tests for MCP Server
"""

import unittest
from unittest.mock import MagicMock, patch

from tests.base_wiki_test import BaseWikiTest


class TestMCPServer(BaseWikiTest):
    """
    Unit tests for MCP Server
    """

    def test_list_wikis_impl(self):
        """Test listing configured wikis."""
        from wikibot3rd.mcp_server import list_wikis_impl

        with patch("wikibot3rd.mcp_server.WikiUser") as mock_wiki_user_class:
            mock_wiki_user_class.getWikiUsers.return_value = {
                "test.wiki.org": MagicMock(
                    wikiId="test.wiki.org",
                    url="https://test.wiki.org",
                    user="testuser",
                ),
                "another.wiki.org": MagicMock(
                    wikiId="another.wiki.org",
                    url="https://another.wiki.org",
                    user=None,
                ),
            }

            result = list_wikis_impl()

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["wikiId"], "test.wiki.org")
            self.assertEqual(result[0]["user"], "testuser")
            self.assertEqual(result[1]["wikiId"], "another.wiki.org")
            self.assertEqual(result[1]["user"], "")

    def test_format_page(self):
        """Test page formatting."""
        from wikibot3rd.mcp_server import format_page

        mock_page = MagicMock()
        mock_page.name = "Test Page"
        mock_page.pageid = 12345
        mock_page.text.return_value = "Page content"

        result = format_page(mock_page)

        self.assertEqual(result["title"], "Test Page")
        self.assertEqual(result["pageid"], 12345)
        self.assertEqual(result["content"], "Page content")

    def test_format_search_result(self):
        """Test search result formatting."""
        from wikibot3rd.mcp_server import format_search_result

        mock_result = MagicMock()
        mock_result.name = "Search Result"
        mock_result.pageid = 123

        result = format_search_result(mock_result)

        self.assertEqual(result["title"], "Search Result")
        self.assertEqual(result["pageid"], "123")

    def test_get_wiki_client_not_found(self):
        """Test that ValueError is raised for unknown wiki."""
        from wikibot3rd.mcp_server import get_wiki_client

        with patch("wikibot3rd.mcp_server.WikiUser") as mock_wiki_user_class:
            mock_wiki_user_class.ofWikiId.return_value = None

            with self.assertRaises(ValueError) as context:
                get_wiki_client("nonexistent.wiki.org")

            self.assertIn("not found", str(context.exception))

    def test_get_wiki_client_success(self):
        """Test getting wiki client for known wiki."""
        from wikibot3rd.mcp_server import get_wiki_client
        from wikibot3rd.wikiclient import WikiClient
        from wikibot3rd.wikiuser import WikiUser

        with patch("wikibot3rd.mcp_server.WikiUser") as mock_wiki_user_class:
            with patch("wikibot3rd.mcp_server.WikiClient") as mock_client_class:
                mock_wiki_user = MagicMock(spec=WikiUser)
                mock_wiki_user_class.ofWikiId.return_value = mock_wiki_user

                mock_client = MagicMock(spec=WikiClient)
                mock_client_class.of_wiki_user.return_value = mock_client

                result = get_wiki_client("test.wiki.org")

                mock_wiki_user_class.ofWikiId.assert_called_once_with(
                    "test.wiki.org", lenient=False
                )
                mock_client_class.of_wiki_user.assert_called_once_with(mock_wiki_user)
                self.assertEqual(result, mock_client)

    def test_preview_edit_token_generation(self):
        """Test that preview_edit_impl generates a valid token."""
        from wikibot3rd.mcp_server import PREVIEW_STORE, preview_edit_impl

        mock_client = MagicMock()
        mock_page = MagicMock()
        mock_page.text.return_value = "Old content"
        mock_client.get_page.return_value = mock_page

        with patch("wikibot3rd.mcp_server.get_wiki_client", return_value=mock_client):
            result = preview_edit_impl(
                wiki_id="test.wiki.org",
                page_title="Test Page",
                content="New content",
                summary="Test edit",
            )

            self.assertTrue(result["success"])
            self.assertIn("token", result)
            self.assertIn(result["token"], PREVIEW_STORE)
            self.assertEqual(result["old_content"], "Old content")
            self.assertEqual(result["new_content"], "New content")

    def test_commit_edit_success(self):
        """Test committing a previewed edit."""
        from wikibot3rd.mcp_server import (
            PREVIEW_STORE,
            commit_edit_impl,
            preview_edit_impl,
        )

        mock_client = MagicMock()
        mock_page = MagicMock()
        mock_page.text.return_value = "Old content"
        mock_client.get_page.return_value = mock_page

        with patch("wikibot3rd.mcp_server.get_wiki_client", return_value=mock_client):
            preview_result = preview_edit_impl(
                wiki_id="test.wiki.org",
                page_title="Test Page",
                content="New content",
                summary="Test edit",
            )

            token = preview_result["token"]

            result = commit_edit_impl(
                wiki_id="test.wiki.org",
                page_title="Test Page",
                token=token,
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["title"], "Test Page")
            mock_client.save_page.assert_called_once_with(
                "Test Page", "New content", "Test edit"
            )
            self.assertNotIn(token, PREVIEW_STORE)

    def test_commit_edit_invalid_token(self):
        """Test commit with invalid token fails."""
        from wikibot3rd.mcp_server import commit_edit_impl

        with self.assertRaises(ValueError) as context:
            commit_edit_impl(
                wiki_id="test.wiki.org",
                page_title="Test Page",
                token="invalid-token-123",
            )

        self.assertIn("Invalid or expired token", str(context.exception))

    def test_generate_diff(self):
        """Test diff generation."""
        from wikibot3rd.mcp_server import generate_diff

        result = generate_diff("Line 1\nLine 2", "Line 1\nLine 2")
        self.assertIn("No changes", result)

        result = generate_diff("Old content", "New content")
        self.assertIn("Old content", result)
        self.assertIn("New content", result)

    def test_set_wiki_impl(self):
        """Test setting default wiki."""
        from wikibot3rd.mcp_server import set_wiki_impl

        with patch("wikibot3rd.mcp_server.WikiUser") as mock_wiki_user_class:
            mock_wiki_user_class.ofWikiId.return_value = MagicMock()

            result = set_wiki_impl("test.wiki.org")

            self.assertTrue(result["success"])
            self.assertIn("test.wiki.org", result["message"])

    def test_set_wiki_impl_not_found(self):
        """Test setting wiki that doesn't exist."""
        from wikibot3rd.mcp_server import set_wiki_impl

        with patch("wikibot3rd.mcp_server.WikiUser") as mock_wiki_user_class:
            mock_wiki_user_class.ofWikiId.return_value = None

            with self.assertRaises(ValueError):
                set_wiki_impl("nonexistent.wiki.org")


if __name__ == "__main__":
    unittest.main()
