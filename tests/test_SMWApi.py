'''
Created on 25.05.2020

@author: wf
'''
import unittest
from wikibot.smw import SMW, PrintRequest
from tests.test_wikibot import TestWikiBot
from datetime import datetime

class TestSMW(unittest.TestCase):
    """ test access to SemanticMediaWiki API"""
    debug=True
    testask1="""{{#ask:  [[Concept:Semantic MediaWiki Cons 2012]]
        |?Has_Wikidata_item_ID = WikiDataId
        |?Has planned finish = finish
        |?Has planned start =    start
        |?Has_location  =        location
        |  format=table  }}"""
    
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
        if TestSMW.debug:
            print(concept)
        self.assertEquals(concept,"Semantic_MediaWiki_Cons_2012")
            
    def testSMWInfo(self):
        """ test the SMW Info call"""
        wikibot=TestWikiBot.getSMW_Wiki()
        smw=SMW(wikibot.site)
        result=smw.info()
        if (TestSMW.debug):
            print (result)
        self.assertTrue('info' in result)   
        info=result['info']
        expectedlist=['propcount','usedpropcount','declaredpropcount']
        for expected in expectedlist:
            self.assertTrue(expected in info)
            
                
    def testSMWAskRaw(self):
        """ test getting the raw result of an ask query"""
        wikibot=TestWikiBot.getSMW_Wiki()
        smw=SMW(wikibot.site)  
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
    
    def checkExpected(self,ask,expectedRecords):
        """ check that the given ask query returns the content of the expectedRecords""" 
        wikibot=TestWikiBot.getSMW_Wiki()
        smw=SMW(wikibot.site,"/wiki/")  
        PrintRequest.debug=True
        result=smw.query(ask)
        if TestSMW.debug:
            print (result)    
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
        
    def testSMWBaseUrl(self):
        wikibot=TestWikiBot.getSMW_Wiki()
        print(wikibot.scriptPath)
                
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

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSMWApi']
    unittest.main()