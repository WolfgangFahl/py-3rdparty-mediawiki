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
        """Test committing a previewed edit (CAS: preview records the base)."""
        import time

        from wikibot3rd.mcp_server import (PREVIEW_STORE, _page_base,
                                           commit_edit_impl, preview_edit_impl)

        _page_base.clear()
        base_time = time.strptime("20260705120000", "%Y%m%d%H%M%S")
        mock_client = MagicMock()
        mock_page = MagicMock()
        mock_page.text.return_value = "Old content"
        mock_page.name = "Test Page"
        mock_page.last_rev_time = base_time
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
            # CAS (#134): the commit must pass the basetimestamp recorded at preview
            mock_client.save_page.assert_called_once_with(
                "Test Page",
                "New content",
                "Test edit",
                section=None,
                basetimestamp="20260705120000",
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

    def test_is_logged_in_impl(self):
        """Test is_logged_in_impl returns the client's login state."""
        from wikibot3rd.mcp_server import _client_cache, is_logged_in_impl

        mock_client = MagicMock()
        mock_client.is_logged_in = True
        _client_cache["test.wiki.org"] = mock_client

        result = is_logged_in_impl("test.wiki.org")

        self.assertTrue(result)
        _client_cache.pop("test.wiki.org", None)

    def test_login_impl_success(self):
        """Test login_impl returns success when login works."""
        from wikibot3rd.mcp_server import _client_cache, login_impl

        mock_wiki_user = MagicMock()
        mock_wiki_user.user = "bot"
        mock_wiki_user.getPassword.return_value = "secret"

        mock_client = MagicMock()
        mock_client.is_logged_in = True

        with patch("wikibot3rd.mcp_server.WikiUser") as mock_wu_class:
            mock_wu_class.ofWikiId.return_value = mock_wiki_user
            with patch("wikibot3rd.mcp_server.WikiClient") as mock_client_class:
                mock_client_class.of_wiki_user.return_value = mock_client
                _client_cache.pop("test.wiki.org", None)

                result = login_impl("test.wiki.org")

                self.assertTrue(result["success"])
                self.assertIn("test.wiki.org", result["message"])

    def test_login_impl_no_credentials(self):
        """Test login_impl raises ValueError when no credentials are set."""
        from wikibot3rd.mcp_server import _client_cache, login_impl

        mock_wiki_user = MagicMock()
        mock_wiki_user.user = None
        mock_wiki_user.getPassword.return_value = None

        with patch("wikibot3rd.mcp_server.WikiUser") as mock_wu_class:
            mock_wu_class.ofWikiId.return_value = mock_wiki_user
            _client_cache.pop("test.wiki.org", None)

            with self.assertRaises(ValueError) as ctx:
                login_impl("test.wiki.org")

            self.assertIn("no credentials", str(ctx.exception))

    def test_call_mediawiki_api_requires_login(self):
        """Test call_mediawiki_api raises PermissionError when not logged in."""
        from wikibot3rd.mcp_server import call_mediawiki_api_impl

        mock_client = MagicMock()
        mock_client.is_logged_in = False

        with patch("wikibot3rd.mcp_server.get_wiki_client", return_value=mock_client):
            with self.assertRaises(PermissionError) as ctx:
                call_mediawiki_api_impl(
                    "test.wiki.org", {"action": "query", "list": "recentchanges"}
                )
            self.assertIn("Not logged in", str(ctx.exception))

    def test_call_mediawiki_api_success(self):
        """Test call_mediawiki_api passes params to site.api and returns result."""
        from wikibot3rd.mcp_server import call_mediawiki_api_impl

        mock_client = MagicMock()
        mock_client.is_logged_in = True
        mock_site = MagicMock()
        mock_site.api.return_value = {"query": {"recentchanges": [{"title": "Test"}]}}
        mock_client.get_site.return_value = mock_site

        with patch("wikibot3rd.mcp_server.get_wiki_client", return_value=mock_client):
            result = call_mediawiki_api_impl(
                "test.wiki.org",
                {"action": "query", "list": "recentchanges", "rclimit": 5},
            )

        mock_site.api.assert_called_once_with("query", list="recentchanges", rclimit=5)
        self.assertIn("query", result)

    def test_call_mediawiki_api_limit(self):
        """Test call_mediawiki_api truncates oversized list results."""
        from wikibot3rd.mcp_server import call_mediawiki_api_impl

        mock_client = MagicMock()
        mock_client.is_logged_in = True
        mock_site = MagicMock()
        mock_site.api.return_value = {
            "query": {"recentchanges": [{"title": f"Page{i}"} for i in range(200)]}
        }
        mock_client.get_site.return_value = mock_site

        with patch("wikibot3rd.mcp_server.get_wiki_client", return_value=mock_client):
            result = call_mediawiki_api_impl(
                "test.wiki.org",
                {"action": "query", "list": "recentchanges"},
                limit=10,
            )

        self.assertEqual(len(result["query"]["recentchanges"]), 10)

    def test_update_section_zero_replaces_content(self):
        """Test that update_section with section 0 replaces top content."""
        from wikibot3rd.wikiclient import WikiClient

        mock_client = WikiClient.__new__(WikiClient)
        mock_page = MagicMock()

        def mock_get_page(page_title):
            return mock_page

        mock_client.get_page = mock_get_page
        mock_client.save_page(
            page_title="Test Page",
            page_content="New top content",
            page_summary="Test update",
            section="0",
        )

        mock_page.edit.assert_called_once_with(
            "New top content", "Test update", section="0"
        )

    def test_section_numbering_matches_mediawiki(self):
        """
        Regression for #133: read-side section numbering must match the
        MediaWiki edit numbering used by update_section, including single-=
        (H1) headings and 0 = page lead. Previously the read side skipped
        single-= headings, so update_section wrote to the wrong section.
        """
        from wikibot3rd.mcp_server import (get_page_sections_impl,
                                           get_section_content_impl)

        wikitext = (
            "lead text\n"
            "= Problems =\n"
            "p\n"
            "== Alpha ==\n"
            "a\n"
            "== Beta ==\n"
            "b\n"
            "= Effort =\n"
            "e\n"
        )
        mock_client = MagicMock()
        mock_page = MagicMock()
        mock_page.text.return_value = wikitext
        mock_client.get_page.return_value = mock_page

        with patch(
            "wikibot3rd.mcp_server.get_wiki_client", return_value=mock_client
        ):
            sections = get_page_sections_impl("test.wiki.org", "Test Page")

            # MediaWiki numbering: 0=lead (implicit), 1=Problems, 2=Alpha,
            # 3=Beta, 4=Effort - single-= headings are counted.
            self.assertEqual(
                [(s["index"], s["title"]) for s in sections],
                [(1, "Problems"), (2, "Alpha"), (3, "Beta"), (4, "Effort")],
            )

            # Every reported index must round-trip: the content fetched for
            # that index is the section whose heading we listed.
            for s in sections:
                got = get_section_content_impl(
                    "test.wiki.org", "Test Page", str(s["index"])
                )
                self.assertEqual(got["section_number"], str(s["index"]))
                self.assertEqual(got["title"], s["title"])
                # content includes the heading (what edit replaces)
                self.assertIn(f"= {s['title']} =", got["content"])

            # 'Beta' (a == heading) must be section 3, not 1 - the old bug.
            beta = next(s for s in sections if s["title"] == "Beta")
            self.assertEqual(beta["index"], 3)

            # section 0 is the lead (before the first heading)
            lead = get_section_content_impl("test.wiki.org", "Test Page", "0")
            self.assertEqual(lead["content"], "lead text\n")
            self.assertIsNone(lead["title"])


class TestMCPServerCAS(BaseWikiTest):
    """
    Compare-and-swap (CAS) tests for issue #134: update_page must never
    silently overwrite a concurrent edit (lost-update), a write requires a
    prior read in the session, and create_page never overwrites an
    existing page.
    """

    def setUp(self, debug=False, profile=True):
        super().setUp(debug=debug, profile=profile)
        import time

        from wikibot3rd.mcp_server import _page_base

        _page_base.clear()
        self.base_time = time.strptime("20260705120000", "%Y%m%d%H%M%S")
        self.mock_client = MagicMock()
        self.mock_page = MagicMock()
        self.mock_page.name = "Test Page"
        self.mock_page.text.return_value = "Old content"
        self.mock_page.last_rev_time = self.base_time
        self.mock_page.exists = True
        self.mock_client.get_page.return_value = self.mock_page

    def test_update_requires_prior_read(self):
        """CAS: an update without a prior read in the session is refused."""
        from wikibot3rd.mcp_server import update_page_impl

        with patch(
            "wikibot3rd.mcp_server.get_wiki_client", return_value=self.mock_client
        ):
            with self.assertRaises(ValueError) as context:
                update_page_impl(
                    "test.wiki.org", "Test Page", "New content", "summary"
                )
            self.assertIn("was not read in this session", str(context.exception))
            self.mock_client.save_page.assert_not_called()

    def test_update_passes_read_time_basetimestamp(self):
        """CAS: update passes the basetimestamp recorded at READ time."""
        from wikibot3rd.mcp_server import get_page_impl, update_page_impl

        with patch(
            "wikibot3rd.mcp_server.get_wiki_client", return_value=self.mock_client
        ):
            get_page_impl("test.wiki.org", "Test Page")
            update_page_impl("test.wiki.org", "Test Page", "New content", "summary")
            self.mock_client.save_page.assert_called_once_with(
                "Test Page",
                "New content",
                "summary",
                section=None,
                basetimestamp="20260705120000",
            )

    def test_update_detects_same_user_conflict_client_side(self):
        """
        CAS: a concurrent edit is detected CLIENT-SIDE by comparing the head
        revision to the read-time base. Essential because MediaWiki
        suppresses basetimestamp editconflicts for the SAME user, and human +
        agent typically share one bot account.
        """
        import time

        from wikibot3rd.mcp_server import get_page_impl, update_page_impl

        with patch(
            "wikibot3rd.mcp_server.get_wiki_client", return_value=self.mock_client
        ):
            get_page_impl("test.wiki.org", "Test Page")
            # someone (same user!) edited after our read
            newer = time.strptime("20260705120500", "%Y%m%d%H%M%S")
            self.mock_page.revisions.return_value = iter([{"timestamp": newer}])
            with self.assertRaises(ValueError) as context:
                update_page_impl(
                    "test.wiki.org", "Test Page", "New content", "summary"
                )
            self.assertIn("edit conflict", str(context.exception))
            self.mock_client.save_page.assert_not_called()

    def test_update_surfaces_edit_conflict(self):
        """CAS: an editconflict from the API becomes a clear ValueError."""
        import mwclient.errors

        from wikibot3rd.mcp_server import get_page_impl, update_page_impl

        self.mock_client.save_page.side_effect = mwclient.errors.APIError(
            "editconflict", "Edit conflict detected", {}
        )
        with patch(
            "wikibot3rd.mcp_server.get_wiki_client", return_value=self.mock_client
        ):
            get_page_impl("test.wiki.org", "Test Page")
            with self.assertRaises(ValueError) as context:
                update_page_impl(
                    "test.wiki.org", "Test Page", "New content", "summary"
                )
            self.assertIn("edit conflict", str(context.exception))
            self.assertIn("re-read", str(context.exception))

    def test_update_section_is_cas_guarded(self):
        """CAS: update_section is guarded the same way as update_page."""
        from wikibot3rd.mcp_server import update_section_impl

        with patch(
            "wikibot3rd.mcp_server.get_wiki_client", return_value=self.mock_client
        ):
            with self.assertRaises(ValueError) as context:
                update_section_impl(
                    "test.wiki.org", "Test Page", "1", "New content", "summary"
                )
            self.assertIn("was not read in this session", str(context.exception))

    def test_create_page_refuses_existing(self):
        """CAS: create_page never overwrites an existing page."""
        from wikibot3rd.mcp_server import create_page_impl

        with patch(
            "wikibot3rd.mcp_server.get_wiki_client", return_value=self.mock_client
        ):
            with self.assertRaises(ValueError) as context:
                create_page_impl(
                    "test.wiki.org", "Test Page", "New content", "summary"
                )
            self.assertIn("already exists", str(context.exception))
            self.mock_client.save_page.assert_not_called()

    def test_create_page_new_page_ok(self):
        """CAS: create_page on a missing page works and records the base."""
        from wikibot3rd.mcp_server import create_page_impl

        self.mock_page.exists = False
        saved_page = MagicMock()
        saved_page.name = "Test Page"
        saved_page.last_rev_time = self.base_time
        self.mock_client.save_page.return_value = saved_page

        with patch(
            "wikibot3rd.mcp_server.get_wiki_client", return_value=self.mock_client
        ):
            result = create_page_impl(
                "test.wiki.org", "Test Page", "New content", "summary"
            )
            self.assertTrue(result["success"])
            self.mock_client.save_page.assert_called_once_with(
                "Test Page", "New content", "summary"
            )


if __name__ == "__main__":
    unittest.main()
