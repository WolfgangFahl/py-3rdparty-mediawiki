from typing import Any, Dict, Optional
from urllib.parse import urlparse

from mwclient import Site

from wikibot3rd.wiki import Wiki
from wikibot3rd.wikiuser import WikiUser


class WikiClient(Wiki):
    """
    Access MediaWiki via mwclient library.
    """

    def __init__(
        self, wiki_user: WikiUser, debug: bool = False, smw_enabled: bool = True
    ):
        """
        Initialize the WikiClient with a WikiUser and an optional debug mode.

        Args:
            wiki_user: A WikiUser instance containing login credentials.
            debug: A flag to enable debug mode.
        """
        super(WikiClient, self).__init__(
            wiki_user, debug=debug, smw_enabled=smw_enabled
        )
        self.wiki_user: WikiUser = wiki_user
        # compatibility
        self.wikiUser = self.wiki_user
        self.site: Optional[Site] = None
        self._is_logged_in: bool = False

    def get_site(self) -> Site:
        """
        Get the Site object for the MediaWiki site.

        Returns:
            The Site object representing the MediaWiki site.
        """
        if self.site is None:
            o = urlparse(self.wiki_user.url)
            scheme = o.scheme
            host = o.netloc
            path = o.path + self.wiki_user.scriptPath
            path = f"{path}/"
            self.site = Site(host=host, path=path, scheme=scheme)
        return self.site

    def getSite(self) -> Site:
        """Deprecated: Use get_site instead."""
        return self.get_site()

    def needs_login(self) -> bool:
        """
        Check if login is required for the wiki.

        Returns:
            True if login is required, False otherwise.
        """
        login_needed: bool = False
        site = self.get_site()
        if not site.initialized:
            try:
                self.site.site_init()
                if hasattr("site", "writeapi"):
                    login_needed = not site.writeapi
                else:
                    login_needed = not "writeapi" in site.site
            except Exception as ex:
                if hasattr(ex, "args") and "readapidenied" in ex.args:
                    login_needed = True
                pass

        return login_needed

    def needsLogin(self) -> bool:
        """Deprecated: Use needs_login instead."""
        return self.needs_login()

    def try_login(self) -> Exception:
        """
        Attempt to log in to the MediaWiki site.

        Returns:
            Exception: None if login is successful, Exception otherwise.
        """
        wu = self.wiki_user
        try:
            self.get_site().login(username=wu.user, password=wu.get_password())
            self._is_logged_in = True
            return None
        except Exception as ex:
            self._is_logged_in = False
            return ex

    def login(self) -> bool:
        """
        Attempt to log in to the MediaWiki site.

        Returns:
            True if login is successful, False otherwise.
        """
        ex = self.try_login()
        if ex and self.debug:
            print(f"Login failed: {ex}")
        success = ex is None
        return success

    def get_wiki_markup(self, page_title: str) -> str:
        """
        Get the wiki markup for a given page title.

        Args:
            page_title: The title of the page to retrieve the markup for.

        Returns:
            The wiki markup of the specified page.
        """
        page = self.get_page(page_title)
        markup = page.text()
        return markup

    def getWikiMarkup(self, pageTitle: str) -> str:
        """Deprecated: Use get_wiki_markup instead."""
        return self.get_wiki_markup(pageTitle)

    def get_html(self, page_title: str) -> str:
        """
        Get the HTML content for a given page title.

        Args:
            page_title: The title of the page to retrieve the HTML for.

        Returns:
            The HTML content of the specified page.
        """
        api = self.get_site().api("parse", page=page_title)
        if "parse" not in api:
            raise Exception(f"Could not retrieve HTML for page {page_title}")
        html: str = api["parse"]["text"]["*"]
        return html

    def getHtml(self, pageTitle: str) -> str:
        """Deprecated: Use get_html instead."""
        return self.get_html(pageTitle)

    def get_page(self, page_title: str) -> Any:
        """
        Get the page object for a given title.

        Args:
            page_title: The title of the page to retrieve.

        Returns:
            The page object for the specified title.
        """
        page = self.get_site().pages[page_title]
        return page

    def getPage(self, pageTitle: str) -> Any:
        """Deprecated: Use get_page instead."""
        return self.get_page(pageTitle)

    def save_page(self, page_title: str, page_content: str, page_summary: str) -> None:
        """
        Save a page with given title and content.

        Args:
            page_title: The title of the page.
            page_content: The new content of the page.
            page_summary: A summary of the changes made.
        """
        new_page = self.get_page(page_title)
        new_page.edit(page_content, page_summary)

    def savePage(self, pageTitle: str, pageContent: str, pageSummary: str) -> None:
        """Deprecated: Use save_page instead."""
        self.save_page(pageTitle, pageContent, pageSummary)

    def get_site_statistics(self) -> Dict[str, Any]:
        """
        Fetch site statistics using the MediaWiki API.

        Returns:
            A dictionary containing the site statistics.
        """
        params = {
            "action": "query",
            "meta": "siteinfo",
            "siprop": "statistics",
            "format": "json",
        }
        site = self.get_site()
        data = site.api(**params)
        statistics = data["query"]["statistics"]
        return statistics

    def getSiteStatistics(self) -> Dict[str, Any]:
        """Deprecated: Use get_site_statistics instead."""
        return self.get_site_statistics()

    @staticmethod
    def get_clients() -> Dict[str, "WikiClient"]:
        """
        Get a dictionary of WikiClient instances for all WikiUsers.

        Returns:
            Dict[str, WikiClient]: A dictionary with wiki user IDs as keys and WikiClient instances as values.
        """
        clients: Dict[str, WikiClient] = {}
        for wiki_user in WikiUser.getWikiUsers().values():
            wiki_client = WikiClient(wiki_user)
            clients[wiki_user.wikiId] = wiki_client
        return clients

    @staticmethod
    def getClients() -> Dict[str, "WikiClient"]:
        """Deprecated: Use get_clients instead."""
        return WikiClient.get_clients()

    @staticmethod
    def of_wiki_id(
        wiki_id: str, lenient: bool = True, debug: bool = False
    ) -> "WikiClient":
        """
        Create a WikiClient instance for a specific wiki ID.

        Args:
            wiki_id: The ID of the wiki to create a client for.
            lenient: Whether to be lenient in case of errors.
            debug: Whether to enable debug output.

        Returns:
            WikiClient: A WikiClient instance for the given wiki ID.
        """
        wiki_user = WikiUser.ofWikiId(wiki_id, lenient=lenient)
        wikibot = WikiClient(wiki_user, debug=debug)
        wikibot.is_smw_enabled = wiki_user.is_smw
        return wikibot

    @staticmethod
    def ofWikiId(
        wiki_id: str, lenient: bool = True, debug: bool = False
    ) -> "WikiClient":
        """Deprecated: Use of_wiki_id instead."""
        return WikiClient.of_wiki_id(wiki_id, lenient=lenient, debug=debug)

    @staticmethod
    def of_wiki_user(wiki_user: WikiUser, debug: bool = False) -> "WikiClient":
        """
        Create a WikiClient instance from a WikiUser object.

        Args:
            wiki_user: A WikiUser instance to create a WikiClient for.

        Returns:
            WikiClient: A WikiClient instance for the given WikiUser.
        """
        wikibot = WikiClient(wiki_user, debug=debug)
        wikibot.is_smw_enabled = wiki_user.is_smw
        return wikibot

    @staticmethod
    def ofWikiUser(wiki_user: WikiUser, debug: bool = False) -> "WikiClient":
        """Deprecated: Use of_wiki_user instead."""
        return WikiClient.of_wiki_user(wiki_user, debug=debug)
