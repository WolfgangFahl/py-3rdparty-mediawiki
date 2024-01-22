"""
Created on 2020-11-01

@author: wf
"""

import datetime
import getpass
import os
import sys
import traceback
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import makedirs
from os.path import isdir
from pathlib import Path

from wikibot3rd.crypt import Crypt
from wikibot3rd.version import Version


class WikiUser(object):
    """
    User credentials for a specific wiki
    """

    def __init__(self):
        """
        construct me
        """
        # set None values for all fields
        for field in WikiUser.getFields():
            setattr(self, field, None)

    def get_password(self):
        password = self.getPassword()
        return password

    def getPassword(self):
        """
        get my decrypted password

        Returns:
            str: the decrypted password for this user
        """
        c = Crypt(self.cypher, 20, self.salt)
        return c.decrypt(self.secret)

    def get_wiki_url(self):
        wiki_url = self.getWikiUrl()
        return wiki_url

    def getWikiUrl(self):
        """
        return the full url of this wiki

        Returns:
            str: the full url of this wiki
        """
        url = f"{self.url}{self.scriptPath}"
        return url

    def interactiveSave(
        self, yes: bool = False, interactive: bool = False, filePath=None
    ):
        """
        save me

        Args:
            yes(bool): if True save without asking
            interactive(bool): if True get interactive input
            filePath(str): the path where to save the credentials ini file
        """
        fields = WikiUser.getFields(encrypted=False)
        text = ""
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
            else:
                value = None
            if interactive:
                print(text)
                inputMsg = f"{field} ({value}): "
                inputValue = input(inputMsg)
                if inputValue:
                    setattr(self, field, inputValue)
                    value = inputValue
            text += f"\n  {field}={value}"
        # encrypt
        self.encrypt()
        if not yes:
            answer = input(
                f"shall i store credentials for {text}\nto an ini file? yes/no y/n"
            )
            yes = "y" in answer or "yes" in answer
        if yes:
            self.save(filePath)

    def encrypt(self, remove: bool = True):
        """
        encrypt my clear text password

        Args:
            remove(bool): if True remove the original password
        """
        crypt = Crypt.getRandomCrypt()
        self.secret = crypt.encrypt(self.password)
        self.cypher = crypt.cypher.decode()
        self.salt = crypt.salt.decode()
        if remove:
            delattr(self, "password")

    def __str__(self):
        text = f"{self.user} {self.wikiId}"
        return text

    @staticmethod
    def getIniPath():
        home = str(Path.home())
        path = f"{home}/.mediawiki-japi"
        return path

    @staticmethod
    def iniFilePath(wikiId: str):
        user = getpass.getuser()
        iniPath = WikiUser.getIniPath()
        iniFilePath = f"{iniPath}/{user}_{wikiId}.ini"
        return iniFilePath

    @staticmethod
    def ofWikiId(wikiId: str, lenient=False):
        """
        create a wikiUser for the given wikiId

        Args:
            wikiId(str): the wikiId of the user to be created
            lenient(bool): if True ignore parsing errors in the ini file

        Returns:
            WikiUser: the wikiUser for this wikiId
        """
        path = WikiUser.iniFilePath(wikiId)
        try:
            config = WikiUser.readPropertyFile(path)
        except FileNotFoundError as _e:
            errMsg = f'the wiki with the wikiID "{wikiId}" does not have a corresponding configuration file ... you might want to create one with the wikiuser command'
            raise FileNotFoundError(errMsg)
        wikiUser = WikiUser.ofDict(config, lenient=lenient)
        return wikiUser

    def save(self, iniFilePath=None):
        """
        save me to a propertyFile
        """
        if iniFilePath is None:
            iniPath = WikiUser.getIniPath()
            if not isdir(iniPath):
                makedirs(iniPath)
            iniFilePath = WikiUser.iniFilePath(self.wikiId)

        iniFile = open(iniFilePath, "w")
        isodate = datetime.datetime.now().isoformat()
        template = """# Mediawiki JAPI credentials for %s
# created by py-3rdparty-mediawiki WikiUser at %s
"""
        content = template % (self.wikiId, isodate)
        for field in WikiUser.getFields():
            value = self.__dict__[field]
            if value is not None:
                content += "%s=%s\n" % (field, value)

        iniFile.write(content)
        iniFile.close()

    @staticmethod
    def readPropertyFile(filepath, sep="=", comment_char="#"):
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

    @staticmethod
    def getWikiUsers(lenient: bool = False):
        wikiUsers = {}
        iniPath = WikiUser.getIniPath()
        if os.path.isdir(iniPath):
            with os.scandir(iniPath) as it:
                for entry in it:
                    if entry.name.endswith(".ini") and entry.is_file():
                        try:
                            config = WikiUser.readPropertyFile(entry.path)
                            wikiUser = WikiUser.ofDict(config, lenient=lenient)
                            wikiUsers[wikiUser.wikiId] = wikiUser
                        except Exception as ex:
                            print("error in %s: %s" % (entry.path, str(ex)))
        return wikiUsers

    @staticmethod
    def getFields(encrypted=True):
        # copy fields
        fields = ["wikiId", "url", "scriptPath", "version", "user", "email"]
        passwordFields = ["cypher", "secret", "salt"] if encrypted else ["password"]
        result = []
        result.extend(fields)
        result.extend(passwordFields)
        return result

    @staticmethod
    def ofDict(userDict, encrypted=True, lenient=False, encrypt=True):
        wikiUser = WikiUser()
        # fix http\: entries from Java created entries
        if "url" in userDict and userDict["url"] is not None:
            userDict["url"] = userDict["url"].replace("\:", ":")

        for field in WikiUser.getFields(encrypted):
            if field in userDict:
                wikiUser.__dict__[field] = userDict[field]
            else:
                if not lenient:
                    raise Exception(f"{field} missing")
        if not encrypted and encrypt:
            wikiUser.encrypt()
        return wikiUser


__version__ = Version.version
__date__ = Version.date
__updated__ = Version.updated
DEBUG = False


def main(argv=None):  # IGNORE:C0111
    """
    WikiUser credential handling
    """

    if argv is None:
        argv = sys.argv[1:]

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = "%%(prog)s %s (%s)" % (
        program_version,
        program_build_date,
    )
    program_shortdesc = "WikiUser credential handling"
    user_name = "Wolfgang Fahl"

    program_license = """%s

  Created by %s on %s.
  Copyright 2020-2023 Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
""" % (
        program_shortdesc,
        user_name,
        str(__date__),
    )

    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license, formatter_class=RawDescriptionHelpFormatter
        )
        parser.add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="count",
            help="set debug level [default: %(default)s]",
        )
        parser.add_argument(
            "-V", "--version", action="version", version=program_version_message
        )
        parser.add_argument("-i", "--interactive", action="store_true")
        parser.add_argument("-e", "--email", dest="email", help="email of the user")
        parser.add_argument("-f", "--file", dest="filePath", help="ini-file path")
        parser.add_argument("-l", "--url", dest="url", help="url of the wiki")
        parser.add_argument(
            "-s",
            "--scriptPath",
            dest="scriptPath",
            help="script path default: %(default)s)",
            default="",
        )
        parser.add_argument("-p", "--password", dest="password", help="password")
        parser.add_argument(
            "-u",
            "--user",
            dest="user",
            help="os user id default: %(default)s)",
            default=getpass.getuser(),
        )
        parser.add_argument(
            "-v",
            "--wikiVersion",
            dest="version",
            default="MediaWiki 1.39.1",
            help="version of the wiki default: %(default)s)",
        )
        parser.add_argument("-w", "--wikiId", dest="wikiId", help="wiki Id")
        parser.add_argument(
            "-y",
            "--yes",
            dest="yes",
            action="store_true",
            help="immediately store without asking",
        )
        # Process arguments
        args = parser.parse_args(argv)
        argsDict = vars(args)
        wikiuser = WikiUser.ofDict(
            argsDict, encrypted=False, lenient=True, encrypt=False
        )
        wikiuser.interactiveSave(args.yes, args.interactive, args.filePath)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise (e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        if args.debug:
            print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
