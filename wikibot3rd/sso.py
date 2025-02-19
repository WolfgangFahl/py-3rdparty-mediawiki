"""
Created on 2024-01-22

@author: wf

with ChatGPT-4 prompting
"""

import base64
import hashlib
import socket
import traceback
from typing import Dict, Optional

import mysql.connector
from lodstorage.yamlable import lod_storable
from mysql.connector import pooling


@lod_storable
class User:
    """
    Mediawiki user details
    """

    id: int
    name: str
    real_name: str
    password: str  # hashed password
    email: str
    touched: str
    editcount: int
    is_admin: Optional[bool] = False

    def __post_init__(self):
        # Safely convert binary fields to strings if they are not already
        if isinstance(self.password, bytes):
            self.password = self.password.decode("utf-8", errors="replace")
        if isinstance(self.touched, bytes):
            self.touched = self.touched.decode("utf-8", errors="replace")


class SSO:
    """
    A class to implement MediaWiki single sign-on support.

    This class provides functionality to connect to a MediaWiki database,
    verify user credentials, and handle database connections with pooling.

    Attributes:
        host (str): The host of the MediaWiki database.
        database (str): The name of the MediaWiki database.
        sql_port (int): The SQL port for the database connection.
        db_username (Optional[str]): The database username.
        db_password (Optional[str]): The database password.
        with_pool (bool): Flag to determine if connection pooling is used.
        timeout (float): The timeout for checking SQL port availability.
        debug (Optional[bool]): Flag to enable debug mode.
    """

    def __init__(
        self,
        host: str,
        database: str,
        sql_port: int = 3306,
        db_username: Optional[str] = None,
        db_password: Optional[str] = None,
        with_pool: bool = True,
        timeout: float = 3,
        debug: Optional[bool] = False,
    ):
        """
        Constructs all the necessary attributes for the SSO object.

        Args:
            host (str): The host of the MediaWiki database.
            database (str): The name of the MediaWiki database.
            sql_port (int): The SQL port for the database connection.
            db_username (Optional[str]): The database username.
            db_password (Optional[str]): The database password.
            with_pool (bool): Flag to determine if connection pooling is used.
            timeout (float): The timeout for checking SQL port availability.
            debug (Optional[bool]): Flag to enable debug mode.
        """
        self.host = host
        self.database = database
        self.sql_port = sql_port
        self.timeout = timeout
        self.db_username = db_username
        self.db_password = db_password
        self.debug = debug
        self.pool = self.get_pool() if with_pool else None

    def get_pool(self) -> pooling.MySQLConnectionPool:
        """
        Creates a connection pool for the database.

        Returns:
            MySQLConnectionPool: A pool of database connections.
        """
        pool_config = {
            "pool_name": "mypool",
            "pool_size": 2,
            "host": self.host,
            "user": self.db_username,
            "password": self.db_password,
            "database": self.database,
            "raise_on_warnings": True,
        }
        return pooling.MySQLConnectionPool(**pool_config)

    def check_port(self) -> bool:
        """
        Checks if the specified SQL port is accessible on the configured host.

        Returns:
            bool: True if the port is accessible, False otherwise.
        """
        try:
            with socket.create_connection(
                (self.host, self.sql_port), timeout=self.timeout
            ):
                return True
        except socket.error as ex:
            if self.debug:
                print(f"Connection to {self.host} port {self.sql_port} failed: {ex}")
                traceback.print_exc()
            return False

    def verify_password(self, password: str, hash_value: str) -> bool:
        """
        Verifies a password against a stored hash value.

        Args:
            password (str): The password to verify.
            hash_value (str): The stored hash value to compare against.

        Returns:
            bool: True if the password matches the hash value, False otherwise.
        """
        parts = hash_value.split(":")
        if len(parts) != 7:
            raise ValueError("Invalid hash format")

        (
            _,
            pbkdf2_indicator,
            hash_algorithm,
            iterations,
            _,
            salt,
            hashed_password,
        ) = parts

        if pbkdf2_indicator != "pbkdf2":
            raise ValueError("verify_password expects pbkdf2 hashes")

        iterations = int(iterations)

        def fix_base64_padding(string: str) -> str:
            return string + "=" * (-len(string) % 4)

        salt = fix_base64_padding(salt)
        hashed_password = fix_base64_padding(hashed_password)

        salt = base64.b64decode(salt)
        hashed_password = base64.b64decode(hashed_password)

        if hash_algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

        new_hash = hashlib.pbkdf2_hmac(
            hash_algorithm, password.encode("utf-8"), salt, iterations
        )
        return new_hash == hashed_password

    def get_user(self, username: str) -> Optional[User]:
        """
        Retrieve details of a user by username.
        Returns a User object if found, otherwise None.
        """
        mw_username = username[0].upper() + username[1:]
        user_record = self.fetch_user_data_from_database(mw_username)
        if user_record:
            return User(
                id=user_record["user_id"],
                name=user_record["user_name"],
                real_name=user_record["user_real_name"],
                password=user_record["user_password"],
                email=user_record["user_email"],
                touched=user_record["user_touched"],
                editcount=user_record["user_editcount"],
                is_admin=user_record["is_sysop"] > 0,
            )
        return None

    def query(self, connection, sql_query, params) -> Dict:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_query, params)
        record = cursor.fetchone()
        cursor.close()
        return record

    def fetch_user_data_from_database(self, mw_username: str) -> Optional[dict]:
        """
        Fetch user data from the database.

        Args:
            mw_username(str): the Mediawiki username
        """
        user_record = None
        try:
            connection = (
                self.pool.get_connection()
                if self.pool
                else mysql.connector.connect(
                    host=self.host,
                    user=self.db_username,
                    password=self.db_password,
                    database=self.database,
                )
            )
            # JOIN query: Fetch user data and sysop status
            sql_query = """
            SELECT u.*,
                   COUNT(ug.ug_group) AS is_sysop
            FROM `user` u
            LEFT JOIN `user_groups` ug ON u.user_id = ug.ug_user AND ug.ug_group = 'sysop'
            WHERE u.user_name = %s
            GROUP BY u.user_id
            """
            user_record = self.query(connection, sql_query, (mw_username,))
        except Exception as ex:
            if self.debug:
                print(f"Database error: {ex}")
                traceback.print_exc()
        finally:
            if connection and connection.is_connected():
                connection.close()
        return user_record

    def check_credentials(self, username: str, password: str) -> bool:
        """
        Checks the validity of MediaWiki username and password.

        Args:
            username (str): The MediaWiki username.
            password (str): The password to verify.

        Returns:
            bool: True if the credentials are valid, False otherwise.
        """
        is_valid = False
        user = self.get_user(username)
        if user:
            stored_hash = user.password
            is_valid = self.verify_password(password, stored_hash)
        elif self.debug:
            print(f"Username {username} not found in {self.database} on {self.host}")
        return is_valid
