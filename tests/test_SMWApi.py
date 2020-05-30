'''
Created on 25.05.2020

@author: wf
'''
import unittest
from wikibot.smw import SMW
from tests.test_wikibot import TestWikiBot

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
        
    def testSMWAsk(self):
        """ test getting the unserialized json result of an ask query"""
        wikibot=TestWikiBot.getSMW_Wiki()
        smw=SMW(wikibot.site)  
        result=smw.query(TestSMW.testask1)
        if TestSMW.debug:
            print (result)    
        self.assertEquals(2,len(result))    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSMWApi']
    unittest.main()