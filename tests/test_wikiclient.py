'''
Created on 2020-11-02

@author: wf
'''
import unittest
from wikibot3rd.wikiclient import WikiClient
from tests.basetest import BaseTest

class TestWikiClient(BaseTest):
    '''
    test Wiki client handling with mwclient library
    '''
    
    def testWikiClient(self):
        '''
        test clients
        '''
        for i,client in enumerate(WikiClient.getClients().values()):
            print (f"{i:2}{client} ",end="")
            error=False
            status=""
            try:
                needsLogin=client.needsLogin()
            except BaseException as _ex:
                status="↯"
                error=True
                loggedIn=False
            if not error:
                if needsLogin:
                    loggedIn=client.login()
                else:
                    loggedIn=True
            print ('✅' if loggedIn else f'❌{status}',end='')
            if loggedIn:
                mainpage=client.site.site["mainpage"]
                page=client.getPage(mainpage)
                print ('✅' if page.exists else '❌',end='')
            print()
        pass
    
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()