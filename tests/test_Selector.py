'''
Created on 2020-12-20

@author: wf
'''
import unittest
from wikibot.selector import Selector
import numpy as np
import getpass
class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testIssue26(self):
        '''
        test https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/25
        Add Selection option for multi-file operations #25
        Testing on 100 records to see if Selector handles large records.
        '''
        # don't test this in Travis since it's interactive
        if getpass.getuser()=="travis":
            return
        selectionList=np.arange(0, 100, 1)
        selectionList=Selector.select(selectionList)
        print(selectionList)

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