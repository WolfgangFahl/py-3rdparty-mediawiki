"""
Created on 2020-10-29

@author: wf
"""

import io
import os
import unittest
import warnings
from contextlib import redirect_stdout

import wikibot3rd
from tests.base_wiki_test import BaseWikiTest
from wikibot3rd.wikipush import WikiPush


class TestWikiPush(BaseWikiTest):
    """
    test pushing pages including images
    """

    def setUp(self, debug=False, profile=True):
        super().setUp(debug, profile)
        self.getWikiUser("smwcopy")

    def testLimitInQuery(self):
        """
        test if limits defined inside of the query work properly and can be overwritten by the argument definition
        :return:
        """
        if self.inPublicCI():
            return
        wp = WikiPush("smwcopy")
        pageTitles = wp.query("[[modification date::+]]", limit=3)
        self.assertTrue(len(pageTitles) == 3)
        pageTitlesInlineLimit = wp.query("[[modification date::+]]|limit=3")
        self.assertTrue(len(pageTitlesInlineLimit) == 3)
        pageTitlesOverwritten = wp.query(
            "[[modification date::+]]|limit=3",
            limit=2,
        )
        self.assertTrue(len(pageTitlesOverwritten) == 2)

    def testIssue66(self):
        """
        test wikibackup behavior if it has nothing to backup
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/66
        """
        if self.inPublicCI():
            return
        try:
            wp = WikiPush("smwcopy")
            pageTitles = wp.query(
                "[[Modification date::>=3000-01-01]]", queryDivision=10
            )
            wp.backup(pageTitles)
        except Exception as e:
            self.fail(
                f"Empty query result should not lead to an error but {e} was thrown"
            )

    def testIssue65(self):
        """
        test WikiPush initialization for non existent wikiIdorth
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/65
        """
        if self.inPublicCI():
            return
        try:
            wp = WikiPush("invalidWikiId")
        except FileNotFoundError as e:
            self.assertIsInstance(e, FileNotFoundError)
            expectedMessage = 'the wiki with the wikiID "invalidWikiId" does not have a corresponding configuration file ... you might want to create one with the wikiuser command'
            self.assertEqual(expectedMessage, str(e))

    def testIssue11(self):
        """
        test the limit handling
        """
        # don't test this in Travis
        if self.inPublicCI():
            return
        askQuery = "[[isA::Event]]"
        wikipush = WikiPush("orcopy", None)
        pages = wikipush.query(askQuery, showProgress=False, limit=10)
        self.assertEqual(10, len(pages))

    def testIssue29(self):
        """
        makes sure query does not hang on large queries
        """
        # don't test this in Travis
        if self.inPublicCI():
            return
        return  # test takes 22 secs - don't activate if not necessary
        askQuery = "[[isA::Event]]"
        wikipush = WikiPush("orcopy", None)
        pages = wikipush.query(askQuery, showProgress=True)
        print(len(pages))
        pass

    def testIssue16(self):
        """
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/16
        allow mass delete of pages
        """
        # don't test this in Travis
        if self.inPublicCI():
            return
        wikipush = WikiPush(None, "test")
        pageTitles = ["deleteMe1", "deleteMe2", "deleteMe3"]
        for pageTitle in pageTitles:
            newPage = wikipush.toWiki.getPage(pageTitle)
            newPage.edit("content for %s" % pageTitle, "created by testIssue16")
        wikipush.nuke(pageTitles, force=False)
        wikipush.nuke(pageTitles, force=True)

    def testIssue14(self):
        """
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/14
        Pushing pages in File: namespace should be working
        """
        return  # don't test this nightly
        # don't test this in Travis
        if self.inPublicCI():
            return
        wikipush = WikiPush("master", "test")
        wikipush.push(["File:index.png"], force=True, ignore=True, withImages=True)

    def testIssue12(self):
        """
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/12
        add -pf / pageField option to allow to select other property than mainlabel
        """
        # don't test this in Travis
        if self.inPublicCI():
            return
        wikipush = WikiPush("smwcopy", "test")
        ask = """{{#ask:[[Has conference::+]]
 |mainlabel=Talk
 |?Has description=Description
 |?Has conference=Event
 |sort=Has conference
 |order=descending
 |format=table
 |limit=200
}}"""
        pages = wikipush.query(ask, pageField="Event")
        debug = self.debug
        debug = True
        if debug:
            print(pages)
            print(len(pages))
        self.assertTrue(len(pages) > 15)
        self.assertTrue(len(pages) < 100)

    def testTransferPagesFromMaster(self):
        """
        test transferpages
        """
        if self.inPublicCI():
            return
        debug = self.debug
        # debug=True
        ask = "{{#ask: [[TransferPage page::+]][[TransferPage wiki::Master]]| mainlabel=-| ?TransferPage page = page| format=table|limit=300}}"
        wikipush = WikiPush("master", "test", login=True, debug=debug)
        pages = wikipush.query(ask, pageField="page")
        if debug:
            print(pages)
        self.assertTrue(len(pages) > 100)

    def testQuery(self):
        """
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/10
        Query support for page selection
        """
        if self.inPublicCI():
            return
        wp = WikiPush("smwcopy", "test")
        pages = wp.query("[[Capital of::+]]")
        if self.debug:
            print(pages)
        self.assertTrue(len(pages) >= 5)
        self.assertTrue("Demo:Berlin" in pages)

    def testWikiBackup(self):
        # don't test this in Travis
        if self.inPublicCI():
            return
        wp = WikiPush("smw")
        pageTitles = wp.query("[[Capital of::+]]")
        wp.backup(pageTitles)

    def testWikiBackupCommandLine(self):
        """
        test starting backup from the command line
        """
        argv = ["-s", "smwcopy", "-q", "[[modification date::+]]"]
        wikibot3rd.wikipush.mainBackup(argv)

    def testWikiPush(self):
        """
        test pushing a page from one wiki to another
        """
        # don't test this in Travis
        if self.inPublicCI():
            return
        wp = WikiPush("wikipedia_org_test2", "test")
        for force in [False, True]:
            for ignore in [False, True]:
                wp.push(["PictureTestPage"], force=force, ignore=ignore)
        pass

    def testDiff(self):
        """
        check the diff functionality
        """
        text = "Hello World!\nLet's test the search and replace function.\nTry Apples and Oranges!\nOr do you like chocolate better?"
        # print (text)
        modify = WikiPush.getModify("Apples", "Peaches")
        newText = modify(text)
        diff = WikiPush.getDiff(text, newText, n=0)
        if self.debug:
            print(diff)
        self.assertEqual(2, len(diff.split("\n")))

    def testDownload(self):
        """
        check the image download
        """
        # don't test this in Travis
        if self.inPublicCI():
            return
        wp = WikiPush("wikipedia_org_test2", "test")
        page = wp.fromWiki.getPage("PictureTestPage")
        images = list(page.images())
        self.assertEqual(3, len(images))
        for image in images:
            if "Mona" in image.name:
                imagePath, filename = wp.downloadImage(image, "/tmp")
                imageSize = os.path.getsize(imagePath)
                if self.debug:
                    print("size of %s is %d bytes" % (filename, imageSize))
                self.assertEqual(3506068, imageSize)

    def testWarnings(self):
        """
        test the warning handling
        """
        return
        # https://stackoverflow.com/a/5222474/1497139
        argv = [
            "-l",
            "-s",
            "swa",
            "-t",
            "test",
            "-q",
            "[[modification date::>2020-11-29]]",
            "-wi",
            "-f",
            "-i",
        ]
        wikibot3rd.wikipush.main(argv)

    def testEdit(self):
        return
        # this actually edits data ... don't activate if you don't really want to do this
        argv = [
            "-t",
            "orcopy",
            "-d",
            "-q",
            "[[isA::Event]]",
            "--search",
            "\\[Category:",
            "--replace",
            "[has category::",
            "-f",
            "--progress",
        ]
        wikibot3rd.wikipush.mainEdit(argv)
        return

    def testRestore(self):
        return
        # this actually edits data ... don't activate if you don't really want to do this
        argv = ["-s", "smwcopy", "-t", "smwcopy", "-q", "[[modification date::+]]"]
        wikibot3rd.wikipush.mainRestore(argv)
        return

    def testHandleWarningIssue70(self):
        """
        tests the logging of warnings
        see https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/70
        """
        if self.inPublicCI():
            return
        wp = WikiPush("test")
        wp.handleWarning("uploaddisabled")

    def testHandleAPIWarningsIssue70(self):
        """
        tests the logging of warnings
        see https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/70
        handleAPIWarnings needs to handle strings and lists
        """
        if self.inPublicCI():
            return
        wp = WikiPush("test")
        wp.handleAPIWarnings("uploaddisabled")
        wp.handleAPIWarnings(["uploaddisabled", "Server not responding"])

    def testImageOverwrite(self):
        """
        tests the handling of duplicate file warnings
        """
        if self.inPublicCI():
            return
        wp = WikiPush("test")
        msg = "duplicate\nexists\nnochange"
        self.assertTrue(wp.handleWarning(msg, ignoreExists=True))
        self.assertFalse(wp.handleAPIWarnings(msg, ignoreExists=False))

    def testIssue75(self):
        """
        see https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/75
        """
        if self.inPublicCI():
            return
        argv = ["-s", "orfixed", "-t", "test", "-p", "Form:Rating"]
        f = io.StringIO()
        with redirect_stdout(f):
            wikibot3rd.wikipush.mainPush(argv=argv)
        out = f.getvalue()
        if self.debug:
            print(out)
        if "internal_api_error_MWException" in out or "✅" not in out:
            warnings.warn(
                "Issue 75: internal_api_error_MWException should not be in the output"
            )
        # uncomment if issue fixed
        # self.assertNotIn("internal_api_error_MWException", out)
        # self.assertIn("✅", out)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
