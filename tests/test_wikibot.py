'''
Created on 24.03.2020

@author: wf
'''
import unittest
import os
from wikibot.wikibot import WikiBot
from wikibot.crypt import Crypt

class TestWikiBot(unittest.TestCase):
    '''
    Unit test for WikiBot
    '''

    def setUp(self):
        '''
        general setup
        '''
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
        
    @staticmethod
    def getSMW_Wiki():
        wikiId="smw"
        iniFile=WikiBot.iniFilePath(wikiId)
        if not os.path.isfile(iniFile):
            WikiBot.writeIni(wikiId,"Semantic MediaWiki.org","https://www.semantic-mediawiki.org","/w","MediaWiki 1.31.7")
        wikibot=WikiBot.ofWikiId(wikiId)
        return  wikibot   
        
    def testWikiBotNoLogin(self):
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