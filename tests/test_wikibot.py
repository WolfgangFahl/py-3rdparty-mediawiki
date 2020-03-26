'''
Created on 24.03.2020

@author: wf
'''
import unittest
from wikibot.wikibot import WikiBot
from wikibot.crypt import Crypt

class TestWikiBot(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testDecrypt(self):
        ''' test decryption '''
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

    def testWikiBot(self):
        bots=WikiBot.getBots()
        for bot in bots.values():
            print (bot)
            if bot.site is not None:
                print (bot.site.sitename)
                print (bot.getPage("MainPage").text)   
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()