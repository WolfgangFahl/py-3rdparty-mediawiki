"""
Created on 2021-01-23

@author: wf
"""

from lodstorage.query import Query

from tests.basetest import BaseTest
from wikibot3rd.lambda_action import Code, LambdaAction
from wikibot3rd.smw import SMWClient
from wikibot3rd.wikiaction import WikiAction
from wikibot3rd.wikiclient import WikiClient
from wikibot3rd.wikiuser import WikiUser


class TestLambda(BaseTest):
    """
    test lamdba query/action handling
    """

    def setUp(self):
        BaseTest.setUp(self)
        self.echoCode = Code(
            "EchoCode",
            text="""# this is a lambda Action action
# it get's its context from a context dict
rows=context["rows"]
for row in rows:
    print(row)
context["result"]={"message":"%d rows printed" %len(rows)}""",
            lang="python",
        )
        pass

    def getSMW(self, wikiId="cr"):
        smw = None
        wikiclient = None
        wusers = WikiUser.getWikiUsers()
        if wikiId in wusers:
            wuser = wusers[wikiId]
            wikiclient = WikiClient.ofWikiUser(wuser)
            smw = SMWClient(wikiclient.getSite())
        return smw, wikiclient

    def testLambda(self):
        """
        test the lamdba handling
        """
        smw, wikiclient = self.getSMW()
        if smw is not None:
            wikiAction = WikiAction(smw)
            query = Query("test query", query="[[Capital of::+]]", lang="smw")
            lambdaAction = LambdaAction(
                "test smw query", query=query, code=self.echoCode
            )
            context = {"smw": smw}
            lambdaAction.execute(context=context)
            message = lambdaAction.getMessage(context)
            if self.debug:
                print(message)
            self.assertTrue(message is not None)
            self.assertTrue("printed" in message)
        pass
