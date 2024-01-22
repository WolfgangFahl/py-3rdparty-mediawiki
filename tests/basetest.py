"""
Created on 2021-10-21

@author: wf
"""
import getpass
import os
import time
import warnings
from unittest import TestCase

from wikibot3rd.wikiuser import WikiUser


class Profiler:
    """
    simple profiler
    """

    def __init__(self, msg, profile=True):
        """
        construct me with the given msg and profile active flag

        Args:
            msg(str): the message to show if profiling is active
            profile(bool): True if messages should be shown
        """
        self.msg = msg
        self.profile = profile
        self.starttime = time.time()
        if profile:
            print(f"Starting {msg} ...")
        warnings.simplefilter("ignore", ResourceWarning)

    def time(self, extraMsg=""):
        """
        time the action and print if profile is active
        """
        elapsed = time.time() - self.starttime
        if self.profile:
            print(f"{self.msg}{extraMsg} took {elapsed:5.3f} s")
        return elapsed


class BaseTest(TestCase):
    """
    base Test class
    """

    def setUp(self, debug=False, profile=True):
        """
        setUp test environment
        """
        TestCase.setUp(self)
        self.debug = debug
        msg = f"test {self._testMethodName} ... with debug={self.debug}"
        # make sure there is an EventCorpus.db to speed up tests
        self.profiler = Profiler(msg=msg, profile=profile)
        self.wikiId = "smwcopy"

    def tearDown(self):
        self.profiler.time()
        pass

    @staticmethod
    def isInPublicCI():
        """
        are we running in a public Continuous Integration Environment?
        """
        return getpass.getuser() in ["travis", "runner"]

    def inPublicCI(self):
        return BaseTest.isInPublicCI()

    def getWikiUser(self, wikiId: str = None) -> WikiUser:
        """
        Get WikiUser for given wikiId

        Args:
            wikiId(str): if of the wiki

        Returns WikiUser
        """
        if wikiId is None:
            wikiId = self.wikiId
        # make sure there is a wikiUser (even in public CI)
        wikiUser = self.getSMW_WikiUser(wikiId=wikiId, save=self.inPublicCI())
        return wikiUser

    def getSMW_WikiUser(self, wikiId="or", save=False) -> WikiUser:
        """
        get semantic media wiki users for SemanticMediawiki.org and openresearch.org
        """
        iniFile = WikiUser.iniFilePath(wikiId)
        wikiUser = None
        if not os.path.isfile(iniFile):
            wikiDict = None
            if wikiId == "or":
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "noreply@nouser.com",
                    "url": "https://www.openresearch.org",
                    "scriptPath": "/mediawiki/",
                    "version": "MediaWiki 1.31.1",
                }
            if wikiId == "cr":
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "noreply@nouser.com",
                    "url": "http://cr.bitplan.com",
                    "scriptPath": "",
                    "version": "MediaWiki 1.35.5",
                }
            if wikiId in ["orclone", "orcopy"]:
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "noreply@nouser.com",
                    "url": "https://confident.dbis.rwth-aachen.de",
                    "scriptPath": "/or/",
                    "version": "MediaWiki 1.35.1",
                }
            if wikiId == "smwcopy":
                wikiDict = {
                    "wikiId": wikiId,
                    "email": "noreply@nouser.com",
                    "url": "https://smw.bitplan.com/",
                    "scriptPath": "",
                    "version": "MediaWiki 1.35.5",
                }
            if wikiDict is None:
                raise Exception(f"wikiId {wikiId} is not known")
            else:
                wikiUser = WikiUser.ofDict(wikiDict, lenient=True)
                if save:
                    wikiUser.save()
        else:
            wikiUser = WikiUser.ofWikiId(wikiId, lenient=True)
        return wikiUser
