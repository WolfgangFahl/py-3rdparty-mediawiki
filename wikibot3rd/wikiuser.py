"""
Created on 2020-11-01

@author: wf
"""

"""
Created on 2020-11-01

@author: wf
"""

import datetime
import getpass
import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Dict

from wikibot3rd.crypt import Crypt


@dataclass
class WikiCredentials:
    """
    Base class for wiki credentials
    """

    password: str = field(default=None, repr=False)
    cypher: str = field(default=None, repr=False)
    secret: str = field(default=None, repr=False)
    salt: str = field(default=None, repr=False)

    def __post_init__(self):
        """
        if a password is available immediately encrypt it
        """
        if self.password is not None:
            self.encrypt(self.password)
            self.password = None

    @property
    def encrypted(self) -> bool:
        """
        Property to check if the credentials are encrypted.

        Returns:
            bool: True if the credentials are encrypted, False otherwise.
        """
        encrypted = self.cypher is not None
        return encrypted

    @property
    def needs_encrypt(self) -> bool:
        needs_encrypt = self.password is not None and not self.encrypted
        return needs_encrypt

    def encrypt(self, password: str):
        """
        Encrypt the given password
        """
        crypt = Crypt.getRandomCrypt()
        self.secret = crypt.encrypt(password)
        self.cypher = crypt.cypher.decode()
        self.salt = crypt.salt.decode()

    def decrypt(self) -> str:
        """
        Decrypt and return the password
        """
        if not self.encrypted:
            raise ValueError("Data is not encrypted")
        c = Crypt(self.cypher, 20, self.salt)
        password = c.decrypt(self.secret)
        return password

    def get_password(self) -> str:
        """
        get my decrypted password

        Returns:
            str: the decrypted password for this user
        """
        if not self.encrypted:
            raise ValueError("clear text password state")
        password = self.decrypt()
        return password

    def getPassword(self) -> str:
        return self.get_password()


@dataclass
class WikiUserData(WikiCredentials):
    """
    User credentials for a specific wiki
    """

    wikiId: str = None
    url: str = None
    scriptPath: str = ""
    version: str = "MediaWiki 1.39.10"
    user: str = None
    email: str = None
    is_smw: bool = True

    def __post_init__(self):
        WikiCredentials.__post_init__(self)
        if isinstance(self.is_smw, str):
            normalized_value = self.is_smw.strip().lower()
            if normalized_value in {"yes", "y", "true"}:
                self.is_smw = True
            elif normalized_value in {"no", "n", "false"}:
                self.is_smw = False
            else:
                raise ValueError(f"Invalid value for is_smw: {self.is_smw}")


@dataclass
class WikiUser(WikiUserData):
    """
    WikiUser handling
    """

    interactive: bool = False
    debug: bool = False
    lenient: bool = True
    filePath: str = None
    yes: bool = False

    def get_wiki_url(self) -> str:
        """
        return the full url of this wiki

        Returns:
            str: the full url of this wiki
        """
        return f"{self.url}{self.scriptPath}"

    def getWikiUrl(self) -> str:
        """
        return the full url of this wiki

        Returns:
            str: the full url of this wiki
        """
        return self.get_wiki_url()

    def getInteractiveFields(self):
        """
        Get the non-credential fields from WikiUserData plus 'password' for interactive input.
        """
        # Get all field names from WikiCredentials to exclude
        credentials_field_names = {field.name for field in fields(WikiCredentials)}

        # Create a list to hold the non-credential fields in the declared order
        interactive_fields = []

        # Iterate over WikiUserData fields in the declared order
        for field in fields(WikiUserData):
            if field.name not in credentials_field_names:
                interactive_fields.append(field)

        # Add the 'password' field explicitly, assuming it's part of WikiCredentials
        password_field = next(
            field for field in fields(WikiCredentials) if field.name == "password"
        )
        interactive_fields.append(password_field)

        return interactive_fields

    def ask_password(self) -> str:
        """
        Ask the user for a password twice to ensure it is entered correctly.

        Returns:
            str: The confirmed password entered by the user.
        """
        while True:
            password = getpass.getpass("Password (hidden): ")
            if not password:
                print("Password cannot be empty. Please enter a valid password.")
                continue
            confirm_password = getpass.getpass("Confirm Password (hidden): ")
            if password == confirm_password:
                return password
            else:
                print("Passwords do not match. Please try again.")

    def interactiveSave(
        self, yes: bool = False, interactive: bool = False, filePath=None
    ):
        """
        save me

        Args:
            yes (bool): if True save without asking
            interactive (bool): if True get interactive input
            filePath (str): the path where to save the credentials ini file
        """
        text = ""
        interactive_fields = self.getInteractiveFields()

        for field in interactive_fields:
            value = getattr(self, field.name)
            if interactive:
                print(text)
                if field.name == "password":
                    # Ensure password is provided
                    if not value:
                        inputValue = self.ask_password()  # Ask for password twice
                        self.encrypt(inputValue)  # Encrypt immediately after input
                        value = "********"  # Placeholder for display purposes
                else:
                    inputMsg = f"{field.name} ({value}): "
                    inputValue = input(inputMsg)
                    if inputValue:
                        setattr(self, field.name, inputValue)
                        value = inputValue
            text += f"\n  {field.name}={value}"
        if not yes:
            answer = input(
                f"shall i store credentials for {text}\nto an ini file? yes/no y/n"
            )
            yes = "y" in answer or "yes" in answer
        if yes:
            ini_path = self.save(filePath)
            print(f"wikiuser details available at {ini_path}")

    def __str__(self):
        return f"{self.user} {self.wikiId}"

    @staticmethod
    def getIniPath():
        """
        get the path for the ini file
        """
        return str(Path.home() / ".mediawiki-japi")

    @staticmethod
    def iniFilePath(wikiId: str):
        """
        get the path for the ini file for the given wikiId
        """
        user = getpass.getuser()
        iniPath = WikiUser.getIniPath()
        return f"{iniPath}/{user}_{wikiId}.ini"

    @classmethod
    def ofWikiId(cls, wikiId: str, lenient=False) -> "WikiUser":
        """
        create a wikiUser for the given wikiId

        Args:
            wikiId (str): the wikiId of the user to be created
            lenient (bool): if True ignore parsing errors in the ini file

        Returns:
            WikiUser: the wikiUser for this wikiId
        """
        path = cls.iniFilePath(wikiId)
        try:
            config = cls.readPropertyFile(path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f'the wiki with the wikiID "{wikiId}" does not have a corresponding configuration file ... you might want to create one with the wikiuser command'
            )
        return cls.ofDict(config, lenient=lenient)

    def save(self, iniFilePath=None) -> str:
        """
        save me to a propertyFile

        Returns:
            str: the path of the property file
        """
        if iniFilePath is None:
            iniPath = self.getIniPath()
            os.makedirs(iniPath, exist_ok=True)
            iniFilePath = self.iniFilePath(self.wikiId)

        with open(iniFilePath, "w") as iniFile:
            isodate = datetime.datetime.now().isoformat()
            content = f"# Mediawiki JAPI credentials for {self.wikiId}\n# created by py-3rdparty-mediawiki WikiUser at {isodate}\n"
            for field in fields(WikiUserData):
                value = getattr(self, field.name)
                if value is not None:
                    content += f"{field.name}={value}\n"
            iniFile.write(content)
        return iniFilePath

    @staticmethod
    def readPropertyFile(filepath, sep="=", comment_char="#") -> Dict[str, str]:
        """
        Read the file passed as parameter as a properties file.

        https://stackoverflow.com/a/31852401/1497139

        """
        props = {}
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    props[key] = value
        return props

    @classmethod
    def getWikiUsers(cls, lenient: bool = False):
        """
        get all WikiUsers from the ini files in the iniPath
        """
        wikiUsers = {}
        iniPath = cls.getIniPath()
        if os.path.isdir(iniPath):
            for entry in os.scandir(iniPath):
                if entry.name.endswith(".ini") and entry.is_file():
                    try:
                        config = cls.readPropertyFile(entry.path)
                        wikiUser = cls.ofDict(config, lenient=lenient)
                        wikiUsers[wikiUser.wikiId] = wikiUser
                    except Exception as ex:
                        print(f"error in {entry.path}: {str(ex)}")
        return wikiUsers

    @classmethod
    def ofDict(cls, userDict: dict, encrypted=True, lenient=False, encrypt=True):
        """
        create a WikiUser from the given dictionary

        Args:
        userDict (dict): dictionary with WikiUser properties
        encrypted(bool): if True the password is encrypted in the dict
        lenient (bool): if True ignore missing fields
        encrypt (bool): if True encrypt the password (if not encrypted yet)

        Returns:
        WikiUser: the WikiUser created from the dictionary
        """
        if "url" in userDict and userDict["url"] is not None:
            # fix broken escapes e.g. http\://waihekepedia.bitplan.com
            userDict["url"] = userDict["url"].replace(r"\:", ":")

        # is the password currently encrypted?
        is_encrypted = userDict.get("cypher") is not None

        if encrypted != is_encrypted and not lenient:
            raise Exception("Encryption state mismatch")

        err_msg = ""
        try:
            wikiUser = cls(**userDict)
        except Exception as ex:
            err_msg = str(ex) + "\n"
        if wikiUser and wikiUser.is_smw:
            for field in fields(WikiUserData):
                if field.name not in userDict and not lenient:
                    if field.default is None:
                        if is_encrypted and field.name in ["cypher", "secret", "salt"]:
                            err_msg += f"\n{field.name} missing for encrypted data"
                        elif field.name not in [
                            "cypher",
                            "secret",
                            "salt",
                            "password",
                            "encrypted",
                        ]:
                            err_msg += f"\n{field.name} missing"
        if err_msg:
            raise Exception(err_msg)

        if encrypt and wikiUser.needs_encrypt:
            wikiUser.encrypt(wikiUser.password)
        return wikiUser
