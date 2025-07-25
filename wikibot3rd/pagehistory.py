from dataclasses import field
from typing import List, Union, Optional

from basemkit.yamlable import lod_storable
from wikibot3rd.wikiclient import WikiClient


@lod_storable
class PageRevision:
    """
    Represents the metadata of a mediawiki page revision
    """
    revid: int = 0
    parentid: Optional[int] = None
    user: Optional[str] = None
    anon: Optional[str] = None
    userid: Optional[int] = None
    timestamp: Optional[str] = None
    size: Optional[int] = None
    comment: Optional[str] = None

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

@lod_storable
class PageHistory:
    """
    Represents the history of a page
    """
    pageTitle: str
    wikiId: str
    debug: bool = False
    wikiClient: WikiClient = field(init=False)
    page: object = field(init=False)
    revisions: List[PageRevision] = field(init=False)

    def __post_init__(self):
        self.wikiClient = WikiClient.ofWikiId(self.wikiId, debug=self.debug)
        self.page = self.wikiClient.getPage(self.pageTitle)
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
            revision = PageRevision.from_dict(revisionRecord)
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
        self, reverse: bool = False, limitedUserGroup: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Returns the first user in the revision list matching the criteria
        """
        revisions = sorted(self.revisions, key=lambda r: int(getattr(r, "revid", 0)))
        if reverse:
            revisions = list(reversed(revisions))
        for revision in revisions:
            user = getattr(revision, "user", None)
            if user is None:
                continue
            if limitedUserGroup is None or user in limitedUserGroup:
                return user
        return None
