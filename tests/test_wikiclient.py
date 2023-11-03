"""
Created on 2020-11-02

@author: wf
"""
from wikibot3rd.wikiclient import WikiClient
from tests.basetest import BaseTest

class TestWikiClient(BaseTest):
    """
    test Wiki client handling with mwclient library
    """
    def setUp(self, debug=False, profile=True):
        BaseTest.setUp(self, debug=debug, profile=profile)
        self.clients=WikiClient.get_clients().values()
        
    def optLogin(self,client):
        """
        optionally login to the given client if necessary
        """
        error = False
        status = ""
        try:
            needsLogin = client.needsLogin()
        except BaseException as _ex:
            status = "↯"
            error = True
            loggedIn = False
        if not error:
            if needsLogin:
                loggedIn = client.login()
            else:
                loggedIn = True
        print("✅" if loggedIn else f"❌{status}", end="")
        return error,loggedIn

    def testStatistics(self):
        """
        Test the get_site_statistics method of MediaWikiAPI
        """
        for i, client in enumerate(self.clients):
            print(f"{i+1:2}{client} ", end="")
            _error,loggedIn=self.optLogin(client)
            if loggedIn:
                statistics = client.get_site_statistics()
            
                # Assert that statistics is not None
                self.assertIsNotNone(statistics, "Statistics should not be None")
                
                # List of expected keys in the statistics
                expected_keys = [
                    "pages",
                    "articles",
                    "edits",
                    "images",
                    "users",
                    "activeusers",
                    "admins",
                    "jobs",
                ]
                
                # Loop through each expected key and assert it is in statistics
                for key in expected_keys:
                    self.assertIn(key, statistics, f"Statistics should include {key} count")
                print(statistics["pages"])
            else:
                print()
                
    def testWikiClient(self):
        """
        test clients
        """
        for i, client in enumerate(self.clients):
            print(f"{i+1:2}{client} ", end="")
            error,loggedIn=self.optLogin(client)
            if loggedIn:
                mainpage = client.site.site["mainpage"]
                page = client.getPage(mainpage)
                print("✅" if page.exists else "❌", end="")
            print()
        pass
