'''
Created on 2021-02-16

@author: wf
'''
import json
import unittest
import sys
from io import StringIO

from wikibot.wikiclient import WikiClient
from tests.test_WikiUser import TestWikiUser
from wikibot.wikipush import WikiPush, mainQuery
from tests.basetest import BaseTest

class TestWikiQuery(BaseTest):
    '''
    tests for https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/56
    '''
    def setUp(self):
        BaseTest.setUp(self)
        self.eventQuery = "[[IsA::Event]][[Ordinal::>2]][[start date::>2018]][[start date::<2019]]| mainlabel = Event| ?Title = title| ?Event in series = series| ?_CDAT=creation date| ?_MDAT=modification date| ?ordinal=ordinal| ?Homepage = homepage|format=table"
        pass
    
    def getWikiClient(self,wikiId='orcopy'):
        ''' get the alternative SMW access instances for the given wiki id
        '''
        wikiuser=TestWikiUser.getSMW_WikiUser(wikiId)
        wikiclient=WikiClient.ofWikiUser(wikiuser)
        return wikiclient

    def testWikiQuery(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/56
        '''
        # make sure the CI wikiUser is prepared
        if self.inPublicCI(): return
        wikiId='orcopy'
        wikiClient=self.getWikiClient(wikiId)
        wikiPush=WikiPush(fromWikiId=wikiId)
        askQuery="""{{#ask: [[IsA::Event]][[Ordinal::>2]][[start date::>2018]][[start date::<2019]]
| mainlabel = Event
| ?Title = title
| ?Event in series = series
| ?_CDAT=creation date
| ?_MDAT=modification date
| ?ordinal=ordinal
| ?Homepage = homepage
|format=table
}}"""   
        for outputFormat in ["csv","json","xml","ttl","wikidata","lod"]:
            formatedQueryResults = wikiPush.formatQueryResult(askQuery, wikiClient,outputFormat=outputFormat, entityName="Event")
            if formatedQueryResults:
                if self.debug:
                    print(formatedQueryResults)
            else:
                if self.debug:
                    print(f"Format {outputFormat} is not supported.")
        pass

    def testJsonDefalt(self):
        """Test if default entityName is set correctly for format json"""
        if self.inPublicCI(): return
        argv=["-s","orcopy","-q",self.eventQuery]
        mystdout = StringIO()
        sys.stdout = mystdout
        mainQuery(argv)
        res = mystdout.getvalue()
        self.assertTrue("data" in json.loads(res).keys())
        return

    def testJson(self):
        """Test if given entityName is set correctly for format json"""
        if self.inPublicCI(): return
        entityName = "Event"
        argv=["-s","orcopy","-q",self.eventQuery, "--entityName", entityName, "--format", "json"]
        mystdout = StringIO()
        sys.stdout = mystdout
        mainQuery(argv)
        res = mystdout.getvalue()
        self.assertTrue(entityName in json.loads(res).keys())
        return

    def testCSV(self):
        """Test if wikiquery returns CSV format correctly"""
        if self.inPublicCI(): return
        entityName = "Event"
        argv=["-s","orcopy","-q",self.eventQuery, "--format", "csv"]
        mystdout = StringIO()
        sys.stdout = mystdout
        mainQuery(argv)
        res = mystdout.getvalue()
        expected_headline = "Event;title;series;creation_date;modification_date;ordinal;homepage\n"
        self.assertTrue(res.startswith(expected_headline))
        return

    def  testLOD(self):
        '''
        Test if LOD is returned correctly if called form api
        '''
        wikiId = 'orclone'
        wikiClient = self.getWikiClient(wikiId)
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery = "{{#ask:" + self.eventQuery + "}}"
        lod_res = wikiPush.formatQueryResult(askQuery, wikiClient, entityName="Event")
        if self.debug:
            print(lod_res)
        self.assertTrue(isinstance(lod_res, list))
        self.assertTrue(isinstance(lod_res[0], dict))
        
    def testIssue66(self):
        '''
        test TypeError("'dict_values' object is not subscriptable")
        '''
        if self.inPublicCI(): return
        wikiId= 'wgt'
        wikiClient = self.getWikiClient(wikiId)
        wikiClient.login()
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery="{{#ask:[[Modification date::+]]}}"
        lod_res= wikiPush.formatQueryResult(askQuery, wikiClient, queryDivision=10)
        if self.debug:
            print (lod_res)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()