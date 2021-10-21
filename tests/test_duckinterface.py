'''
Created on 2020-12-27

@author: wf
'''
import unittest
from wikibot.wiki import Wiki
from wikibot.wikibot import WikiBot
from wikibot.wikiclient import WikiClient
from tests.test_WikiUser import TestWikiUser
from tests.basetest import BaseTest

class TestDuckInterface(BaseTest):
    '''
    test https://en.wikipedia.org/wiki/Duck_typing interface of Wiki
    '''

    
    def getWikis(self,wikiId):
        '''
        get the wikis
        '''
        wikiuser=TestWikiUser.getSMW_WikiUser(wikiId)
        wikibot=WikiBot.ofWikiUser(wikiuser)
        wikiclient=WikiClient.ofWikiUser(wikiuser)
        return wikibot,wikiclient


    def testGetHtml(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/38
        add html page retrieval even when using mwclient 
        '''
        wikiId='or'
        for wiki in self.getWikis(wikiId):
            if self.debug:
                print(wiki)
            self.assertTrue(isinstance(wiki,Wiki))
            pageTitle="Openresearch:About"
            markup=wiki.getWikiMarkup(pageTitle)
            self.assertTrue("[[Imprint]]" in markup)
            html=wiki.getHtml(pageTitle)
            if self.debug:
                print(html)
            self.assertTrue('<a href="#Imprint">' in html)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()