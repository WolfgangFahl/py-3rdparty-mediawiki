import mwclient

from tests.basetest import BaseTest
from wikibot3rd.wikitext import WikiMarkup, WikiSON


class TestWikiSON(BaseTest):
    """
    tests WikiSON
    """

    def test_set(self):
        """
        tests adding new data to wiki markup
        """
        test_params = [
            # (entity_type, data, markup, expected)
            (
                "Person",
                {"Name": "John", "last name": "Doe"},
                "",
                "\n{{Person\n|Name=John\n|last name=Doe\n}}",
            ),
            (
                "Person",
                {"Name": "John", "last name": "Doe"},
                "==Freetext==",
                "==Freetext==\n{{Person\n|Name=John\n|last name=Doe\n}}",
            ),
            (
                "Person",
                {"Name": "John", "last name": "Doe"},
                "{{Person\n|age=42}}",
                "{{Person\n|age=42|Name=John\n|last name=Doe\n}}",
            ),
            (
                "Person",
                {"Name": "John", "last name": "Doe"},
                "{{Person\n|Name=Jane\n}}",
                "{{Person\n|Name=John\n|last name=Doe\n}}",
            ),
            (
                "Person",
                {"Name": "John", "last name": "Doe"},
                "{{Scholar\n|Name=Jane\n}}",
                "{{Scholar\n|Name=Jane\n}}\n{{Person\n|Name=John\n|last name=Doe\n}}",
            ),
            (
                "Person",
                {"Name": "John", "last name": "Doe"},
                "==Person=={{Person\n|age=42}}\n==Details==",
                "==Person=={{Person\n|age=42|Name=John\n|last name=Doe\n}}\n==Details==",
            ),
            (
                "Person",
                {"Name": "John", "last name": None},
                "",
                "\n{{Person\n|Name=John\n}}",
            ),
        ]
        for test_param in test_params:
            with self.subTest(test_param=test_param):
                entity_type, data, markup, expected = test_param
                wikison = WikiSON("test page", markup)
                new_markup = wikison.set(entity_type_name=entity_type, record=data)
                self.assertEqual(expected, new_markup)

    def test_get(self):
        """
        tests getting WikiSON records from a given wiki markup
        """
        test_params = [
            # (entity_type, expected, markup)
            (
                "Person",
                {"Name": "John", "last name": "Doe"},
                "==Person=={{Person\n|Name=John\n|last name=Doe\n}}",
            ),
            (
                "Scholar",
                {"Name": "Decker", "orcid id": "0000-0001-6324-7164"},
                "{{Scholar\n|Name=Decker\n|orcid id=0000-0001-6324-7164\n}}",
            ),
            (
                "Event",
                {"Title": "Wikidata Workshop 2022", "ordinal": "3"},
                "{{Event|Title=Wikidata Workshop 2022|ordinal=3}}",
            ),
            ("Person", None, "{{Scholar\n|Name=John\n|last name=Doe\n}}"),
            ("Person", None, "==Person==\n* Name: Bob"),
        ]
        for test_param in test_params:
            with self.subTest(test_param=test_param):
                entity_type, expected, markup = test_param
                wikison = WikiSON("test page", markup)
                record = wikison.get(entity_type_name=entity_type)
                if isinstance(expected, dict):
                    self.assertDictEqual(expected, record)
                else:
                    self.assertEqual(expected, record)

    def test_get_exceptions(self):
        """
        tests getting WikiSON records in the cases where an exception is thrown
        """
        test_params = [
            # (entity_type, markup)
            ("Person", "{{Person\n|Name=Alice\n}}{{Person\n|Name=Bob\n}}"),
        ]
        for test_param in test_params:
            with self.subTest(test_param=test_param):
                entity_type, markup = test_param
                wikison = WikiSON("test page", markup)
                self.assertRaises(Exception, wikison.get, entity_type)

    def test_issue_111(self):
        """
        test add --template option to wikiquery

        """
        # Create a site object
        site = mwclient.Site("en.wikipedia.org")

        page_title = "John Adams"
        template = "Infobox officeholder"
        # Get the page
        page = site.pages[page_title]

        # Get the markup
        markup = page.text()
        debug = self.debug
        if debug:
            print(markup)
        # Create WikiSON instance
        wikison = WikiSON(page_title, markup)

        # Get the Infobox officeholder template
        infobox_data = wikison.get(template)
        if debug:
            print(infobox_data)
        self.assertTrue(page_title, infobox_data.get("name"))
