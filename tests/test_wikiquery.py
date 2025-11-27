"""
Created on 2021-02-16

@author: wf
"""

import json
import re
import unittest
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO

from basemkit.basetest import Basetest

from tests.base_wiki_test import BaseWikiTest
from wikibot3rd.wikiclient import WikiClient
from wikibot3rd.wikipush import WikiPush, mainQuery


class TestWikiQuery(BaseWikiTest):
    """
    tests for https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/56
    and issues/111
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

    def getWikiClient(self, wikiId="cr"):
        """get the alternative SMW access instances for the given wiki id"""
        wikiuser = self.getSMW_WikiUser(wikiId)
        wikiclient = WikiClient.ofWikiUser(wikiuser)
        return wikiclient

    def capture_mainQuery(self, argv: list) -> str:
        """
        Helper to capture stdout from mainQuery and handle debug printing
        """
        mystdout = StringIO()
        with redirect_stdout(mystdout):
            mainQuery(argv)
        result = mystdout.getvalue()

        if self.debug:
            print(result)
        return result

    def testWikiQuery(self):
        """
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/56
        """
        if self.inPublicCI():
            return

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
            if formatedQueryResults and self.debug:
                print(formatedQueryResults)
            elif not formatedQueryResults and self.debug:
                print(f"Format {outputFormat} is not supported.")

    def testJsonDefault(self):
        """Test if default entityName is set correctly for format json"""
        argv = ["-s", "cr", "-q", self.eventQuery]
        res = self.capture_mainQuery(argv)
        self.assertIn("data", json.loads(res).keys())

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
        res = self.capture_mainQuery(argv)
        self.assertIn(entityName, json.loads(res).keys())

    def testCSV(self):
        """
        Test if wikiquery returns CSV format correctly
        """
        argv = ["-s", "cr", "-q", self.eventQuery, "--format", "csv"]
        res = self.capture_mainQuery(argv)
        expected_headline = "Event;acronym;description;title;homepage;wikidataid;series;colocated_with;city;country;region;creation date;modification date\n"
        self.assertTrue(res.startswith(expected_headline))

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
        self.assertIsInstance(lod_res, list)
        self.assertIsInstance(lod_res[0], dict)

    @unittest.skipIf(Basetest.inPublicCI(), "target test wiki not public")
    def testIssue66(self):
        """
        test TypeError("'dict_values' object is not subscriptable")
        """
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
        limit = 10
        argv = [
            "-d",
            "-s",
            "wikipedia_en",
            "--throttle",
            "1.0",
            "-q",
            "[[Category:19th-century_presidents_of_the_United_States]]",
            "--template",
            "Infobox officeholder",
            "--limit",
            f"{limit}",
            "--format",
            "json",
        ]

        # Use common capture method
        text = self.capture_mainQuery(argv)

        # Parse output
        json_match = re.search(r"\{.*", text, re.DOTALL)
        self.assertIsNotNone(json_match, "No JSON content found in output")
        json_text = json_match.group(0)

        records = json.loads(json_text)
        self.assertGreaterEqual(len(records["data"]), limit)

        key_counter = Counter()
        for record in records["data"]:
            key_counter.update(record.keys())

        if self.debug:
            print(key_counter.most_common())

        common_keys = {k for k, v in key_counter.items() if v >= limit * 0.9}
        expected_keys = [
            "image",
            "caption",
            "office",
            "party",
            "birth_date",
            "death_date",
        ]
        for k in expected_keys:
            self.assertIn(k, common_keys)
