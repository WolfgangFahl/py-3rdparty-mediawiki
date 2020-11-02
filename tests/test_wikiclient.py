'''
Created on 2020-11-02

@author: wf
'''
import unittest
from wikibot.wikiclient import WikiClient

class TestWikiClient(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testWikiClient(self):
        '''
        test clients
        '''
        for i,client in enumerate(WikiClient.getClients().values()):
            print ("%2d %s" % (i,client))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()