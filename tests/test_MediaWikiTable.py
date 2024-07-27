"""
Created on 2020-08-21

@author: wf
"""

import unittest
from datetime import date, datetime

from tests.basetest import BaseTest
from wikibot3rd.mwTable import MediaWikiTable


class Test_MediaWikiTable(BaseTest):
    """
    test mediawiki table creation
    """

    def dob(self, isoDateString):
        """get the date of birth from the given iso date state"""
        # if sys.version_info >= (3, 7):
        #    dt=datetime.fromisoformat(isoDateString)
        # else:
        dt = datetime.strptime(isoDateString, "%Y-%m-%d")
        return dt.date()

    def test_MediaWikiTable(self):
        """
        see
        """
        listOfDicts = [
            {
                "name": "Elizabeth Alexandra Mary Windsor",
                "born": self.dob("1926-04-21"),
                "numberInLine": 0,
                "wikidataurl": "https://www.wikidata.org/wiki/Q9682",
            },
            {
                "name": "Charles, Prince of Wales",
                "born": self.dob("1948-11-14"),
                "numberInLine": 1,
                "wikidataurl": "https://www.wikidata.org/wiki/Q43274",
            },
            {
                "name": "George of Cambridge",
                "born": self.dob("2013-07-22"),
                "numberInLine": 3,
                "wikidataurl": "https://www.wikidata.org/wiki/Q1359041",
            },
            {
                "name": "Harry Duke of Sussex",
                "born": self.dob("1984-09-15"),
                "numberInLine": 6,
                "wikidataurl": "https://www.wikidata.org/wiki/Q152316",
            },
        ]
        today = date.today()
        for person in listOfDicts:
            born = person["born"]
            age = (today - born).days / 365.2425
            person["age"] = age
            person["ofAge"] = age >= 18
        for nlMode in [True, False]:
            colFormats = {"age": "%5.1f years"}
            mwTable = MediaWikiTable(withNewLines=nlMode, colFormats=colFormats)
            mwTable.fromListOfDicts(listOfDicts)
            wikiMarkup = mwTable.asWikiMarkup()
            if self.debug:
                print(wikiMarkup)
            self.assertTrue('{|class="wikitable sortable"' in wikiMarkup)
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_MediaWikiTable']
    unittest.main()
