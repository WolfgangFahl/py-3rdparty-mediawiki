import json

from tests.base_wiki_test import BaseWikiTest
from wikibot3rd.pagehistory import PageHistory


class TestPageHistory(BaseWikiTest):
    """
    test querying the wiki api for the history of a page
    """

    def setUp(self, debug=False, profile=True):
        super(TestPageHistory, self).setUp(debug=debug, profile=profile)
        self.wikiId = "cr"
        self.getWikiUser()
        self.testPage = "POPL97"
        # self.debug=True

    def getPageHistory(self):
        """
        get the pageHistory of the testPage
        """
        pageHistory = PageHistory(pageTitle=self.testPage, wikiId=self.wikiId)
        if self.debug:
            print(json.dumps(pageHistory.revisions, indent=2, default=str))
        return pageHistory

    def test_PageHistory(self):
        """
        tests the extraction of the page revisions
        """
        pageHistory = self.getPageHistory()
        self.assertGreaterEqual(len(pageHistory.revisions), 7)

    def test_exists(self):
        """
        tests if a page exists and has at least one page revision
        """
        pageHistory = self.getPageHistory()
        self.assertTrue(pageHistory.exists())

    def test_getFirstUser(self):
        """
        tests getFirstUser()
        """
        pageHistory = self.getPageHistory()
        # test pageCreator
        expectedPageCreator = "Wf"
        self.assertEqual(expectedPageCreator, pageHistory.getFirstUser())
        expectedUserLimitedGroup = "Wf"
        self.assertEqual(
            expectedUserLimitedGroup,
            pageHistory.getFirstUser(limitedUserGroup=["Wf", "Th"]),
        )
        pageHistory.revisions.sort(
            key=lambda r: int(getattr(r, "revid", 0)), reverse=True
        )
        latestUser = pageHistory.revisions[0].user
        self.assertEqual(latestUser, pageHistory.getFirstUser(reverse=True))
