'''
Created on 2021-02-16

@author: wf
'''
import unittest
from wikibot.wikiclient import WikiClient
from tests.test_WikiUser import TestWikiUser
from wikibot.wikipush import WikiPush

class TestWikiQuery(unittest.TestCase):
    '''
    tests for https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/56
    '''
    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass
    
    def getWikiClient(self,wikiId='or'):
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
        wikiId='or'
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
        for outputFormat in ["csv","json","xml","ttl","wikidata"]:
            formatedQueryResults = wikiPush.formatQueryResult(askQuery, wikiClient,outputFormat=outputFormat)
            if formatedQueryResults:
                if self.debug:
                    print(formatedQueryResults)
            else:
                if self.debug:
                    print(f"Format {outputFormat} is not supported.")
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()