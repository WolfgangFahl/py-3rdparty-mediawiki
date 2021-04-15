'''
Created on 2020-11-02

@author: wf
'''
from wikibot.wikiuser import WikiUser
from mwclient import Site
from urllib.parse import urlparse
from wikibot.wiki import Wiki

class WikiClient(Wiki):
    '''
    access MediaWiki via mwclient library
    '''

    def __init__(self, wikiUser,debug=False):
        '''
        Constructor
        '''
        super(WikiClient,self).__init__(wikiUser,debug=debug) 
        self.wikiUser=wikiUser
        self.site=None
      
        
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
        
    def getWikiMarkup(self,pageTitle):
        '''
        get the wiki markup code (text) for the given page Title
        
        Args:
            pageTitle(str): the title of the page to retrieve
            
        Returns:
            str: the wiki markup code for the page
        '''
        page=self.getPage(pageTitle)
        markup=page.text()
        return markup
    
    def getHtml(self,pageTitle):
        '''
        get the HTML code for the given page Title
        
        Args:
            pageTitle(str): the title of the page to retrieve
        '''
        api=self.getSite().api("parse",page=pageTitle)
        if not "parse" in api:
            raise Exception("could not retrieve html for page %s" % pageTitle)
        html=api["parse"]["text"]["*"]
        return html        
        
    def getPage(self,pageTitle):
        page=self.getSite().pages[pageTitle]
        return page
    
    def savePage(self,pageTitle,pageContent,pageSummary):
        '''
        save the page
        Args:
            pageTitle(str): the title of the page
            pageContent(str): the wikimarkup content
            pageSummary(str): 
        '''
        newPage=self.getPage(pageTitle)
        newPage.edit(pageContent,pageSummary)
        
    @staticmethod
    def getClients():
        clients={}
        for wikiUser in WikiUser.getWikiUsers().values():
            wikiClient=WikiClient(wikiUser)
            clients[wikiUser.wikiId]=wikiClient
        return clients
        
    @staticmethod
    def ofWikiId(wikiId,lenient=True,debug=False):
        wikiUser=WikiUser.ofWikiId(wikiId,lenient=lenient)
        wikibot=WikiClient(wikiUser,debug=debug)
        return wikibot
    
    @staticmethod
    def ofWikiUser(wikiUser):
        wikibot=WikiClient(wikiUser)
        return wikibot
        