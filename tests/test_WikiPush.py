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
    
    def testIssue12(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/12
        add -qf / queryField option to allow to select other property than mainlabel
        '''
        # don't test this in Travis
        if getpass.getuser()=="travis":
            return
        wikipush=WikiPush("smw","test")
        ask="""{{#ask:[[Has conference::+]]
 |mainlabel=Talk
 |?Has description=Description
 |?Has conference=Event
 |sort=Has conference
 |order=descending
 |format=table
 |limit=200
}}"""
        pages=wikipush.query(ask,queryField="Event")
        if self.debug:
            print (pages)
            print (len(pages))
        self.assertTrue(len(pages)>15)
        self.assertTrue(len(pages)<100)
    
    def testTransferPagesFromMaster(self):
        '''
        test transferpages
        '''
        # only activate when needed
        #return 
        ask="{{#ask: [[TransferPage page::+]][[TransferPage wiki::Master]]| mainlabel=-| ?TransferPage page = page| format=table|limit=300}}"
        wikipush=WikiPush("master","test")
        pages=wikipush.query(ask,queryField="page")
        print (pages)
    
    def testQuery(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/10
        Query support for page selection
        '''
        if getpass.getuser()=="travis":
            return
        wp=WikiPush("smw","test")
        pages=wp.query("[[Category:City]]|limit=10")
        self.assertTrue(len(pages)<=10)
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