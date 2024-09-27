"""
Created on 2021-10-21

@author: wf
"""

import getpass
import time
import unittest
import warnings
from unittest import TestCase


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


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
