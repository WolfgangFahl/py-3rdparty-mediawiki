"""
Created on 2021-02-16

@author: wf
"""

import json
import re
import unittest
from contextlib import redirect_stdout
from io import StringIO

from tests.base_wiki_test import BaseWikiTest
from wikibot3rd.wikiclient import WikiClient
from wikibot3rd.wikipush import WikiPush, mainQuery


class TestWikiQuery(BaseWikiTest):
    """
    tests for https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/56
    """

    def setUp(self, debug: bool = False, profile: bool = True):
        """ """
        super().setUp(debug, profile)
        self.eventQuery = """{{#ask: [[IsA::Event]]
|mainlabel=Event
|?Event acronym = acronym
|?Event description = description
|?Event title = title
|?Event homepage = homepage
|?Event wikidataid = wikidataid
|?Event series = series
|?Event colocated_with = colocated_with
|?Event city = city
|?Event country = country
|?Event region = region
|?Creation date=creation date
|?Modification date=modification date
|sort=Event acronym
|order=ascending
|format=table
|limit=10
}}
"""
        self.getWikiUser("cr")
        # self.getWikiUser("orcopy")
        # self.getWikiUser("orclone")

    def getWikiClient(self, wikiId="cr"):
        """get the alternative SMW access instances for the given wiki id"""
        wikiuser = self.getSMW_WikiUser(wikiId)
        wikiclient = WikiClient.ofWikiUser(wikiuser)
        return wikiclient

    def testWikiQuery(self):
        """
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/56
        """
        # make sure the CI wikiUser is prepared
        if self.inPublicCI():
            return
        debug = self.debug
        debug = True
        wikiId = "cr"
        wikiClient = self.getWikiClient(wikiId)
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery = self.eventQuery
        for outputFormat in [
            "csv",
            "json",
            "xml",
            "ttl",
            "mediawiki",
            "github",
            "latex",
            "lod",
        ]:
            formatedQueryResults = wikiPush.formatQueryResult(
                askQuery, wikiClient, outputFormat=outputFormat, entityName="Event"
            )
            if formatedQueryResults:
                if debug:
                    print(formatedQueryResults)
            else:
                if debug:
                    print(f"Format {outputFormat} is not supported.")
        pass

    def testJsonDefault(self):
        """Test if default entityName is set correctly for format json"""
        argv = ["-s", "cr", "-q", self.eventQuery]
        mystdout = StringIO()
        with redirect_stdout(mystdout):
            mainQuery(argv)
        res = mystdout.getvalue()
        debug = self.debug
        # debug=True
        if debug:
            print(res)
        self.assertTrue("data" in json.loads(res).keys())
        return

    def testJson(self):
        """Test if given entityName is set correctly for format json"""
        entityName = "Event"
        argv = [
            "-s",
            "cr",
            "-q",
            self.eventQuery,
            "--entityName",
            entityName,
            "--format",
            "json",
        ]
        mystdout = StringIO()
        with redirect_stdout(mystdout):
            mainQuery(argv)
        res = mystdout.getvalue()
        if self.debug:
            print(res)
        self.assertTrue(entityName in json.loads(res).keys())
        return

    def testCSV(self):
        """
        Test if wikiquery returns CSV format correctly
        """
        entityName = "Event"
        argv = ["-s", "cr", "-q", self.eventQuery, "--format", "csv"]
        mystdout = StringIO()
        with redirect_stdout(mystdout):
            mainQuery(argv)
        res = mystdout.getvalue()
        debug = self.debug
        debug = True
        if debug:
            print(res)
        expected_headline = "Event;acronym;description;title;homepage;wikidataid;series;colocated_with;city;country;region;creation date;modification date\n"
        self.assertTrue(res.startswith(expected_headline))
        return

    def testLOD(self):
        """
        Test if LOD is returned correctly if called form api
        """
        wikiId = "cr"
        wikiClient = self.getWikiClient(wikiId)
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery = self.eventQuery
        lod_res = wikiPush.formatQueryResult(askQuery, wikiClient, entityName="Event")
        if self.debug:
            print(lod_res)
        self.assertTrue(isinstance(lod_res, list))
        self.assertTrue(isinstance(lod_res[0], dict))

    def testIssue66(self):
        """
        test TypeError("'dict_values' object is not subscriptable")
        """
        if self.inPublicCI():
            return
        wikiId = "wgt"
        wikiClient = self.getWikiClient(wikiId)
        wikiClient.login()
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery = "{{#ask:[[Modification date::+]]}}"
        lod_res = wikiPush.formatQueryResult(askQuery, wikiClient, queryDivision=10)
        if self.debug:
            print(lod_res)

    def test_issue111(self):
        """
        test https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/111
        add --template option to wikiquery
        """
        self.getSMW_WikiUser("wikipedia_en")
        argv = [
            "-d",
            "-s",
            "wikipedia_en",
            "-q",
            "[[Category:Presidents_of_the_United_States]]",
            "--template",
            "Infobox officeholder",
            "--limit",
            "6",
            "--format",
            "json",
        ]
        mystdout = StringIO()
        with redirect_stdout(mystdout):
            mainQuery(argv)
        text = mystdout.getvalue()
        debug = self.debug
        # debug=True
        json_text = re.search(r"\{.*", text, re.DOTALL).group(0)
        if debug:
            print(json_text)
        records = json.loads(json_text)
        self.assertGreaterEqual(len(records["data"]), 3)
        for record in records["data"]:
            self.assertIn("name", record)
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
