"""
Created on 2024-08-14

@author: wf
"""

import unittest

from tests.base_wiki_test import BaseWikiTest
from wikibot3rd.wikiclient import WikiClient
from wikibot3rd.wikipush import WikiPush


class TestNonSMW(BaseWikiTest):
    """
    Test functionality for non SemanticMediaWiki sites
    according to https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/104

    Add basic support for non SMW wikis
    """

    def setUp(self, debug=False, profile=True):
        BaseWikiTest.setUp(self, debug=debug, profile=profile)
        self.wiki_id = "genealogy"
        self.category_name = "Adressbuch_in_der_Online-Erfassung/fertig"
        self.category = f"Kategorie:{self.category_name}"

        # Setup WikiUser for non-SMW wiki
        self.wiki_user = self.get_wiki_user(self.wiki_id, save=self.inPublicCI())

        # Setup WikiClient
        self.wiki_client = WikiClient.ofWikiUser(self.wiki_user)
        self.wiki_client.is_smw_enabled = False

    def test_category_query(self):
        """
        Test querying a category on a non-SMW wiki
        Example: https://wiki.genealogy.net/Kategorie:Adressbuch_in_der_Online-Erfassung/fertig
        """
        debug = self.debug
        # debug=True
        wikipush = WikiPush(self.wiki_id, None, debug=self.debug)
        wikipush.fromWiki = self.wiki_client

        # Check if the wiki is correctly identified as non-SMW
        self.assertFalse(wikipush.fromWiki.is_smw_enabled)

        test_cases = [
            (f"[[{self.category}]]", 500, self.category_name, 300, 10),
            # 34103 categories as of 2024-09-27
            (f"[[Category:+]]", 50000, "+", 1500, 30),
        ]
        for (
            ask_query,
            limit,
            expected_category,
            expected_pages,
            debug_pages,
        ) in test_cases:
            category, _mainlabel = wikipush.extract_category_and_mainlabel(ask_query)
            self.assertEqual(expected_category, category)
            pages = wikipush.query(
                ask_query, limit=limit
            )  # Limit to 10 for faster testing

            # Assertions
            self.assertIsNotNone(pages)
            if debug:
                print(f"Found {len(pages)} pages in category {category}:")
                for i, page_title in enumerate(pages, start=1):
                    if i <= debug_pages:
                        print(f"{i:3}:{page_title}")
            self.assertGreaterEqual(len(pages), expected_pages)


if __name__ == "__main__":
    unittest.main()
