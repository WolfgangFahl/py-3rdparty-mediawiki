"""
Created on 2020-12-27

@author: wf
"""

import unittest

from tests.base_wiki_test import BaseWikiTest
from wikibot3rd.wiki import Wiki
from wikibot3rd.wikibot import WikiBot
from wikibot3rd.wikiclient import WikiClient


class TestDuckInterface(BaseWikiTest):
    """
    test https://en.wikipedia.org/wiki/Duck_typing interface of Wiki
    """

    def getWikis(self, wikiId):
        """
        get the wikis
        """
        wikiuser = self.getSMW_WikiUser(wikiId)
        wikibot = WikiBot.ofWikiUser(wikiuser)
        wikiclient = WikiClient.ofWikiUser(wikiuser)
        return wikibot, wikiclient

    def testGetHtml(self):
        """
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/38
        add html page retrieval even when using mwclient
        """
        wikiId = "orcopy"
        debug = self.debug
        debug = True
        for wiki in self.getWikis(wikiId):
            if debug:
                print(wiki)
            self.assertTrue(isinstance(wiki, Wiki))
            pageTitle = "Openresearch:About"
            markup = wiki.getWikiMarkup(pageTitle)
            self.assertTrue("[[Imprint]]" in markup)
            html = wiki.getHtml(pageTitle)
            if self.debug:
                print(html)
            self.assertTrue('<a href="#Imprint">' in html)
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
