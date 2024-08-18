"""
Created on 2024-08-14

@author: wf
"""
from tests.basetest import BaseTest
from wikibot3rd.wikipush import WikiPush
from wikibot3rd.wikiclient import WikiClient
import unittest
class TestNonSMW(BaseTest):
    """
    Test functionality for non SemanticMediaWiki sites
    according to https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/104

    Add basic support for non SMW wikis
    """

    def setUp(self, debug=False, profile=True):
        BaseTest.setUp(self, debug=debug, profile=profile)
        self.wiki_id = "genealogy"
        self.category = "Kategorie:Adressbuch_in_der_Online-Erfassung/fertig"

        # Setup WikiUser for non-SMW wiki
        self.wiki_user = self.get_wiki_user(self.wiki_id,save=self.inPublicCI())

        # Setup WikiClient
        self.wiki_client = WikiClient.ofWikiUser(self.wiki_user)
        self.wiki_client.is_smw_enabled=False

    def test_category_query(self):
        """
        Test querying a category on a non-SMW wiki
        Example: https://wiki.genealogy.net/Kategorie:Adressbuch_in_der_Online-Erfassung/fertig
        """
        wikipush = WikiPush(self.wiki_id, None, debug=self.debug)
        wikipush.fromWiki = self.wiki_client

        # Check if the wiki is correctly identified as non-SMW
        self.assertFalse(wikipush.fromWiki.is_smw_enabled)

        # Perform the category query
        query = f"[[{self.category}]]"
        limit=500
        expected=300
        pages = wikipush.query(query, limit=limit)  # Limit to 10 for faster testing

        # Assertions
        self.assertIsNotNone(pages)
        if self.debug:
            print(f"Found {len(pages)} pages in category {self.category}:")
            print(pages)
        self.assertTrue(len(pages) > expected)


if __name__ == "__main__":
    unittest.main()