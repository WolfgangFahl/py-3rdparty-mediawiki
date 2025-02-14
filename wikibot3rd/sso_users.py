'''
Created on 2025-02-14

@author: wf
'''
import os
import yaml
from wikibot3rd.sso import SSO

class Sso_Users:
    """
    Single Sign on User handling
    """

    def __init__(self,
                 server_url:str,
                 wiki_id: str,
                 credentials_path:str,
                 debug: bool = False):
        """
        construct the SsoUsers environment

        Args:
            debug(bool): if True enable debug mode
        """
        debug = debug
        self.get_credentials(credentials_path=credentials_path)
        self.sso = SSO(
            server_url,
            wiki_id,
            db_username=self.db_username,
            db_password=self.db_password,
            debug=debug,
        )
        self.port_avail = self.sso.check_port()

    def check_password(self, username: str, password: str) -> bool:
        """
        check the password
        """
        is_valid = self.sso.check_credentials(
            username=username,
            password=password)
        return is_valid

    def get_credentials(self,credentials_path:str):
        """
        get the database credentials
        """
        credentials_file = os.path.expanduser(credentials_path)
        with open(credentials_file, "r") as file:
            credentials = yaml.safe_load(file)
        self.db_username = credentials["username"]
        self.db_password = credentials["password"]
        self.secret = credentials["secret"]