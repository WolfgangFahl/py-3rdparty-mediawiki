'''
Created on 01.11.2020

@author: wf
'''
import unittest
import getpass
from wikibot.wikiuser import WikiUser
from wikibot.crypt import Crypt
import wikibot
import os
import tempfile

class TestWikiUser(unittest.TestCase):

    def setUp(self):
        self.debug=False
        pass

    def tearDown(self):
        pass

    def testWikiUser(self):
        '''
        test the wiki user handling
        '''
        if getpass.getuser()=="travis":
            return
        wikiUsers=WikiUser.getWikiUsers()
        for wikiUser in wikiUsers.values():
            print(wikiUser)
            
        testUser=WikiUser.ofWikiId("test")
        print(testUser)
        pass
    
    def testCommandLine(self):
        '''
        test command line handling
        '''
        fd,path=tempfile.mkstemp(".ini")
        password="anUnsecurePassword"
        try:
            if (fd):
                args=["--url","http://wiki.doe.com","-u","john","-e","john@doe.com","-w","doe","-s","","-v","MediaWiki 1.35.0","-p",password,"-f",path,'-y']
                wikibot.wikiuser.main(args)
        finally:
            if self.debug:
                print(open(path, 'r').read())
            props=WikiUser.readPropertyFile(path)
            rUser=WikiUser.ofDict(props, encrypted=True)
            self.assertEqual(password,rUser.getPassword())
            os.remove(path)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()