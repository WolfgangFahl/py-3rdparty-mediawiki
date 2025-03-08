"""
Created on 2025-02-14

@author: wf
"""

import os
import yaml
import logging
from wikibot3rd.sso import SSO

class Sso_Users:
    """
    Single Sign on User handling
    """

    def __init__(self,
        solution_name: str,
        debug: bool = False,
        credentials_path: str = None):
        """
        construct the SsoUsers environment

        Args:
            solution_name(str): name of the solution to derive credentials path from
            debug(bool): if True enable debug mode
            credentials_path(str): optional override for credentials file path (for testing)
        """
        self.debug = debug
        self.is_available = False

        # Allow override for testing
        self.credentials_path = credentials_path or self.get_default_credentials_path(solution_name)

        try:
            self.get_credentials()
            self.sso = SSO(
                host=self.server_url,
                database=self.database,
                db_username=self.db_username,
                db_password=self.db_password,
                debug=debug,
            )
            self.port_avail = self.sso.check_port()
            self.is_available = True
        except FileNotFoundError:
            msg=f"SSO credentials file not found at {self.credentials_path}"
            logging.warning(msg)
        except Exception as ex:
            msg=f"SSO initialization failed: {str(ex)}"
            logging.warning(msg)

    def get_default_credentials_path(self, solution_name: str) -> str:
        """
        Returns the default credentials file path.
        """
        return os.path.expanduser(f"~/.solutions/{solution_name}/sso_credentials.yaml")

    def get_credentials(self):
        """
        Get the database credentials from the credential file.
        """
        credentials_file = os.path.expanduser(self.credentials_path)
        with open(credentials_file, "r") as file:
            credentials = yaml.safe_load(file)
        self.db_username = credentials["username"]
        self.db_password = credentials["password"]
        self.secret = credentials["secret"]
        self.server_url = credentials["server_url"]
        self.database=credentials.get("database")
        self.wiki_id = credentials["wiki_id"]
        if not self.database:
            self.database=self.wiki_id

    def check_password(self, username: str, password: str) -> bool:
        """
        Check if the given username and password are valid by delegating to SSO

        Args:
            username (str): The username to check
            password (str): The password to verify

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        ok=False
        if not self.is_available:
            logging.warning("SSO is not available - password check failed")

        elif not self.port_avail:
            logging.warning(f"Database port on {self.server_url} is not accessible")
        else:
            try:
                ok=self.sso.check_credentials(username, password)
            except Exception as ex:
                if self.debug:
                    logging.error(f"Password check failed: {str(ex)}")
        return ok

