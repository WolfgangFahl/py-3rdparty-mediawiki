'''
Created on 2020-10-29

@author: wf
'''
import unittest
import getpass
from wikibot.wikipush import WikiPush

class TestWikiPush(unittest.TestCase):
    '''
    test pushing pages including images
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def testQuery(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/10
        Query support for page selection
        '''
        if getpass.getuser()=="travis":
            return
        wp=WikiPush("smw","test")
        pages=wp.query("[[Category:City]]")
        self.assertTrue(len(pages)>5)
        self.assertTrue("Demo:Tokyo" in pages)

    def testWikiPush(self):
        '''
        test pushing a page from one wiki to another
        '''
        # don't test this in Travis
        if getpass.getuser()=="travis":
            return
        wp=WikiPush("wikipedia_org_test2","test")
        for force in [False,True]:
            for ignore in [False,True]:
                wp.push(["PictureTestPage"],force=force,ignore=ignore)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()