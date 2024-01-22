"""
Created on 2024-01-22

@author: wf
"""
import os

import yaml

from tests.basetest import BaseTest
from wikibot3rd.sso import SSO


class TestSSO(BaseTest):
    """
    test single sign on
    """

    def get_credentials(self):
        credentials_file = os.path.expanduser("~/.mediawiki-japi/cr_credentials.yaml")
        with open(credentials_file, "r") as file:
            credentials = yaml.safe_load(file)
        username = credentials["username"]
        password = credentials["password"]
        return username, password

    def test_mw_sso(self):
        """
        test mediawiki single sign on
        """
        if not self.inPublicCI():
            debug = self.debug
            debug = True
            db_username, db_password = self.get_credentials()
            sso = SSO(
                "cr.bitplan.com",
                "crwiki",
                db_username=db_username,
                db_password=db_password,
                debug=debug,
            )
            port_avail = sso.check_port()
            if not port_avail:
                print(f"SQL Port {sso.sql_port} not accessible")
                print("You might want to try opening an SSL tunnel to the port with")
                print(f"ssh -L {sso.sql_port}:{sso.host}:{sso.sql_port} {sso.host}")
            wiki_user = self.getWikiUser("cr")
            is_valid = sso.check_credentials(
                username=wiki_user.user, password=wiki_user.get_password()
            )
            self.assertTrue(is_valid)
