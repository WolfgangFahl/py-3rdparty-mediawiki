'''
Created on 2020-11-02

@author: wf
'''
from wikibot.wikiuser import WikiUser
from mwclient import Site
from urllib.parse import urlparse

class WikiClient(object):
    '''
    access MediaWiki via mwclient library
    '''

    def __init__(self, wikiUser,debug=False):
        '''
        Constructor
        '''
        self.wikiUser=wikiUser
        self.site=None
        self.debug=debug
        
    def getSite(self):
        '''
        get my site
        '''
        if self.site is None:
            o=urlparse(self.wikiUser.url)
            scheme=o.scheme
            host=o.netloc
            path=o.path+self.wikiUser.scriptPath   
            path="%s/" % path
            self.site=Site(host=host, path=path, scheme=scheme)
        return self.site
        
    def login(self):
        '''
        login
        '''
        wu=self.wikiUser
        try:
            self.getSite().login(username=wu.user,password=wu.getPassword())
            return True
        except Exception as ex:
            if self.debug:
                print("login failed: %s" % str(ex))
            return False
        
    def getPage(self,pageTitle):
        page=self.getSite().pages[pageTitle]
        return page
    
    def __str__(self):
        wu=self.wikiUser
        text="%20s: %15s %s" % (wu.wikiId,wu.user,wu.url)    
        return text
        
    @staticmethod
    def getClients():
        clients={}
        for wikiUser in WikiUser.getWikiUsers().values():
            wikiClient=WikiClient(wikiUser)
            clients[wikiUser.wikiId]=wikiClient
        return clients
        
    @staticmethod
    def ofWikiId(wikiId):
        wikiUser=WikiUser.ofWikiId(wikiId)
        wikibot=WikiClient(wikiUser)
        return wikibot
    
    @staticmethod
    def ofWikiUser(wikiUser):
        wikibot=WikiClient(wikiUser)
        return wikibot
        