'''
Created on 2020-11-02

@author: wf
'''
from wikibot.wikiuser import WikiUser

class WikiClient(object):
    '''
    access MediaWiki via mwclient library
    '''


    def __init__(self, wikiUser):
        '''
        Constructor
        '''
        self.wikiUser=wikiUser
        
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
        