'''
Created on 24.03.2020

@author: wf
'''
from os.path import expanduser,isfile,isdir,join
from os import listdir,makedirs
import datetime
from urllib.parse import urlparse
import pywikibot
import getpass
from pywikibot import config2
from wikibot.crypt import Crypt
from pywikibot.data.api import LoginManager


class WikiBot(object):
    '''
    WikiBot
    '''
    
    @staticmethod
    def load_properties(filepath, sep='=', comment_char='#'):
        """
        Read the file passed as parameter as a properties file.
        https://stackoverflow.com/a/31852401/1497139
        """
        props = {}
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"') 
                    props[key] = value 
        return props
    
    @staticmethod
    def iniPath():
        home = expanduser("~")
        mj=home+"/.mediawiki-japi"
        return mj
        
    @staticmethod
    def getBots():
        bots={}
        mj=WikiBot.iniPath()
        if isdir(mj):
            for file in listdir(mj):
                proppath=join(mj,file)
                if isfile(proppath) and file.endswith(".ini"):
                    try:
                        bot=WikiBot(proppath)
                        bots[bot.wikiId]=bot
                    except Exception as e:
                        print (e)    
        return bots      
  
    @staticmethod
    def iniFilePath(wikiId):
        user=getpass.getuser()
        iniFilePath="%s/%s_%s.ini" % (WikiBot.iniPath(),user,wikiId)
        return iniFilePath
    
    @staticmethod
    def ofWikiId(wikiId):
        iniFile=WikiBot.iniFilePath(wikiId)
        wikibot=WikiBot(iniFile)
        return wikibot
    
    @staticmethod
    def writeIni(wikiId,name,url,scriptPath,version):
        iniPath=WikiBot.iniPath()
        if not isdir(iniPath):
            makedirs(iniPath)
        iniFile=open(WikiBot.iniFilePath(wikiId),"w")
        isodate=datetime.datetime.now().isoformat()
        template="""# Mediawiki JAPI credentials for %s
            # created by wikibot at %s
            url=%s
            scriptPath=%s
            wikiId=%s
            version=%s
        """
        iniFile.write(template % (name,isodate,url,scriptPath,wikiId,version))
        iniFile.close()
        
    def __init__(self,iniFile):
        '''
        Constructor
        '''
        self.iniFile=iniFile
        self.site=None
        config=WikiBot.load_properties(iniFile)
        if 'wikiId' in config: 
            self.wikiId=config['wikiId'] 
        else: 
            raise Exception("wikiId missing for %s" % iniFile)
        self.family=self.wikiId.replace("-","").replace("_","")
        self.url=config['url'].replace("\\:",":")
        if not self.url:
            raise Exception("url is missing for %s" % iniFile)
        
        self.scriptPath=config['scriptPath']
        self.version=config['version']
        o=urlparse(self.url)
        self.scheme=o.scheme
        self.netloc=o.netloc
        self.scriptPath=o.path+self.scriptPath
        
        # if a user is configured a login will be tried     
        if 'user' in config:
            self.user=config['user']
            self.email=config['email']
            self.salt=config['salt']
            self.cypher=config['cypher']
            self.secret=config['secret']
        else:
            self.user=None    
        self.checkFamily()
        
    def getPassword(self):
        c=Crypt(self.cypher,20,self.salt)
        return c.decrypt(self.secret)
        
    def checkFamily(self):
        '''
        check if a family file exists and if not create it
        '''
        famfile=self.iniFile.replace(".ini",".py")
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
            mw_version=self.version.lower().replace("mediawiki ","")
            ispublic='False' if self.user is not None else 'True'
            code=template % (self.family,self.netloc,self.scriptPath,ispublic,mw_version,self.scheme)
            with open(famfile,"w") as py_file:
                py_file.write(code)
        config2.register_family_file(self.family, famfile)  
        if self.user:
            config2.usernames[self.family]['en'] = self.user
        #config2.authenticate[self.netloc] = (self.user,self.getPassword())
        self.site=pywikibot.Site('en',self.family)  
        if self.user:
            # needs patch as outlined in https://phabricator.wikimedia.org/T248471
            #self.site.login(password=self.getPassword())
            lm = LoginManager(password=self.getPassword(), site=self.site, user=self.user)
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
        text="%20s: %s %s" % (self.wikiId,self.url,self.user)    
        return text