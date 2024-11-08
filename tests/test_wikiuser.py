"""
Created on 2020-11-01

@author: wf
"""

import os
import tempfile

import wikibot3rd.wikiuser_cmd
from tests.base_wiki_test import BaseWikiTest
from wikibot3rd.wikiuser import WikiUser


class TestWikiUser(BaseWikiTest):
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
                    "--lenient",
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
                wikibot3rd.wikiuser_cmd.main(args)
        finally:
            debug = self.debug
            debug = True
            if debug:
                print(open(path, "r").read())
            props = WikiUser.readPropertyFile(path)
            rUser = WikiUser.ofDict(props, encrypted=True)
            self.assertEqual(password, rUser.getPassword())
            os.remove(path)
