'''
Created on 2020-11-01

@author: wf
'''
import unittest
import getpass
from wikibot.wikiuser import WikiUser
import wikibot
import os
import tempfile

class TestWikiUser(unittest.TestCase):
    '''
    test for WikiUser handling e.g. credentials and parsing
    user info from Java properties compatible ini file
    '''

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
    
    @staticmethod
    def getSMW_WikiUser(wikiId="smw"):
        '''
        get semantic media wiki users for SemanticMediawiki.org and openresearch.org
        '''
        iniFile=WikiUser.iniFilePath(wikiId)
        wikiUser=None
        if not os.path.isfile(iniFile):
            wikiDict=None
            if wikiId=="smwcopy":
                wikiDict={"wikiId": wikiId,"email":"webmaster@bitplan.com","url":"http://smw.bitplan.com","scriptPath":"","version":"MediaWiki 1.35.0"}
            if wikiId=="smw":
                wikiDict={"wikiId": wikiId,"email":"webmaster@semantic-mediawiki.org","url":"https://www.semantic-mediawiki.org","scriptPath":"/w","version":"MediaWiki 1.31.7"}
            if wikiId=="or":
                wikiDict={"wikiId": wikiId,"email":"webmaster@openresearch.org","url":"https://www.openresearch.org","scriptPath":"/mediawiki/","version":"MediaWiki 1.31.1"}   
            if wikiDict is None:
                raise Exception("%s missing for wikiId %s" % (iniFile,wikiId))
            else:
                wikiUser=WikiUser.ofDict(wikiDict, lenient=True)
                if getpass.getuser()=="travis":
                    wikiUser.save()
        else: 
            wikiUser=WikiUser.ofWikiId(wikiId,lenient=True)
        return wikiUser
    
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