"""
Created on 2020-12-20
@author: wf
"""

import getpass
import logging
import sys
import unittest

from tests.basetest import BaseTest
from wikibot3rd.selector import Selector


class TestSelector(BaseTest):
    """
    Test the selector GUI e.g. checking if the correct selection is returned and all GUI elements work accordingly
    """

    def setUp(self):
        BaseTest.setUp(self)
        self.LOGGER = logging.getLogger(self.__class__.__name__)
        self.LOGGER.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
        )
        self.LOGGER.addHandler(handler)

    def testIssue25(self):
        """
        Tests the basic functionality of the selector GUI by guiding the user through the tests.
        Since the test requires user input nothing is tested if executed with travis.
        The core components of the selector are define by https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/25
        Add Selection option for multi-file operations #25
        """
        # don't test this in Travis or github actions since it's interactive
        if getpass.getuser() in ["travis", "runner"]:
            return

        # switch of interactive tests by default
        return

        self.LOGGER.info(
            "Starting interactive GUI test for the selector interface. Please follow the upcoming "
            "instructions in the GUI to successfully complete the test."
        )
        selectionList = ["Apple", "Banana", "Orange", "Pear"]
        self.LOGGER.info("Testing Quit button")
        self.assertTrue(
            Selector.select(selectionList, description="Click on the Quit button")
            == "Q",
            msg="Returned list should be empty after quiting",
        )

        self.LOGGER.info("Testing window close button")
        self.assertTrue(
            Selector.select(
                selectionList,
                description="Click on the window close button (The X in "
                "the right corner)",
            )
            == "Q",
            msg="Returned list should be empty after closing the window",
        )

        self.LOGGER.info("Testing selection of one item")
        selection = Selector.select(selectionList, description="Select one item.")
        self.assertTrue(
            len(selection) == 1,
            msg=f"Incorrect amount of items was returned. {len(selection)} items returned 1 expected.",
        )

        self.LOGGER.info("Testing selection of all items")
        x = Selector.select(selectionList, description="Select all items.")
        self.assertTrue(len(x) == len(selectionList), msg="Not all items were selected")

        self.LOGGER.info("Testing selection of no item")
        self.assertTrue(
            len(Selector.select(selectionList, description="Select no item.")) == 0,
            msg="Returned list was not empty.",
        )

        self.LOGGER.info("Testing select all button")
        selection = Selector.select(
            selectionList,
            description="Please test the 'Select all' button. It "
            "should select all items. Deselecting one or "
            "more items should change the state of the "
            "button. Reversing your actions should "
            "result in the original state of the button. "
            "Clicking the 'Select All' button (now 'Select "
            "None') should deselect all items. If "
            "everything functions as intended select all "
            "items and click confirm otherwise quit.",
        )
        self.assertTrue(
            len(selection) == len(selectionList),
            msg="Global select button not working properly (acording to user)",
        )

        self.LOGGER.info("Testing handling of large amount of items")
        items = []
        amount = 10000
        for i in range(amount):
            items.append("item_" + str(i))
        self.assertTrue(
            len(Selector.select(items, description="Select all items.")) == amount,
            msg="Not all items were selected",
        )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
