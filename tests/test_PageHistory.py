from tests.basetest import BaseTest
from wikibot3rd.pagehistory import PageHistory


class TestPageHistory(BaseTest):
    '''
    test querying the wiki api for the history of a page
    '''

    def setUp(self, debug=False, profile=True):
        super(TestPageHistory, self).setUp(debug=debug, profile=profile)
        self.wikiId = "orclone"
        self.getWikiUser()
        self.testPage = "AMCIS"

    def test_PageHistory(self):
        """
        tests the extraction of the page revisions
        """
        pageHistory = PageHistory(pageTitle=self.testPage, wikiId=self.wikiId)
        if self.debug:
            print(pageHistory.revisions)
        self.assertGreaterEqual(len(pageHistory.revisions), 6)

    def test_exists(self):
        """
        tests if a page exists and has at least one page revision
        """
        pageHistory = PageHistory(pageTitle=self.testPage, wikiId=self.wikiId)
        if self.debug:
            print(pageHistory.revisions)
        self.assertTrue(pageHistory.exists())

    def test_getFirstUser(self):
        """
        tests getFirstUser()
        """
        pageHistory = PageHistory(pageTitle=self.testPage, wikiId=self.wikiId)
        if self.debug:
            print(pageHistory.revisions)
        # test pageCreator
        expectedPageCreator = "Soeren"
        self.assertEqual(expectedPageCreator, pageHistory.getFirstUser())
        expectedUserLimitedGroup = "Wf"
        self.assertEqual(expectedUserLimitedGroup, pageHistory.getFirstUser(limitedUserGroup=["Wf", "Orapi"]))
        pageHistory.revisions.sort(key=lambda r: int(getattr(r, "revid", 0)), reverse=True)
        latestUser = pageHistory.revisions[0].user
        self.assertEqual(latestUser, pageHistory.getFirstUser(reverse=True))
