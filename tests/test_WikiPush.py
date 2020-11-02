'''
Created on 2020-10-29

@author: wf
'''
import unittest
import getpass
from wikibot.wikipush import WikiPush

class TestWikiPush(unittest.TestCase):


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
        wp=WikiPush("wikipedia_org_test2","testbot")
        wp.push("PictureTestPage")
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()