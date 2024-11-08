"""
Created on 2020-03-24

@author: wf
"""

import re
import sys
from os.path import isfile
from urllib.parse import urlparse

from wikibot3rd.wiki import Wiki
from wikibot3rd.wikiuser import WikiUser

try:
    import pywikibot
except Exception as ex:
    # ignore pywikibot setup problems?
    print("pywikibot config issue see https://phabricator.wikimedia.org/T278076")
    print("%s" % str(ex), file=sys.stderr)
    pass


class WikiBot(Wiki):
    """
    WikiBot
    """

    @staticmethod
    def getBots(limit=None, name=None, valueExpr=None):
        bots = {}
        wikiUsers = WikiUser.getWikiUsers().values()
        for wikiUser in wikiUsers:
            selected = True
            if name is not None:
                value = wikiUser.__dict__[name]
                found = re.search(valueExpr, value)
                selected = found is not None
            if selected:
                wikibot = WikiBot(wikiUser)
                bots[wikiUser.wikiId] = wikibot
                if limit is not None and len(bots) >= limit:
                    break
        return bots

    @staticmethod
    def ofWikiId(wikiId, lenient: bool = True, debug: bool = False):
        wikiUser = WikiUser.ofWikiId(wikiId, lenient=lenient)
        wikibot = WikiBot(wikiUser, debug=debug)
        return wikibot

    @staticmethod
    def ofWikiUser(wikiUser, debug: bool = False):
        wikibot = WikiBot(wikiUser, debug=debug)
        return wikibot

    def __init__(
        self, wikiUser, debug: bool = False, withLogin: bool = False, maxRetries=2
    ):
        """
        Constructor

        Args:
            wikiUser(WikiUser): the wiki user to initialize me for
            debug(bool): True if debug mode should be on
            withLogin(bool): True if init should automatically login
        """
        pywikibot.config.max_retries = maxRetries
        super(WikiBot, self).__init__(wikiUser, debug)
        self.family = wikiUser.wikiId.replace("-", "").replace("_", "")
        self.url = wikiUser.url.replace("\\:", ":")
        if not self.url:
            raise Exception("url is missing for %s" % wikiUser.wikiId)

        self.scriptPath = wikiUser.scriptPath
        self.version = wikiUser.version
        o = urlparse(self.url)
        self.scheme = o.scheme
        self.netloc = o.netloc
        msg = f"netloc for family {self.family} is {self.netloc} derived from url {self.url}"
        if self.debug:
            print(msg)
        self.scriptPath = o.path + self.scriptPath
        self.checkFamily()
        if withLogin:
            self.login()

    def register_family_file(self, familyName: str, famfile: str):
        """
        register the family file

        Args:
            family(str): the familyName to register
            famfile(str): the path to the family file
        """
        # deprecated code
        # config2.register_family_file(familyName, famfile)
        pywikibot.config.family_files[familyName] = famfile

    def checkFamily(self):
        """
        check if a valid family file exists and if not create it

        watch out for https://stackoverflow.com/questions/76612838/how-to-work-with-custom-wikibase-using-pywikibot
        8.2 changes that might break old family files
        """
        iniFile = WikiUser.iniFilePath(self.wikiUser.wikiId)
        famfile = iniFile.replace(".ini", ".py")
        if not isfile(famfile):
            print("creating family file %s" % famfile)
            template = """# -*- coding: utf-8  -*-
from pywikibot import family

class Family(family.Family):
    name = '%s'
    langs = {
        'en': '%s',
    }
    def scriptpath(self, code):
       return '%s'

    def isPublic(self):
        return %s

    def version(self, code):
        return "%s"  # The MediaWiki version used. Very important in most cases. (contrary to documentation)

    def protocol(self, code):
       return '%s'

    def ignore_certificate_error(self, code):
       return True
"""
            mw_version = self.wikiUser.version.lower().replace("mediawiki ", "")
            ispublic = "False" if self.wikiUser.user is not None else "True"
            code = template % (
                self.family,
                self.netloc,
                self.scriptPath,
                ispublic,
                mw_version,
                self.scheme,
            )
            with open(famfile, "w") as py_file:
                py_file.write(code)
        self.register_family_file(self.family, famfile)
        if self.wikiUser.user:
            pywikibot.config.usernames[self.family]["en"] = self.wikiUser.user
        # config2.authenticate[self.netloc] = (self.user,self.getPassword())
        self.site = pywikibot.Site("en", self.family)

    def login(self):
        if self.wikiUser.user:
            # needs patch as outlined in https://phabricator.wikimedia.org/T248471
            # self.site.login(password=self.wikiUser.getPassword())
            lm = pywikibot.login.ClientLoginManager(
                password=self.wikiUser.getPassword(),
                site=self.site,
                user=self.wikiUser.user,
            )
            lm.login()
        else:
            raise Exception("wikiUser is not set")

    def getWikiMarkup(self, pageTitle):
        """
        get the wiki markup code (text) for the given page Title

        Args:
            pageTitle(str): the title of the page to retrieve

        Returns:
            str: the wiki markup code for the page
        """
        page = self.getPage(pageTitle)
        markup = page.text
        return markup

    def getHtml(self, pageTitle):
        """
        get the HTML code for the given page Title

        Args:
            pageTitle(str): the title of the page to retrieve

        Returns:
            str: the rendered HTML code for the page
        """
        page = self.getPage(pageTitle)
        html = page.get_parsed_page()
        return html

    def getPage(self, pageTitle):
        """get the page with the given title
        Args:
            pageTitle(str): the title of the page to retrieve
        Returns:
            Page: the wikibot3rd page for the given pageTitle
        """
        page = pywikibot.Page(self.site, pageTitle)
        return page

    def savePage(self, pageTitle, pageContent, pageSummary):
        """save a page with the given pageTitle, pageContent and pageSummary"""
        newPage = self.getPage(pageTitle)
        newPage.text = pageContent
        newPage.save(pageSummary)
