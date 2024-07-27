"""
Created on 2023-02-24
  @author: tholzheim
"""

import typing
import warnings

import wikitextparser as wtp
from wikitextparser import Template


class WikiMarkup:
    """
    Provides methods to modify, query and update Templates in wiki markup
    see https://en.wikipedia.org/wiki/Help:Wikitext
    """

    def __init__(self, page_title: str, wiki_markup: str = None, debug: bool = False):
        """

        Args:
            page_title: page title of the wiki_markup file
            wiki_markup: WikiPage content as string. If None tries to init the wiki_markup from source location
        """
        self.page_title = page_title
        self.debug = debug
        self._wiki_markup = wiki_markup
        self._parsed_wiki_markup: typing.Optional[wtp.WikiText] = None

    @property
    def wiki_markup(self) -> str:
        """
        Get wiki markup. If wikimarkup was parsed the parsed markup is converted back to wiki markup

        Returns:
            str
        """
        if self._parsed_wiki_markup is None:
            return self._wiki_markup
        else:
            return str(self._parsed_wiki_markup)

    @wiki_markup.setter
    def wiki_markup(self, wiki_markup: str):
        self._wiki_markup = wiki_markup
        if self._parsed_wiki_markup is not None:
            # update parsed wiki_markup
            self._parsed_wiki_markup = wtp.parse(wiki_markup)

    @property
    def parsed_wiki_markup(self) -> wtp.WikiText:
        """
        Get WikiText. If not already parsed the markup is parsed

        Returns:
            wtp:WikiText
        """
        if self._parsed_wiki_markup is None and self._wiki_markup is not None:
            self._parsed_wiki_markup = wtp.parse(self._wiki_markup)
        return self._parsed_wiki_markup

    @parsed_wiki_markup.setter
    def parsed_wiki_markup(self, parsed_wiki_markup: wtp.WikiText):
        self._parsed_wiki_markup = parsed_wiki_markup

    def _get_templates_by_name(
        self, template_name: str, match: dict = typing.Dict[str, str]
    ) -> typing.List[Template]:
        """
        Returns the templates matching the given name and if additional matches are defined the values of the template
        also have to match these
        Args:
            template_name: name of the template
            match(dict): Additional matching criteria

        Returns:
            list of templates with the given name matching the given criteria
        """
        if match is None:
            match = {}
        if self.parsed_wiki_markup is None or self.parsed_wiki_markup.templates is None:
            # markup has no templates
            return []
        target_template_name = template_name.strip()
        matching_templates = []
        for template in self.parsed_wiki_markup.templates:
            name = template.name.strip()
            if name == target_template_name:
                matches = True
                for key, value in match.items():
                    if not template.has_arg(key, value):
                        matches = False
                if matches:
                    matching_templates.append(template)
        return matching_templates

    @classmethod
    def _get_template_arguments(cls, template: Template) -> typing.Dict[str, str]:
        """
        Get the arguments of the given template
        Args:
            template: template to extract the arguments from

        Returns:
            dict: arguments of the template
        """
        args = dict()
        for arg in template.arguments:
            name = arg.name.strip()
            value = arg.value.strip()
            args[name] = value
        return args

    def add_template(self, template_name: str, data: dict):
        """
        Adds the given data as template with the given name to this wikifile.
        The data is added as new template object to the wikifile.
        Args:
            template_name(str): Name of the template the data should be inserted in
            data(dict): Data that should be saved in form of a template
        """
        template_markup = "{{" + template_name + "\n"
        for key, value in data.items():
            if value is not None:
                template_markup += f"|{key}={value}\n"
        template_markup += "}}"
        template = Template(template_markup)
        self.wiki_markup = f"{self.wiki_markup}\n{template}"

    def update_template(
        self,
        template_name: str,
        args: dict,
        overwrite: bool = False,
        update_all: bool = False,
        match: typing.Optional[typing.Dict[str, str]] = None,
    ):
        """
        Updates the given template the values from the given dict args.
        If force is set to True existing values will be overwritten.
        Args:
            template_name(str): name of the template that should be updated
            args(dict): Dict containing the arguments that should be set. key=argument name, value=argument value
            overwrite(bool): If True existing values will be overwritten
            update_all(bool): If True all matching attributes are updated.
                              Otherwise, only one template is updated if matched multiple an error is raised.
            match(dict): matching criteria for the template.

        Returns:
            Nothing
        """
        if match is None:
            match = {}
        matching_templates = self._get_templates_by_name(template_name, match=match)
        if matching_templates:
            if len(matching_templates) > 1 and not update_all:
                warnings.warn(
                    "More than one template were matched. Either improve the matching criteria or enable update_all",
                    UserWarning,
                )
                pass
            else:
                for template in matching_templates:
                    self._update_arguments(template, args, overwrite)
        else:
            self.add_template(template_name, args)

    @classmethod
    def _update_arguments(cls, template: Template, args: dict, overwrite: bool = False):
        """
        Updates the arguments of the given template with the values of the given dict (args)

        Args:
            template: Template that should be updated
            args(dict): Dict containing the arguments that should be set. key=argument name, value=argument value
            overwrite(bool): If True existing values will be overwritten

        Returns:
            Nothing
        """
        postfix = "\n"
        for key, value in args.items():
            if template.has_arg(key):
                # update argument
                if overwrite:
                    template.del_arg(key)
                    if value is not None:
                        template.set_arg(key, str(value) + postfix)
                else:
                    pass
            else:
                if value is not None:
                    template.set_arg(key, str(value) + postfix, preserve_spacing=False)

    def extract_template(
        self, template_name: str, match: typing.Optional[typing.Dict[str, str]] = None
    ) -> typing.List[typing.Dict[str, str]]:
        """
        Extracts the template data and returns it as dict

        Args:
            template_name: name of the template that should be extracted
            match(dict): Additional matching criteria

        Returns:
            list of dicts: records of the templates that match the given name
        """
        if match is None:
            match = {}
        templates = self._get_templates_by_name(template_name, match=match)
        lod = []
        for template in templates:
            if template is None:
                continue
            records = self._get_template_arguments(template)
            if records:
                lod.append(records)
        return lod

    def __str__(self) -> str:
        return self.wiki_markup


class WikiSON:
    """
    WikiSON Api to edit WikiSON entities
    """

    def __init__(self, page_title: str, wiki_markup: str):
        """
        constructor
        Args:
            page_title: name of the wiki page
            wiki_markup: markup of the wiki page
        """
        self.wiki_markup = WikiMarkup(page_title, wiki_markup)

    def get(self, entity_type_name: str) -> typing.Optional[typing.Dict[str, str]]:
        """
        Get the WikiSON entity by the given name
        Args:
            entity_type_name: name of the WikiSON entity type e.g. Scholar, Event

        Raises:
            Exception: if wiki markup contains more than one WikiSON with the same entity type name

        Returns:
            dict: record of the entity
        """
        records = self.wiki_markup.extract_template(entity_type_name)
        if len(records) > 1:
            raise Exception(
                "More than one WikiSON with the same entity type on one Page"
            )
        if len(records) == 1:
            record = records[0]
        else:
            record = None
        return record

    def set(self, entity_type_name: str, record: dict) -> str:
        """
        Set WikiSON entity with the given type and data
        Args:
            entity_type_name: name of the WikiSON entity type e.g. Scholar, Event
            record: data to add to the WikiSON entity

        Returns:
            str: wiki markup of the page
        """
        self.wiki_markup.update_template(entity_type_name, args=record, overwrite=True)
        return self.wiki_markup.wiki_markup
