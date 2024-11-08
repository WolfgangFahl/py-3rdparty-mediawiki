"""
Created on 2024-01-22

@author: wf
"""

import os

import yaml

from tests.base_wiki_test import BaseWikiTest
from wikibot3rd.sso import SSO


class TestSSO(BaseWikiTest):
    """
    test single sign on
    """

    def setUp(self, debug=False, profile=True):
        BaseWikiTest.setUp(self, debug=debug, profile=profile)
        if not self.inPublicCI():
            db_username, db_password = self.get_credentials()
            self.sso = SSO(
                "cr.bitplan.com",
                "crwiki",
                db_username=db_username,
                db_password=db_password,
                debug=debug,
            )
            self.wiki_user = self.getWikiUser("cr")

    def get_credentials(self):
        """
        get the mediawiki credentials of user
        """
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
            port_avail = self.sso.check_port()
            if not port_avail:
                print(f"SQL Port {self.sso.sql_port} not accessible")
                print("You might want to try opening an SSL tunnel to the port with")
                print(
                    f"ssh -L {self.sso.sql_port}:{self.sso.host}:{self.sso.sql_port} {self.sso.host}"
                )
            is_valid = self.sso.check_credentials(
                username=self.wiki_user.user, password=self.wiki_user.get_password()
            )
            self.assertTrue(is_valid)

    def test_get_user(self):
        """
        Test the retrieval of a user's details using the get_user method.
        """
        if not self.inPublicCI():
            user = self.sso.get_user(self.wiki_user.user)
            yaml_str = user.to_yaml()
            debug = self.debug
            # debug=True
            if debug:
                print(yaml_str)

            for field in [
                "id",
                "name",
                "real_name",
                "password",
                "email",
                "touched",
                "editcount",
                "is_admin",
            ]:
                self.assertTrue(f"{field}:" in yaml_str)
