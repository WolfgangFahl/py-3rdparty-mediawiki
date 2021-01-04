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
        #return
        selectionList = ["Apple", "Banana", "Orange", "Pear"]
        # Test quit button
        print("Click on the Quit button")
        self.assertTrue(len(Selector.select(selectionList.copy(), description="Click on the Quit button")) == 0)
        # select one
        print("Select only one element")
        self.assertTrue(len(Selector.select(selectionList.copy(), description="Select one item.")) == 1)
        # select all
        print("Select all elements")
        print(len(selectionList))
        x = Selector.select(selectionList.copy(), description="Select all items.")
        print(x)
        self.assertTrue(len(x) == len(selectionList))
        # select none
        print("Select no element")
        self.assertTrue(len(Selector.select(selectionList.copy(), description="Select no item.")) == 0)
        # Test with 1000 List items
        print("Select all elements")
        items = []
        amount = 500
        for i in range(amount):
            items.append("item_"+str(i))
        self.assertTrue(len(Selector.select(items, description="Select all items.")) == amount)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()