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