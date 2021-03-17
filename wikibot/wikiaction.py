'''
Created on 02.02.2021

@author: wf
'''
from wikibot.lambda_action import Code,LambdaAction
from lodstorage.query import Query

class WikiAction(object):
    '''
    perform an action on the given semantic media wiki
    '''

    def __init__(self, smw, debug=False):
        '''
        Constructor
        '''
        self.smw=smw
        self.debug=debug
        self.sourceCodeResult=self.getSourceCodes()
        
    def getSourceCodes(self):
        ask="""{{#ask: [[Concept:Sourcecode]]
|mainlabel=Sourcecode
| ?Sourcecode id = id
| ?Sourcecode lang = lang
| ?Sourcecode text = text
| ?Sourcecode author = author
| ?Sourcecode since = since
| ?Sourcecode url = url
}}"""   
        result=self.smw.query(ask)
        return result
    
    def getLambdaAction(self,name,queryName,actionName):
        '''
        get an action from the result with the given query and actionName
        '''
        if self.debug:
            print("lambdaAction with query: %s and action: %s" % (queryName,actionName))
        qCode=self.sourceCodeResult[queryName]
        query=Query(name=qCode['id'],query=qCode['text'],lang=qCode['lang'])
        sCode=self.sourceCodeResult[actionName]
        code=Code(name=sCode['id'],text=sCode['text'],lang=sCode['lang'])
        action=LambdaAction(name,query=query,code=code)
        return action
          
        
    
        
        
        