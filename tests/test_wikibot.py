'''
Created on 24.03.2020

@author: wf
'''
import unittest
import os
from wikibot.wikibot import WikiBot
from wikibot.wikiuser import WikiUser
from wikibot.crypt import Crypt

class TestWikiBot(unittest.TestCase):
    '''
    Unit test for WikiBot
    '''

    def setUp(self):
        '''
        general setup
        '''
        self.debug=False
        pass


    def tearDown(self):
        '''
        general tear down
        '''
        pass

    def testCrypt(self):
        ''' test encryption/decryption '''
        expected="01234567890unsecure"
        cypher="koyYMmY93wJS_aqpp_PmyxZJKPH5FhSG"
        secret="juMmHMtvrfDADGkRlnJRCMYkd4kUzRE3"
        salt="aPntWu5u"
        c=Crypt(cypher,20,salt)
        secret1=c.encrypt(expected);
        # print(secret1)
        self.assertEquals(secret,secret1)
        pw=c.decrypt(secret)
        self.assertEquals(expected,pw)
        
    def testRandomCrypt(self):
        '''
        test creating a random crypt
        '''
        c=Crypt.getRandomCrypt()
        cypher=c.cypher.decode()
        salt=c.salt.decode()
        self.debug=True
        if self.debug:
            print (cypher)
            print (salt)
        self.assertEqual(32,len(cypher))
        self.assertEqual(8,len(salt))
        
    @staticmethod
    def getSMW_Wiki(wikiId="smw"):
        iniFile=WikiUser.iniFilePath(wikiId)
        if not os.path.isfile(iniFile):
            wikiDict=None
            if wikiId=="smw":
                wikiDict={"wikiId": wikiId,"url":"https://www.semantic-mediawiki.org","scriptPath":"/w","version":"MediaWiki 1.31.7"}
            if wikiId=="or":
                wikiDict={"wikiId": wikiId,"url":"https://www.openresearch.org","scriptPath":"/mediawiki/","version":"MediaWiki 1.31.1"}   
            if wikiDict is None:
                raise Exception("%s missing for wikiId %s" % (iniFile,wikiId))
            else:
                wikiUser=WikiUser.ofDict(wikiDict, lenient=True)
                wikibot=WikiBot.ofWikiUser(wikiUser)
        else:
            wikibot=WikiBot.ofWikiId(wikiId)
        return  wikibot   
        
    def testWikiBotNoLogin(self):
        '''
        test a wikibot where no login is needed
        '''
        wikibot=TestWikiBot.getSMW_Wiki()
        pageTitle="Help:Configuration"
        page=wikibot.getPage(pageTitle)
        # print(page.text)
        self.assertTrue("Semantic MediaWiki" in page.text)
        
    def testWikiBot(self):
        '''
        test collecting all bots for which credentials have been set up
        '''
        bots=WikiBot.getBots()
        for bot in bots.values():
            print (bot)
            if bot.site is not None:
                print (bot.site.sitename)
                print (bot.getPage("MainPage").text)   
                #bot2=WikiBot.ofWikiId(bot.wikiId)
                #self.assertEquals(bot2.url,bot.url)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()