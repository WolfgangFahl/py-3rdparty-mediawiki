'''
Created on 2020-03-24

@author: wf
'''
from urllib.parse import urlparse
import pywikibot
import re
from os.path import isfile 
from wikibot.wikiuser import WikiUser
from pywikibot import config2
from pywikibot.data.api import LoginManager
from wikibot.wiki import Wiki

class WikiBot(Wiki):
    '''
    WikiBot
    '''      
    @staticmethod
    def getBots(limit=None,name=None,valueExpr=None):
        bots={}
        wikiUsers=WikiUser.getWikiUsers().values()
        for wikiUser in wikiUsers:
            selected=True
            if name is not None:
                value=wikiUser.__dict__[name]
                found=re.search(valueExpr,value)
                selected=found is not None
            if selected:
                wikibot=WikiBot(wikiUser)
                bots[wikiUser.wikiId]=wikibot
                if limit is not None and len(bots)>=limit:
                    break
        return bots
    
    @staticmethod
    def ofWikiId(wikiId):
        wikiUser=WikiUser.ofWikiId(wikiId)
        wikibot=WikiBot(wikiUser)
        return wikibot
    
    @staticmethod
    def ofWikiUser(wikiUser):
        wikibot=WikiBot(wikiUser)
        return wikibot
        
    def __init__(self,wikiUser,debug=False):
        '''
        Constructor
        
        Args:
            wikiUser(WikiUser): the wiki user to initialize me for
        '''
        super(WikiBot,self).__init__(wikiUser,debug) 
        self.family=wikiUser.wikiId.replace("-","").replace("_","")
        self.url=wikiUser.url.replace("\\:",":")
        if not self.url:
            raise Exception("url is missing for %s" % wikiUser.wikiId)
        
        self.scriptPath=wikiUser.scriptPath
        self.version=wikiUser.version
        o=urlparse(self.url)
        self.scheme=o.scheme
        self.netloc=o.netloc
        self.scriptPath=o.path+self.scriptPath      
        self.checkFamily()
        
    def checkFamily(self):
        '''
        check if a family file exists and if not create it
        '''
        iniFile=WikiUser.iniFilePath(self.wikiUser.wikiId)
        famfile=iniFile.replace(".ini",".py")
        if not isfile(famfile):
            print("creating family file %s" % famfile)
            template='''# -*- coding: utf-8  -*-
from pywikibot import family

class Family(family.Family):
    name = '%s'
    langs = {
        'en': '%s',
    }
    def scriptpath(self, code):
       return '%s'
       
    def isPublic(self):
        return %s   
        
    def version(self, code):
        return "%s"  # The MediaWiki version used. Very important in most cases. (contrary to documentation)   

    def protocol(self, code):
       return '%s'
'''         
            mw_version=self.wikiUser.version.lower().replace("mediawiki ","")
            ispublic='False' if self.wikiUser.user is not None else 'True'
            code=template % (self.family,self.netloc,self.scriptPath,ispublic,mw_version,self.scheme)
            with open(famfile,"w") as py_file:
                py_file.write(code)
        config2.register_family_file(self.family, famfile)  
        if self.wikiUser.user:
            config2.usernames[self.family]['en'] = self.wikiUser.user
        #config2.authenticate[self.netloc] = (self.user,self.getPassword())
        self.site=pywikibot.Site('en',self.family)  
        if self.wikiUser.user is not None:
            # needs patch as outlined in https://phabricator.wikimedia.org/T248471
            #self.site.login(password=self.wikiUser.getPassword())
            lm = LoginManager(password=self.wikiUser.getPassword(), site=self.site, user=self.wikiUser.user)
            lm.login()
        
    def getPage(self,pageTitle):
        ''' get the page with the given title'''
        page = pywikibot.Page(self.site, pageTitle)  
        return page             
    
    def savePage(self,pageTitle,pageContent,pageSummary):
        ''' save a page with the given pageTitle, pageContent and pageSummary'''
        newPage=self.getPage(pageTitle)
        newPage.text=pageContent
        newPage.save(pageSummary)
        
    def __str__(self):
        wu=self.wikiUser
        text="%20s: %s %s" % (wu.wikiId,wu.url,wu.user)    
        return text