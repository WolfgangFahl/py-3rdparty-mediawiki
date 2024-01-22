"""
Created on 2020-11-01

@author: wf
"""
import os
import tempfile
import unittest

import wikibot3rd
from tests.basetest import BaseTest
from wikibot3rd.wikiuser import WikiUser


class TestWikiUser(BaseTest):
    """
    test for WikiUser handling e.g. credentials and parsing
    user info from Java properties compatible ini file
    """

    def testWikiUser(self):
        """
        test the wiki user handling
        """
        if self.inPublicCI():
            return
        wikiUsers = WikiUser.getWikiUsers()
        for wikiUser in wikiUsers.values():
            if self.debug:
                print(wikiUser)

        testUser = WikiUser.ofWikiId("test")
        if self.debug:
            print(testUser)
        self.assertEqual("http://test.bitplan.com", testUser.getWikiUrl())
        pass

    @staticmethod
    def getSMW_WikiUser(wikiId="smw"):
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

    def testCommandLine(self):
        """
        test command line handling
        """
        fd, path = tempfile.mkstemp(".ini")
        password = "anUnsecurePassword"
        try:
            if fd:
                args = [
                    "--url",
                    "http://wiki.doe.com",
                    "-u",
                    "john",
                    "-e",
                    "john@doe.com",
                    "-w",
                    "doe",
                    "-s",
                    "",
                    "-v",
                    "MediaWiki 1.35.0",
                    "-p",
                    password,
                    "-f",
                    path,
                    "-y",
                ]
                wikibot3rd.wikiuser.main(args)
        finally:
            if self.debug:
                print(open(path, "r").read())
            props = WikiUser.readPropertyFile(path)
            rUser = WikiUser.ofDict(props, encrypted=True)
            self.assertEqual(password, rUser.getPassword())
            os.remove(path)
