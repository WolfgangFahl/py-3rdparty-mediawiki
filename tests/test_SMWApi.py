'''
Created on 2020-05-25

@author: wf
'''
import unittest
from wikibot.smw import SMW,SMWBot, SMWClient, PrintRequest
from wikibot.wikibot import WikiBot
from wikibot.wikiclient import WikiClient
from tests.test_wikibot import TestWikiBot
from tests.test_WikiUser import TestWikiUser
from datetime import datetime

class TestSMW(unittest.TestCase):
    """ test access to SemanticMediaWiki API see https://www.semantic-mediawiki.org/wiki/Help:API:ask"""

    # sample queries
    testask1="""{{#ask:  [[Concept:Semantic MediaWiki Cons 2012]]
        |?Has_Wikidata_item_ID = WikiDataId
        |?Has planned finish = finish
        |?Has planned start =    start
        |?Has_location  =        location
        |  format=table  }}"""
        
    def setUp(self):
        '''
        general setup
        '''
        self.debug=False
        pass


    def tearDown(self):
        '''
        general tear down
        '''
        pass

    
    def testFixAsk(self):
        """ test fixing an ask query to be made fit for API use"""
        smw=SMW()
        fixedAsk=smw.fixAsk(TestSMW.testask1)
        expected="""[[Concept:Semantic_MediaWiki_Cons_2012]]|?Has_Wikidata_item_ID=WikiDataId|?Has_planned_finish=finish|?Has_planned_start=start|?Has_location=location|format=table"""
        if TestSMW.debug:
            print(fixedAsk)
        self.assertEqual(expected,fixedAsk)
        
    def testGetConcept(self):
        """ test extracting a concept from an ask query"""
        smw=SMW()
        fixedAsk=smw.fixAsk(TestSMW.testask1)
        concept=smw.getConcept(fixedAsk)
        if self.debug:
            print(concept)
        self.assertEqual(concept,"Semantic_MediaWiki_Cons_2012")
        
    def getSMWs(self,wikiId='smw'):
        ''' get the alternative SMW access instances for the given wiki id
        '''
        wikiuser=TestWikiUser.getSMW_WikiUser(wikiId)
        wikibot=WikiBot.ofWikiUser(wikiuser)
        wikiclient=WikiClient.ofWikiUser(wikiuser)
        smwbot=SMWBot(wikibot.site)
        smwclient=SMWClient(wikiclient.getSite())
        return [smwbot,smwclient]
         
    def testGetEvents(self):
        ''' text for issue #6 https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/6 '''    
        limit=20
        ask="""{{#ask: [[Acronym::+]]
    |mainlabel=Event
    | ?Acronym = acronym
    | ?Has location city = city
    | ?_CDAT=creation date
    | ?_MDAT=modification date
    | limit=%d
    |format=table
    }}
    """ % limit
        for smw in self.getSMWs("or"):
            result=smw.query(ask,limit=limit)
            if self.debug:
                print (len(result))
                print (result)  
            self.assertEqual(limit,len(result))    
            fields=['Event','acronym','city','creation_date','modification_date']
            for record in result.values():
                for field in fields:
                    self.assertTrue(field in record)
            
    def testSMWInfo(self):
        """ test the SMW Info call"""
        for smw in self.getSMWs():
            result=smw.info()
            if (self.debug):
                print (result)
            self.assertTrue('info' in result)   
            info=result['info']
            expectedlist=['propcount','usedpropcount','declaredpropcount']
            for expected in expectedlist:
                self.assertTrue(expected in info)
                
    def testSMWAskRaw(self):
        """ test getting the raw result of an ask query"""
        for smw in self.getSMWs():
            result=smw.rawquery(TestSMW.testask1)
            if TestSMW.debug:
                print (result)
            self.assertTrue('query' in result)
            query=result['query']
            self.assertTrue('printrequests' in query)
            self.assertTrue('results' in query)
        
    # Helpers for parsing the result of isoformat()
    # https://github.com/python/cpython/blob/master/Lib/datetime.py
    def dateFromIso(self,dtstr):
        # It is assumed that this function will only be called with a
        # string of length exactly 10, and (though this is not used) ASCII-only
        year = int(dtstr[0:4])
        if dtstr[4] != '-':
            raise ValueError('Invalid date separator: %s' % dtstr[4])
    
        month = int(dtstr[5:7])
    
        if dtstr[7] != '-':
            raise ValueError('Invalid date separator')
    
        day = int(dtstr[8:10])
    
        return datetime(year, month, day)
    
    def getAskResult(self,smw,ask,limit=20):
        """ get the query result for the given ask query """
        #PrintRequest.debug=self.debug
        result=smw.query(ask,limit=limit)
        if self.debug:
            print (result)    
        return result;
    
    def checkExpected(self,ask,expectedRecords,debug=False):
        """ check that the given ask query returns the content of the expectedRecords""" 
        for smw in self.getSMWs('smw'):
            result=self.getAskResult(smw,ask)
            if debug:
                print(result)
            self.assertEquals(len(expectedRecords),len(result))
            resultlist=list(result.items())
            for i in range(len(expectedRecords)):
                expectedRecord=expectedRecords[i]
                recordkey,record=resultlist[i];
                for key in expectedRecord.keys():
                    self.assertEquals(expectedRecord[key],record[key]) 
        
    def testSMWAsk(self):
        """ test getting the unserialized json result of an ask query"""
        expectedRecords=[{
            'WikiDataId': 'Q42407116', 
            'location':'Cologne, Germany',
            'start':self.dateFromIso('2012-10-24'),
            'finish':self.dateFromIso('2012-10-26')
            },{
            'WikiDataId': 'Q42407127', 
            'location':'Carlsbad, CA, USA',
            'start':self.dateFromIso('2012-04-25'),
            'finish':self.dateFromIso('2012-04-27')
            }]
        self.checkExpected(TestSMW.testask1,expectedRecords)   
        
    # test the SMWBaseURL    
    def testSMWBaseUrl(self):
        wikibot=TestWikiBot.getSMW_Wiki()
        if TestSMW.debug:
            print(wikibot.scriptPath)
        self.assertEquals("/w",wikibot.scriptPath)
        
    # issue https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/3
    # see https://www.semantic-mediawiki.org/wiki/User:WolfgangFahl/Workdocumentation_2020-06-01
    def testSMWAskwWithEmptyLink(self):
        ask="""
        {{#ask: [[Category:Event]]
|mainlabel=Event
|?Has_local_chair=chair
|format=table
}}
        """
        for smw in self.getSMWs('or'):
            result=self.getAskResult(smw,ask)
            self.assertTrue(len(result)>7)
                
    def testSMWAskWithMainLabel(self):
        ask="""{{#ask:
 [[Category:City]]
 [[Located in::Germany]] 
 |mainlabel=City
 |?Population 
 |?Area#km² = Size in km²
}}"""
        expectedRecords=[{
            'City':'Demo:Berlin',
            'Population': 3520061, 
            },{
            'City':'Demo:Cologne',
            'Population': 1080394, 
            },{
            'City':'Demo:Frankfurt',    
            'Population': 679664, 
            },{
            'City':'Demo:Munich',    
            'Population': 1353186, 
            },{
            'City':'Demo:Stuttgart',    
            'Population': 606588, 
            },{
            'City':'Demo:Würzburg',   
            'Population': 126635, 
            }]
        self.checkExpected(ask, expectedRecords)   
        
    def testIssue5(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/5
        Support more datatypes
        '''
        # https://www.semantic-mediawiki.org/wiki/Help:List_of_datatypes
        properties=[
            "Has annotation uri",
            "Has boolean",
            "Has code",
            "Has date",
            "Has SMW issue ID",
            "Has email address",
            "Has coordinates",
            "Has keyword",
            "Has number",
            "Has mlt",
            "Has example",
            "Has area",
            "Has Wikidata reference",
            "Has conservation status",
            "Telephone number",
            "Has temperatureExample",
            "SomeProperty",
            "Has URL"            
        ]
        #PrintRequest.debug=True
        for prop in properties:
            ask="""{{#ask:[[%s::+]]
 |?%s
 |format=json
 |limit=1
}}
""" % (prop,prop)
            for smw in self.getSMWs('smw'):
                result=self.getAskResult(smw,ask)
                debug=True
                if debug:
                    print("%s: %s" % (prop,result))
                self.assertTrue(len(result)>=1)
                record=list(result.values())[0]
                #print(record.keys())
                self.assertTrue(prop in record.keys())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSMWApi']
    unittest.main()