'''
Created on 2020-10-29

@author: wf
'''
import unittest
import os
import getpass
import wikibot
from wikibot.wikipush import WikiPush


class TestWikiPush(unittest.TestCase):
    '''
    test pushing pages including images
    '''

    def setUp(self):
        self.debug=False
        pass

    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in [ "travis", "runner" ];
            

    def tearDown(self):
        pass
    
    def testIssue11(self):
        '''
        test the limit handling 
        '''
        # don't test this in Travis
        if self.inPublicCI(): return
        askQuery="[[isA::Event]]"
        wikipush=WikiPush("or",None)
        pages=wikipush.query(askQuery,showProgress=False,limit=10)
        self.assertEqual(10,len(pages))
    
    def testIssue29(self):
        '''
        makes sure query does not hang on large queries
        '''
        # don't test this in Travis
        if self.inPublicCI(): return
        return # test takes 22 secs - don't activate if not necessary
        askQuery="[[isA::Event]]"
        wikipush=WikiPush("orcopy",None)
        pages=wikipush.query(askQuery,showProgress=True)
        print(len(pages))
        pass
    
    def testIssue16(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/16
        allow mass delete of pages
        '''
        # don't test this in Travis
        if self.inPublicCI(): return
        wikipush=WikiPush(None,"test")
        pageTitles=['deleteMe1','deleteMe2','deleteMe3']
        for pageTitle in pageTitles:
            newPage=wikipush.toWiki.getPage(pageTitle)            
            newPage.edit("content for %s" % pageTitle,"created by testIssue16")
        wikipush.nuke(pageTitles, force=False)
        wikipush.nuke(pageTitles, force=True)
    
    def testIssue14(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/14
        Pushing pages in File: namespace should be working
        '''
        return # don't test this nightly
        # don't test this in Travis
        if self.inPublicCI(): return
        wikipush=WikiPush("master","test")
        wikipush.push(["File:index.png"], force=True, ignore=True, withImages=True)
        
         
    def testIssue12(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/12
        add -qf / queryField option to allow to select other property than mainlabel
        '''
        # don't test this in Travis
        if self.inPublicCI(): return
        wikipush=WikiPush("smwcopy","test")
        ask="""{{#ask:[[Has conference::+]]
 |mainlabel=Talk
 |?Has description=Description
 |?Has conference=Event
 |sort=Has conference
 |order=descending
 |format=table
 |limit=200
}}"""
        pages=wikipush.query(ask,queryField="Event")
        #self.debug=True
        if self.debug:
            print (pages)
            print (len(pages))
        self.assertTrue(len(pages)>15)
        self.assertTrue(len(pages)<100)
    
    def testTransferPagesFromMaster(self):
        '''
        test transferpages
        '''
        if self.inPublicCI(): return
        ask="{{#ask: [[TransferPage page::+]][[TransferPage wiki::Master]]| mainlabel=-| ?TransferPage page = page| format=table|limit=300}}"
        wikipush=WikiPush("master","test")
        pages=wikipush.query(ask,queryField="page")
        if self.debug:
            print (pages)
    
    def testQuery(self):
        '''
        https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/10
        Query support for page selection
        '''
        if self.inPublicCI(): return
        wp=WikiPush("smwcopy","test")
        pages=wp.query("[[Capital of::+]]")
        if self.debug:
            print (pages)
        self.assertTrue(len(pages)>=5)
        self.assertTrue("Demo:Berlin" in pages)
        
    def testWikiBackup(self):
        # don't test this in Travis
        if self.inPublicCI(): return
        wp=WikiPush("smw")
        pageTitles=wp.query("[[Capital of::+]]")
        wp.backup(pageTitles)
        
    def testWikiBackupCommandLine(self):
        '''
        test starting backup from the command line
        '''
        argv=["-s","smwcopy","-q","[[modification date::+]]"]
        wikibot.wikipush.mainBackup(argv)
  

    def testWikiPush(self):
        '''
        test pushing a page from one wiki to another
        '''
        # don't test this in Travis
        if self.inPublicCI(): return
        wp=WikiPush("wikipedia_org_test2","test")
        for force in [False,True]:
            for ignore in [False,True]:
                wp.push(["PictureTestPage"],force=force,ignore=ignore)
        pass
    
    def testDiff(self):
        '''
        check the diff functionality
        '''
        text="Hello World!\nLet's test the search and replace function.\nTry Apples and Oranges!\nOr do you like chocolate better?"
        #print (text)
        modify=WikiPush.getModify("Apples","Peaches")
        newText=modify(text)
        diff=WikiPush.getDiff(text, newText,n=0)
        if self.debug:
            print (diff)
        self.assertEqual(2,len(diff.split("\n")))
        
    def testDownload(self):
        '''
        check the image download
        '''
        # don't test this in Travis
        if self.inPublicCI(): return
        wp=WikiPush("wikipedia_org_test2","test")
        page=wp.fromWiki.getPage("PictureTestPage")
        images=list(page.images())
        self.assertEqual(3,len(images))
        for image in images:
            if "Mona" in image.name:
                imagePath,filename=wp.downloadImage(image,"/tmp")
                imageSize=os.path.getsize(imagePath)
                if self.debug:
                    print ("size of %s is %d bytes" % (filename,imageSize))
                self.assertEqual(3506068,imageSize)
        

    def testWarnings(self):
        '''
        test the warning handling
        '''
        return 
        # https://stackoverflow.com/a/5222474/1497139
        argv=["-l","-s","swa","-t","test","-q","[[modification date::>2020-11-29]]","-wi","-f","-i"]
        wikibot.wikipush.main(argv)
        
    def testEdit(self):
        return
        # this actually edits data ... don't activate if you don't really want to do this
        argv=["-t","orcopy","-d","-q","[[isA::Event]]","--search","\\[Category:","--replace","[has category::","-f","--progress"]
        wikibot.wikipush.mainEdit(argv)
        return

    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()