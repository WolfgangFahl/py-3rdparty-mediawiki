from typing import List, Union

from lodstorage.jsonable import JSONAble

from wikibot3rd.wikiclient import WikiClient


class PageRevision(JSONAble):
    """
    Represents the metadata of a mediawiki page revision
    """

    @classmethod
    def getSamples(cls):
        samples = [
            {
                "revid": 7056,
                "parentid": 0,
                "user": "127.0.0.1",
                "anon": "",
                "userid": 0,
                "timestamp": "2008-10-14T21:23:09Z",
                "size": 6905,
                "comment": "Event created",
            },
            {
                "revid": 8195,
                "parentid": 8194,
                "user": "Wf",
                "timestamp": "2021-11-11T12:50:31Z",
                "size": 910,
                "comment": "",
            },
        ]
        return samples

    def __repr__(self):
        props = ", ".join([f"{k}={str(v)}" for k, v in self.__dict__.items()])
        return f"{self.__class__.__name__}({props})"


class PageHistory:
    """
    Represents the history of a page
    """

    def __init__(self, pageTitle: str, wikiId: str, debug: bool = False):
        """
        Constructor

        Args:
            pageTitle(str): name of the page
            wikiId(str): id of the wiki the page is located
            debug(bool): If True show debug messages
        """
        self.debug = debug
        self.pageTitle = pageTitle
        self.wikiClient = WikiClient.ofWikiId(wikiId, debug=self.debug)
        self.page = self.wikiClient.getPage(pageTitle)
        self.revisions = self._getRevisions()

    def _getRevisions(self) -> List[PageRevision]:
        """
        Get the revisions of the page as PageRevision object

        Returns:
            List of PageRevisions of the page
        """
        revisions = []
        for revisionRecord in self.page.revisions(
            prop="ids|timestamp|user|userid|comment|size"
        ):
            revision = PageRevision()
            revision.fromDict(revisionRecord)
            revisions.append(revision)
        return revisions

    def exists(self) -> bool:
        """
        Checks if the page exists
        Assumption: If the page exists than ot exists at least one revision entry

        Returns:
            True if the page exists otherwise False
        """
        return len(self.revisions) > 0

    def getFirstUser(
        self, reverse: bool = False, limitedUserGroup: List[str] = None
    ) -> Union[str, None]:
        """
        Returns the first user in the revisions

        Args:
            reverse(bool): If False start the search at the oldest entry. Otherwise, search from the newest to the oldest revision
            limitedUserGroup(list): limit the search to the given list. If None all users will be considered.

        Returns:
            str username that matches the search criterion
        """
        revisions = self.revisions
        revisions.sort(key=lambda r: int(getattr(r, "revid", 0)))
        if reverse:
            revisions = reversed(revisions)
        for revision in revisions:
            user = getattr(revision, "user", None)
            if user is None:
                continue
            if limitedUserGroup is None:
                return user
            elif user in limitedUserGroup:
                return user
        return None
