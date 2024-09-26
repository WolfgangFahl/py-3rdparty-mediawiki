"""
Created on 26.09.2024

@author: wf
"""

import os

from tests.basetest import BaseTest
from wikibot3rd.wikiuser import WikiUser


class BaseSmwTest(BaseTest):
    """
    Base Semantic Mediawiki tests
    """

    def setUp(self, debug=False, profile=True):
        BaseTest.setUp(self, debug=debug, profile=profile)

    def getSMW_WikiUser(self, wikiId="smw"):
        """
        get semantic media wiki users for SemanticMediawiki.org and openresearch.org
        """
        iniFile = WikiUser.iniFilePath(wikiId)
        wikiUser = None
        if not os.path.isfile(iniFile):
            wikiDict = None
            if wikiId == "smwcopy":
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "webmaster@bitplan.com",
                    "url": "https://smw.bitplan.com",
                    "scriptPath": "",
                    "version": "MediaWiki 1.35.5",
                }
            elif wikiId == "smw":
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "webmaster@semantic-mediawiki.org",
                    "url": "https://www.semantic-mediawiki.org",
                    "scriptPath": "/w",
                    "version": "MediaWiki 1.31.16",
                }
            elif wikiId == "or":
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "webmaster@openresearch.org",
                    "url": "https://www.openresearch.org",
                    "scriptPath": "/mediawiki/",
                    "version": "MediaWiki 1.31.1",
                }
                raise Exception("don")
            elif wikiId == "orclone":
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "webmaster@bitplan.com",
                    "url": "https://confident.dbis.rwth-aachen.de",
                    "scriptPath": "/or",
                    "version": "MediaWiki 1.35.5",
                }
            elif wikiId == "orcopy":
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "webmaster@bitplan.com",
                    "url": "https://or.bitplan.com",
                    "scriptPath": "",
                    "version": "MediaWiki 1.35.5",
                }
            if wikiDict is None:
                raise Exception(f"{iniFile} missing for wikiId {wikiId}")
            else:
                wikiUser = WikiUser.ofDict(wikiDict, lenient=True)
                if BaseTest.isInPublicCI():
                    wikiUser.save()
        else:
            wikiUser = WikiUser.ofWikiId(wikiId, lenient=True)
        return wikiUser
