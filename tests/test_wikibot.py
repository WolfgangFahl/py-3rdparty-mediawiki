"""
Created on 24.03.2020

@author: wf
"""

import unittest

from tests.basetest import BaseTest
from tests.test_WikiUser import TestWikiUser
from wikibot3rd.crypt import Crypt
from wikibot3rd.wikibot import WikiBot


class TestWikiBot(BaseTest):
    """
    Unit test for WikiBot
    """

    def test_encryption(self):
        """test encryption/decryption"""
        expected = "01234567890unsecure"
        cypher = "koyYMmY93wJS_aqpp_PmyxZJKPH5FhSG"
        secret = "juMmHMtvrfDADGkRlnJRCMYkd4kUzRE3"
        salt = "aPntWu5u"
        c = Crypt(cypher, 20, salt)
        secret1 = c.encrypt(expected)
        # print(secret1)
        self.assertEqual(secret, secret1)
        pw = c.decrypt(secret)
        self.assertEqual(expected, pw)

    def testRandomCrypt(self):
        """
        test creating a random crypt
        """
        c = Crypt.getRandomCrypt()
        cypher = c.cypher.decode()
        salt = c.salt.decode()
        self.debug = True
        if self.debug:
            print(cypher)
            print(salt)
        self.assertEqual(32, len(cypher))
        self.assertEqual(8, len(salt))

    @staticmethod
    def getSMW_Wiki(wikiId="smw"):
        wikiUser = TestWikiUser.getSMW_WikiUser(wikiId)
        wikibot = None
        if wikiUser is not None:
            wikibot = WikiBot.ofWikiUser(wikiUser)
        return wikibot

    def testWikiBotNoLogin(self):
        """
        test a wikibot3rd where no login is needed
        """
        wikibot = TestWikiBot.getSMW_Wiki()
        pageTitle = "Help:Configuration"
        page = wikibot.getPage(pageTitle)
        # print(page.text)
        self.assertTrue("Semantic MediaWiki" in page.text)

    def testWikiBot(self):
        """
        test collecting all bots for which credentials have been set up
        """
        bots = WikiBot.getBots(name="url", valueExpr="www.*\.org")
        for bot in bots.values():
            print(bot)
            if bot.site is not None:
                print(bot.site.sitename)
                try:
                    mainPageText = bot.getPage("Main Page").text
                    status = f"✅:{len(mainPageText)}"
                except Exception as ex:
                    error = str(ex)
                    status = f"❌:{error}"
                print(status)
                # bot2=WikiBot.ofWikiId(bot.wikiId)
                # self.assertEquals(bot2.url,bot.url)
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
