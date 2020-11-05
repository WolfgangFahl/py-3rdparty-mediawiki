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
        