'''
Created on 2020-11-05

@author: wf
'''

class Wiki(object):
    '''
    common interface for WikiBot and WikiClient
    '''

    def __init__(self,wikiUser,debug=False):
        '''
        Constructor
        
        Args:
            wikiUser(WikiUser): the wiki user to initialize me for
        '''
        self.wikiUser=wikiUser
        self.debug=debug
        
    def __str__(self):
        '''
        return a string representation of myself
        '''
        wu=self.wikiUser
        botType=type(self).__name__
        text="%20s(%10s): %15s %s" % (wu.wikiId,botType,wu.user,wu.url)    
        return text
        