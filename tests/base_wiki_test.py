"""
Created on 26.09.2024

@author: wf
"""

import os

from tests.base_test_config import WikiConfig
from tests.basetest import BaseTest
from wikibot3rd.wikibot import WikiBot
from wikibot3rd.wikiuser import WikiUser


class BaseWikiTest(BaseTest):
    """
    Base (Semantic) Mediawiki tests
    """

    def setUp(self, debug=False, profile=True):
        BaseTest.setUp(self, debug=debug, profile=profile)

    def getWikiUser(self, wikiId: str = None) -> WikiUser:
        """
        Get WikiUser for given wikiId

        Args:
            wikiId(str): id of the wiki

        Returns WikiUser
        """
        if wikiId is None:
            wikiId = self.wikiId
        return self.getSMW_WikiUser(wikiId=wikiId, save=self.inPublicCI())

    def get_wiki_user(self, wikiId="or", save=False) -> WikiUser:
        """
        get wiki users for given wikiId (stub for backwards compatibility)
        """
        return self.getSMW_WikiUser(wikiId, save)

    def getSMW_WikiUser(self, wikiId="or", save=False) -> WikiUser:
        """
        Get semantic media wiki users for various wikis
        """
        iniFile = WikiUser.iniFilePath(wikiId)
        wikiUser = None
        if not os.path.isfile(iniFile):
            configs = WikiConfig.get_configs()
            if wikiId not in configs:
                raise Exception(f"Unknown wikiId: {wikiId}")

            wikiDict = configs[wikiId].copy()
            wikiDict["wikiId"] = wikiId

            wikiUser = WikiUser.ofDict(wikiDict, lenient=True)
            if save or self.inPublicCI():
                wikiUser.save()
        else:
            wikiUser = WikiUser.ofWikiId(wikiId, lenient=True)
        return wikiUser

    def getSMW_Wiki(self, wikiId="smw"):
        wikiUser = self.getSMW_WikiUser(wikiId)
        wikibot = None
        if wikiUser is not None:
            wikibot = WikiBot.ofWikiUser(wikiUser)
        return wikibot
