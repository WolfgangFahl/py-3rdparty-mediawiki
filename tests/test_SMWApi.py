'''
Created on 25.05.2020

@author: wf
'''
import unittest
import getpass
from wikibot.wikibot import WikiBot
from wikibot.smw import SMW

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
        smw=SMW()
        fixedAsk=smw.fixAsk(TestSMW.testask1)
        expected="""[[Concept:Semantic_MediaWiki_Cons_2012]]|?Has_Wikidata_item_ID=WikiDataId|?Has_planned_finish=finish|?Has_planned_start=start|?Has_location=location|format=table"""
        if TestSMW.debug:
            print(fixedAsk)
        self.assertEqual(expected,fixedAsk)
            
    def testSMWInfo(self):
        if not getpass.getuser()=="travis":   
            '''
            needs:
            .mediawiki-japi/smw.ini as:
            #Mediawiki JAPI credentials for semantic-mediawiki
            #manually entered 2020-05-39
            url=https://www.semantic-mediawiki.org
            scriptPath=/w
            wikiId=smw
            version=MediaWiki 1.31.7
            '''              
            wikibot=WikiBot.ofWikiId("smw")
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
        if not getpass.getuser()=="travis": 
            wikibot=WikiBot.ofWikiId("smw")
            smw=SMW(wikibot.site)  
            result=smw.rawquery(TestSMW.testask1)
            if TestSMW.debug:
                print (result)
            self.assertTrue('query' in result)
            query=result['query']
            self.assertTrue('printrequests' in query)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSMWApi']
    unittest.main()