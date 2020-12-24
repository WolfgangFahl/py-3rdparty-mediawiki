'''
Created on 2020-12-20

@author: wf
'''
import unittest
from wikibot.selector import Selector
import getpass
class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testIssue25(self):
        '''
        test https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/25
        Add Selection option for multi-file operations #25
        '''
        # don't test this in Travis since it's interactive
        if getpass.getuser()=="travis":
            return
        selectionList=["Apple","Banana","Orange","Pear"]
        selectionList=Selector.select(selectionList)
        print(selectionList)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()