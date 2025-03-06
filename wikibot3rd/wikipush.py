"""
Created on 2020-10-29
  @author:     wf
  @copyright:  Wolfgang Fahl. All rights reserved.

"""

import shutup
from tqdm import tqdm

shutup.please()
import datetime

# from difflib import Differ
import difflib
import json
import os
import re
import sys
import traceback
import typing
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from git import Repo
from lodstorage.query import Query
from lodstorage.query_cmd import QueryCmd
from mwclient.image import Image

from wikibot3rd.selector import Selector
from wikibot3rd.smw import SMWClient
from wikibot3rd.version import Version
from wikibot3rd.wikiclient import WikiClient
from wikibot3rd.wikitext import WikiMarkup, WikiSON


class WikiPush(object):
    """
    Push pages from one MediaWiki to another
    """

    differ = None

    def __init__(
        self,
        fromWikiId: str,
        toWikiId: str = None,
        login: bool = False,
        verbose: bool = True,
        debug: bool = False,
    ):
        """
        Constructor

        Args:
            fromWikiId(str): the id of the wiki to push from (source)
            toWikiID(str): the id of the wiki to push to (target)
            login(bool): if True login to source wiki
            verbose(bool): if True print info messages
            debug(bool): if True show debugging messages
        """
        self.verbose = verbose
        self.debug = debug
        self.args = Namespace()
        self.args.template = None
        self.fromWiki = None
        self.toWiki = None

        self.fromWikiId = fromWikiId
        if self.fromWikiId is not None:
            self.fromWiki = WikiClient.ofWikiId(fromWikiId, debug=self.debug)
        self.toWikiId = toWikiId
        if self.toWikiId is not None:
            self.toWiki = WikiClient.ofWikiId(toWikiId, debug=self.debug)
        if login and self.fromWikiId is not None:
            if not self.fromWiki.login():
                msg = f"can't login to source Wiki {fromWikiId}"
                ex = Exception(msg)
                self.show_exception(ex)
                raise (ex)
        if self.toWiki is not None:
            if not self.toWiki.login():
                msg = f"can't login to target Wiki {toWikiId}"
                ex = Exception(msg)
                self.show_exception(ex)
                raise (ex)

    def log(self, msg: str, end="\n"):
        """
        show the given message if verbose is on

        Args:
            msg(str): the message to display
        """
        if self.verbose:
            print(msg, end=end)

    def extract_template_records(self, pageRecords, template: str) -> list:
        """
        Extract template records from the given pageRecords using batch page retrieval.

        Args:
            pageRecords (dict): Dictionary with page titles as keys
            template (str): Name of the template to extract (e.g., "Infobox officeholder")

        Returns:
            list[dict]: List of template records, where each record is a dictionary
                       containing the template parameters. Returns None for pages
                       where the template is not found.

        Example:
            >>> pageRecords = {"John Adams": {}, "Thomas Jefferson": {}}
            >>> records = extract_template_records(pageRecords, "Infobox officeholder")
        """
        dod = {}
        page_titles = list(pageRecords.keys())
        # Get multiple pages at once
        site = self.fromWiki.get_site()
        # Process each page
        for page_title in tqdm(page_titles, disable=not self.args.showProgress):
            try:
                page = site.pages[page_title]
                markup = page.text()
                wiki_markup = WikiMarkup(page.name, markup)
                records = wiki_markup.extract_template(template)
                for i, record in enumerate(records):
                    if record is not None:
                        key = f"{page_title}/{i}" if i > 0 else page_title
                        dod[key] = record
            except Exception as ex:
                print(f"❌ {page_title}: {str(ex)}", file=sys.stderr)
                pass
        return dod

    def formatQueryResult(
        self,
        askQuery,
        wiki=None,
        limit=None,
        showProgress=False,
        queryDivision=1,
        outputFormat="lod",
        entityName="data",
        title: str = None,
    ):
        """
        format the query result for the given askQuery.
        Args:
            askQuery(string): Semantic Media Wiki in line query https://www.semantic-mediawiki.org/wiki/Help:Inline_queries
            wiki(wikibot3rd): the wiki to query - use fromWiki if not specified
            limit(int): the limit for the query (optional)
            showProgress(bool): true if progress of the query retrieval should be indicated (default: one dot per 50 records ...)
            queryDivision(int): Defines the number of subintervals the query is divided into (must be greater equal 1)
            outputFormat(str): output format of the query results - default format is lod
            entityName(str): the name of the entity
            title(str): the title of the query (if any)
        Returns:
            Query results in the requested outputFormat as string.
            If the requested outputFormat is not supported None is returned.
        """
        pageRecords = self.queryPages(
            askQuery, wiki, limit, showProgress, queryDivision
        )
        if self.args.template:
            pageRecords = self.extract_template_records(
                pageRecords, template=self.args.template
            )
            pass
        outputFormat = outputFormat.lower()
        if outputFormat == "csv":
            return self.convertToCSV(pageRecords)
        elif outputFormat == "json":
            res = []
            for page in pageRecords.values():
                res.append(page)
            res_json = json.dumps({entityName: res}, default=str, indent=3)
            return res_json
        elif outputFormat == "lod":
            return [pageRecord for pageRecord in pageRecords.values()]
        else:
            if title is None:
                title = entityName
            query = Query(name=entityName, query=askQuery, title=title)
            qlod = [pageRecord for pageRecord in pageRecords.values()]
            doc = query.documentQueryResult(
                qlod, limit, tablefmt=outputFormat, withSourceCode=False
            )
            return doc
            # if self.debug:
            #    print(f"Format {outputFormat} is not supported.")

    def convertToCSV(self, pageRecords, separator=";"):
        """
        Converts the given pageRecords into a str in csv format
        ToDO: Currently does not support escaping of the separator and escaping of quotes
        Args:
            pageRecords: dict of dicts containing the printouts
            separator(char):
        Returns: str
        """
        res = ""
        printedHeaders = False
        for pageRecord in pageRecords.values():
            if not printedHeaders:
                for key in pageRecord.keys():
                    res = f"{res}{key}{separator}"
                res = f"{res[:-1]}\n"
                printedHeaders = True
            for printouts in pageRecord.values():
                res = f"{res}{printouts}{separator}"
            res = f"{res[:-1]}\n"  # remove last separator and end line
        return res

    def queryPages(
        self, askQuery: str, wiki=None, limit=None, showProgress=False, queryDivision=1
    ) -> dict:
        """
        query the given wiki for pagerecords matching the given askQuery

        Args:
            askQuery (str): Semantic Media Wiki in line query https://www.semantic-mediawiki.org/wiki/Help:Inline_queries
            wiki (wikibot3rd): the wiki to query - use fromWiki if not specified
            limit (int): the limit for the query (optional)
            showProgress (bool): true if progress of the query retrieval should be indicated (default: one dot per 50 records ...)
            queryDivision (int): Defines the number of subintervals the query is divided into (must be greater equal 1)
        Returns:
            list: a list of pageRecords matching the given askQuery
        """
        if wiki is None:
            wiki = self.fromWiki
        # no wiki no pages e.g. if wikirestore is used without a -s option
        if wiki is None:
            pageRecords = []

        if wiki.is_smw_enabled:
            smwClient = SMWClient(
                wiki.getSite(),
                showProgress=showProgress,
                queryDivision=queryDivision,
                debug=self.debug,
            )
            pageRecords = smwClient.query(askQuery, limit=limit)
        else:
            pageRecords = self.query_via_mw_api(askQuery, wiki, limit=limit)
        return pageRecords

    def extract_category_and_mainlabel(
        self,
        askQuery: str,
        category_labels: List[str] = [
            "Category",
            "Kategorie",
            "Catégorie",
            "Categoría",
        ],
    ) -> Optional[Tuple[str, Optional[str]]]:
        """
        Extracts the category pattern and mainlabel from a MediaWiki query, supporting multiple language labels.

        Args:
            askQuery (str): The query string to be processed.
            category_labels (List[str], optional): A list of category labels in different languages
                                                   (default: ['Category', 'Kategorie', 'Catégorie', 'Categoría']).

        Returns:
            Optional[Tuple[str, Optional[str]]]: A tuple containing the category pattern and
            the mainlabel if present. Returns None if the query does not match a category pattern.
        """
        # Join the list of category labels into a regex pattern
        labels_pattern = "|".join(re.escape(label) for label in category_labels)

        # Regex to match category queries in specified languages and optionally a mainlabel
        pattern = rf"\[\[\s*(?:{labels_pattern})\s*:\s*([^\]]+)\s*\]\](?:\s*\|\s*mainlabel\s*=\s*([^\|]+))?"
        match = re.match(pattern, askQuery.strip())

        if match:
            category = match.group(1).strip()  # Extract the category pattern
            mainlabel = (
                match.group(2).strip() if match.group(2) else None
            )  # Extract the mainlabel if present
            return category, mainlabel

        return None

    def query_via_mw_api(self, askQuery: str, wiki, limit: int = None) -> Dict:
        # Handle non-SMW wiki (assuming category query)
        category, _ = self.extract_category_and_mainlabel(askQuery)
        if not category:
            err_msg = f"non SMW wiki has limited query support ([[Category:+]] and [[Category:someCategory only]] your query: {askQuery} is not supported"
            raise ValueError(err_msg)
        site = wiki.getSite()
        # result dict
        page_records = {}
        if category == "+":
            q_page_records = site.allcategories()
        else:
            q_page_records = site.categories[category]
        for page in q_page_records:
            if limit and len(page_records) >= limit:
                break
            page_records[page.name] = {"pageTitle": page.name}
        return page_records

    def query(
        self,
        askQuery,
        wiki=None,
        pageField=None,
        limit=None,
        showProgress=False,
        queryDivision=1,
    ):
        """
        query the given wiki for pages matching the given askQuery

        Args:
            askQuery(string): Semantic Media Wiki in line query https://www.semantic-mediawiki.org/wiki/Help:Inline_queries
            wiki(wikibot3rd): the wiki to query - use fromWiki if not specified
            pageField(string): the field to select the pageTitle from
            limit(int): the limit for the query (optional)
            showProgress(bool): true if progress of the query retrieval should be indicated (default: one dot per 50 records ...)
        Returns:
            list: a list of pageTitles matching the given askQuery
        """
        pageRecords = self.queryPages(
            askQuery, wiki, limit, showProgress, queryDivision
        )
        if pageField is None:
            return pageRecords.keys()
        # use a Dict to remove duplicates
        pagesDict = {}
        for pageRecord in pageRecords.values():
            if pageField in pageRecord:
                pagesDict[pageRecord[pageField]] = True
        return list(pagesDict.keys())

    def nuke(self, pageTitles, force=False):
        """
        delete the pages with the given page Titles

        Args:
            pageTitles(list): a list of page titles to be transfered from the formWiki to the toWiki
            force(bool): True if pages should be actually deleted - dry run only listing pages is default
        """
        total = len(pageTitles)
        self.log(
            "deleting %d pages in %s (%s)"
            % (total, self.toWikiId, "forced" if force else "dry run")
        )
        for i, pageTitle in enumerate(pageTitles):
            try:
                self.log(
                    "%d/%d (%4.0f%%): deleting %s ..."
                    % (i + 1, total, (i + 1) / total * 100, pageTitle),
                    end="",
                )
                pageToBeDeleted = self.toWiki.getPage(pageTitle)
                if not force:
                    self.log("👍" if pageToBeDeleted.exists else "👎")
                else:
                    pageToBeDeleted.delete("deleted by wiknuke")
                    self.log("✅")
            except Exception as ex:
                self.show_exception(ex)

    @staticmethod
    def getDiff(text: str, newText: str, n: int = 1, forHuman: bool = True) -> str:
        """
        Compare the two given strings and return the differences
        Args:
            text: old text to compare the new text to
            newText: new text
            n: The number of context lines
            forHuman: If True update the diff string to be better human-readable

        Returns:
            str: difference string
        """
        # if WikiPush.differ is None:
        #    WikiPush.differ=Differ()
        # https://docs.python.org/3/library/difflib.html
        #  difflib.unified_diff(a, b, fromfile='', tofile='', fromfiledate='', tofiledate='', n=3, lineterm='\n')¶
        # diffs=WikiPush.differ.compare(,)
        textLines = text.split("\n")
        newTextLines = newText.split("\n")
        diffs = difflib.unified_diff(textLines, newTextLines, n=n)
        if forHuman:
            hdiffs = []
            for line in diffs:
                unwantedItems = ["@@", "---", "+++"]
                keep = True
                for unwanted in unwantedItems:
                    if unwanted in line:
                        keep = False
                if keep:
                    hdiffs.append(line)
        else:
            hdiffs = diffs
        diffStr = "\n".join(hdiffs)
        return diffStr

    @staticmethod
    def getModify(
        search: str, replace: str, debug: bool = False
    ) -> typing.Callable[[str], str]:
        """
        get the modification function

        Args:
            search(str): the search string
            replace(str): the replace string
            debug(bool): if debug show

        Returns:
            String modify function that takes as input the string, applies the search and replace action
             and returns the modified string
        """
        if debug:
            print(f"search regex: {search}")
            print(f"replace regex: {replace}")
        searchRegex = r"%s" % search
        replaceRegex = r"%s" % replace
        modify = lambda text: re.sub(searchRegex, replaceRegex, text)
        return modify

    def edit_page_content(
        self,
        page_title: str,
        new_text: str = None,
        summary="edited by wikiedit",
        modify: typing.Callable[[str], str] = None,
        force: bool = False,
        context: int = 1,
    ) -> str:
        """
        Edit the content of a single page.

        Args:
        page_title (str): The title of the page to be edited
        new_text (str): the new text for the page
        summary (str): the summary / comment for the editing
        modify (Callable[[str], str]): Function to modify the page content
        force (bool): If True, actually edit the page; if False, perform a dry run
        context (int): The number of context lines for diff

        Returns:
        str: Status of the edit operation
        """
        page_to_edit = self.toWiki.getPage(page_title)
        if not force and not page_to_edit.exists:
            return "👎"

        text = page_to_edit.text()
        if not new_text:
            new_text = modify(text)

        if new_text == text:
            return "↔"

        if force:
            page_to_edit.edit(new_text, summary)
            return "✅"
        else:
            diff_str = self.getDiff(text, new_text, n=context)
            return f"👍{diff_str}"

    def edit(
        self,
        page_titles: typing.List[str],
        modify: typing.Callable[[str], str] = None,
        context: int = 1,
        force: bool = False,
    ):
        """
        Edit the pages with the given page titles

        Args:
        page_titles (list): a list of page titles to be transferred from the formWiki to the toWiki
        modify: String modify function that takes as input the string and returns the modified string
        context: The number of context lines
        force (bool): True if pages should be actually edited - dry run only listing pages is default
        """
        if modify is None:
            raise Exception("wikipush edit needs a modify function!")

        total = len(page_titles)
        self.log(
            f"editing {total} pages in {self.toWikiId} ({'forced' if force else 'dry run'})"
        )

        for i, page_title in enumerate(page_titles):
            try:
                self.log(
                    f"{i + 1}/{total} ({(i + 1) / total * 100:4.0f}%): editing {page_title} ...",
                    end="",
                )

                result = self.edit_page_content(page_title, modify=modify, force=force, context=context)
                self.log(result)

            except Exception as ex:
                self.show_exception(ex)

    def edit_wikison(
        self,
        page_titles: typing.List[str],
        entity_type_name: str,
        property_name: str,
        value: typing.Any,
        force: bool = False,
    ):
        """
        Edit the WikiSON for on the given pages
        Args:
            page_titles: a list of page titles to be edited
            entity_type_name: name of the WikiSON entity type
            property_name: name of the property to edit
            value: value to set. If None property is deleted from the WikiSON
            force: If False only print the changes. Otherwise, apply the changes
        """
        total = len(page_titles)
        self.log(
            f"""editing {total} pages in {self.toWikiId} ({"forced" if force else "dry run"})"""
        )
        for i, page_title in enumerate(page_titles, 1):
            try:
                self.log(
                    f"{i}/{total} ({i/total*100:.2f}%): editing {page_title} ...",
                    end="",
                )
                page_to_be_edited = self.toWiki.getPage(page_title)
                if not force and not page_to_be_edited.exists:
                    self.log("👎")
                else:
                    comment = "edited by wikiedit"
                    markup = page_to_be_edited.text()
                    wikison = WikiSON(page_title, markup)
                    new_markup = wikison.set(
                        entity_type_name=entity_type_name, record={property_name: value}
                    )
                    if new_markup != markup:
                        if force:
                            page_to_be_edited.edit(new_markup, comment)
                            self.log("✅")
                        else:
                            diff_str = self.getDiff(markup, new_markup, n=3)
                            self.log(f"👍{diff_str}")
                    else:
                        self.log("↔")
            except Exception as ex:
                self.show_exception(ex)

    def upload(self, files, force=False):
        """
        push the given files
        Args:
            files(list): a list of filenames to be transfered to the toWiki
            force(bool): True if images should be overwritten if they exist
        """
        total = len(files)
        self.log("uploading %d files to %s" % (total, self.toWikiId))
        for i, file in enumerate(files):
            try:
                self.log(
                    "%d/%d (%4.0f%%): uploading %s ..."
                    % (i + 1, total, (i + 1) / total * 100, file),
                    end="",
                )
                description = "uploaded by wikiupload"
                filename = os.path.basename(file)
                self.uploadImage(file, filename, description, force)
                self.log("✅")
            except Exception as ex:
                self.show_exception(ex)

    def backup(self, pageTitles, backupPath=None, git=False, withImages=False):
        """
        backup the given page titles
        Args:
            pageTitles(list): a list of page titles to be downloaded from the fromWiki
            git(bool): True if git should be used as a version control system
            withImages(bool): True if the image on a page should also be copied
        """
        if backupPath is None:
            backupPath = self.getHomePath("wikibackup/%s" % self.fromWikiId)
        imageBackupPath = "%s/images" % backupPath
        total = len(pageTitles)
        self.log(
            "downloading %d pages from %s to %s" % (total, self.fromWikiId, backupPath)
        )
        for i, pageTitle in enumerate(pageTitles):
            try:
                self.log(
                    "%d/%d (%4.0f%%): downloading %s ..."
                    % (i + 1, total, (i + 1) / total * 100, pageTitle),
                    end="",
                )
                page = self.fromWiki.getPage(pageTitle)
                wikiFilePath = "%s/%s.wiki" % (backupPath, pageTitle)
                self.ensureParentDirectoryExists(wikiFilePath)
                with open(wikiFilePath, "w") as wikiFile:
                    wikiFile.write(page.text())
                self.log("✅")
                if isinstance(page, Image):
                    self.backupImages([page], imageBackupPath)
                if withImages:
                    self.backupImages(page.images(), imageBackupPath)

            except Exception as ex:
                self.show_exception(ex)
        if git:
            gitPath = "%s/.git" % backupPath
            if not os.path.isdir(gitPath):
                self.log("initializing git repository ...")
                repo = Repo.init(backupPath)
            else:
                repo = Repo(backupPath)
            self.log("committing to git repository")
            repo.git.add(all=True)
            timestamp = datetime.datetime.now().isoformat()
            repo.index.commit("auto commit by wikibackup at %s" % timestamp)

    def backupImages(self, imageList: list, imageBackupPath: str):
        """
        backup the images in the givne imageList

        Args:
            imageList(list): the list of images
            imageBackupPath(str): the path to the backup directory
        """
        for image in imageList:
            try:
                imagePath, filename = self.downloadImage(image, imageBackupPath)
            except Exception as ex:
                self.handleException(ex)

    def work(
        self,
        pageTitles: list,
        activity: str = "copying",
        comment: str = "pushed",
        force: bool = False,
        ignore: bool = False,
        withImages: bool = False,
    ) -> list:
        """
        work on the given page titles

        Args:
            pageTitles(list): a list of page titles to be transfered from the formWiki to the toWiki
            activity(str): the activity to perform
            comment(str): the comment to display
            force(bool): True if pages should be overwritten if they exist
            ignore(bool): True if warning for images should be ignored (e.g if they exist)
            withImages(bool): True if the image on a page should also be copied
        Returns:
            list: a list of pageTitles for which the activity failed
        """
        failed = []
        total = len(pageTitles)
        self.log(f"{activity} {total} pages from {self.fromWikiId} to {self.toWikiId}")
        for i, pageTitle in enumerate(pageTitles):
            try:
                percent = (i + 1) / total * 100
                self.log(
                    f"{i+1}/{total} ({percent:4.0f}%): {activity} ... {pageTitle}",
                    end="",
                )
                page = self.fromWiki.getPage(pageTitle)
                if page.exists:
                    # is this an image?
                    if isinstance(page, Image):
                        self.pushImages([page], ignore=ignore)
                    else:
                        newPage = self.toWiki.getPage(pageTitle)
                        if not newPage.exists or force:
                            try:
                                newPage.edit(page.text(), comment)
                                self.log("✅")
                                pageOk = True
                            except Exception as ex:
                                pageOk = self.handleException(ex, ignore)
                                if not pageOk:
                                    failed.append(pageTitle)
                            if withImages and pageOk:
                                self.pushImages(page.images(), ignore=ignore)
                        else:
                            self.log("👎")
                else:
                    self.log("❌")
                    failed.append(pageTitle)
            except Exception as ex:
                self.show_exception(ex)
                failed.append(pageTitle)
        return failed

    def push(self, pageTitles, force=False, ignore=False, withImages=False) -> list:
        """
        push the given page titles

        Args:
            pageTitles(list): a list of page titles to be transfered from the formWiki to the toWiki
            force(bool): True if pages should be overwritten if they exist
            ignore(bool): True if warning for images should be ignored (e.g if they exist)
            withImages(bool): True if the image on a page should also be copied
        Returns:
            list: a list of pageTitles for which the activity failed
        """
        comment = f"pushed from {self.fromWikiId} by wikipush"
        return self.work(
            pageTitles,
            activity="copying",
            comment=comment,
            force=force,
            ignore=ignore,
            withImages=withImages,
        )

    def ensureParentDirectoryExists(self, filePath: str):
        """
        for pages that have a "/" in the name make sure that the parent Directory exists

        Args:
            filePath(str): the filePath to check
        """
        directory = os.path.dirname(filePath)
        self.ensureDirectoryExists(directory)

    def ensureDirectoryExists(self, directory: str):
        """
        make sure the given directory exists

        Args:
            directory(str): the directory to check for existence
        """
        Path(directory).mkdir(parents=True, exist_ok=True)

    def getHomePath(self, localPath):
        """
        get the given home path
        """
        homePath = f"{Path.home()}/{localPath}"
        self.ensureDirectoryExists(homePath)
        return homePath

    def getDownloadPath(self):
        """
        get the download path
        """
        return self.getHomePath("Downloads/mediawiki")

    def pushImages(self, imageList, delim="", ignore=False):
        """
        push the images in the given image List

        Args:
            imageList(list): a list of images to be pushed
            ignore(bool): True to upload despite any warnings.
        """
        for image in imageList:
            try:
                self.log("%scopying image %s ..." % (delim, image.name), end="")
                imagePath, filename = self.downloadImage(image)
                description = image.imageinfo["comment"]
                try:
                    self.uploadImage(imagePath, filename, description, ignore)
                    self.log("✅")
                except Exception as ex:
                    self.handleAPIWarnings(ex.args[0], ignoreExists=ignore)
                    if self.debug:
                        self.show_exception(ex)
                if self.debug:
                    print(image.imageinfo)
            except Exception as ex:
                self.handleException(ex, ignore)

    def show_exception(self, ex: Exception):
        """
        Show the given exception and, if debug mode is on, show the traceback.
        """
        msg = f"❌: {str(ex)}"
        if self.debug:
            # Append the formatted traceback to the message
            msg += "\n" + traceback.format_exc()

        self.log(msg)

    def handleException(self, ex, ignoreExists=False):
        """
        handle the given exception and ignore it if it includes "exists" and ignoreExists is True

        Args:
            ex(Exception): the exception to handle
            ignoreExists(bool): True if "exists" should be ignored

        Returns:
            bool: True if the exception was handled as ok False if it was logged as an error
        """
        msg = str(ex)
        return self.handleWarning(msg, marker="❌", ignoreExists=ignoreExists)

    def handleAPIWarnings(self, warnings, ignoreExists=False):
        """
        handle API Warnings

        Args:
            warnings(list): a list of API warnings
            ignoreExists(bool): ignore messages that warn about existing content

        Returns:
            bool: True if the exception was handled as ok False if it was logged as an error
        """
        msg = ""
        if warnings:
            if isinstance(warnings, str):
                msg = warnings
            else:
                for warning in warnings:
                    msg += "%s\n" % str(warning)
        return self.handleWarning(msg, ignoreExists=ignoreExists)

    def handleWarning(self, msg, marker="⚠️", ignoreExists=False):
        """
        handle the given warning and ignore it if it includes "exists" and ignoreExists is True

        Args:
            msg(string): the warning to handle
            marker(string): the marker to use for the message
            ignoreExists(bool): True if "exists" should be ignored

        Returns:
            bool: True if the exception was handled as ok False if it was logged as an error
        """
        # print ("handling warning %s with ignoreExists=%r" % (msg,ignoreExists))
        if ignoreExists and "exists" in msg:
            # shorten exact duplicate message
            if "exact duplicate" in msg:
                msg = "exact duplicate"
            marker = "👀"
        if not ignoreExists and "exists" in msg:
            msg = (
                "file exists (to overwrite existing files enable the ignore parameter)"
            )
        self.log("%s:%s" % (marker, msg))
        return marker == "👀"

    def downloadImage(self, image, downloadPath=None):
        """
        download the given image

        Args:
            image(image): the image to download
            downloadPath(str): the path to download to if None getDownloadPath will be used
        """
        original_filename = image.name
        prefixes = ["File", "Datei", "Fichier", "Archivo", "Файл", "文件", "ファイル"]
        for prefix in prefixes:
            if original_filename.startswith(f"{prefix}:"):
                filename = original_filename.replace(f"{prefix}:", "")
                break
        else:
            filename = original_filename  # Fallback in case no prefix matches

        if downloadPath is None:
            downloadPath = self.getDownloadPath()
        imagePath = "%s/%s" % (downloadPath, filename)
        self.ensureParentDirectoryExists(imagePath)
        with open(imagePath, "wb") as imageFile:
            image.download(imageFile)
        return imagePath, filename

    def uploadImage(self, imagePath, filename, description, ignoreExists=False):
        """
        upload an image

        Args:
            imagePath(str): the path to the image
            filename(str): the filename to use
            description(str): the description to use
            ignoreExists(bool): True if it should be ignored if the image exists
        """
        with open(imagePath, "rb") as imageFile:
            warnings = None
            response = self.toWiki.site.upload(
                imageFile, filename, description, ignoreExists
            )
            if "warnings" in response:
                warnings = response["warnings"]
            if "upload" in response and "warnings" in response["upload"]:
                warningsDict = response["upload"]["warnings"]
                warnings = []
                for item in warningsDict.items():
                    warnings.append(str(item))
            if warnings:
                raise Exception(warnings)

    def restore(self, pageTitles=None, backupPath=None, listFile=None, stdIn=False):
        """
        restore given page titles from local backup
        If no page titles are given the whole backup is restored.

        Args:
            pageTitles(list): a list of pageTitles to be restored to toWiki. If None -> full restore of backup
            backupPath(str): path to backup location
            listFile:
            stdIn:
        """
        if stdIn:
            backupPath = os.path.dirname(pageTitles[0].strip())
            pageTitlesfix = []
            for i in pageTitles:
                pageTitlesfix.append(os.path.basename(i.strip().replace(".wiki", "")))
            pageTitles = pageTitlesfix
        elif listFile is not None:
            f = open(listFile, "r")
            allx = f.readlines()
            pageTitles = []
            for i in allx:
                pageTitles.append(os.path.basename(i.strip()).replace(".wiki", ""))
        else:
            if backupPath is None:
                backupPath = self.getHomePath(f"wikibackup/{self.toWikiId}")
            if pageTitles is None:
                pageTitles = []
                for path, subdirs, files in os.walk(backupPath):
                    for name in files:
                        filename = os.path.join(path, name)[len(backupPath) + 1 :]
                        if filename.endswith(".wiki"):
                            pageTitles.append(filename[: -len(".wiki")])
        total = len(pageTitles)
        self.log(
            "restoring %d pages from %s to %s" % (total, backupPath, self.toWikiId)
        )
        for i, pageTitle in enumerate(pageTitles):
            try:
                self.log(
                    "%d/%d (%4.0f%%): restore %s ..."
                    % (i + 1, total, (i + 1) / total * 100, pageTitle),
                    end="",
                )
                wikiFilePath = f"{backupPath}/{pageTitle}.wiki"
                with open(wikiFilePath, mode="r") as wikiFile:
                    page_content = wikiFile.read()
                    page = self.toWiki.getPage(pageTitle)
                    page.edit(
                        page_content,
                        f"modified through wikirestore by {self.toWiki.wikiUser.user}",
                    )
                self.log("✅")
            except Exception as ex:
                self.show_exception(ex)


__version__ = Version.version
__date__ = Version.date
__updated__ = Version.updated


def mainNuke(argv=None):
    main(argv, mode="wikinuke")


def mainEdit(argv=None):
    main(argv, mode="wikiedit")


def mainPush(argv=None):
    main(argv, mode="wikipush")


def mainQuery(argv=None):
    main(argv, mode="wikiquery")


def mainUpload(argv=None):
    main(argv, mode="wikiupload")


def mainBackup(argv=None):
    main(argv, mode="wikibackup")


def mainRestore(argv=None):
    main(argv, mode="wikirestore")


def main(argv=None, mode="wikipush"):  # IGNORE:C0111
    """main program."""

    if argv is None:
        argv = sys.argv[1:]

    program_name = mode
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = "%%(prog)s %s (%s)" % (
        program_version,
        program_build_date,
    )
    program_shortdesc = mode
    user_name = "Wolfgang Fahl"

    program_license = """%s

  Created by %s on %s.
  Copyright 2020-2025 Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

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
            "-V", "--version", action="version", version=program_version_message
        )
        parser.add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="store_true",
            help="set debug [default: %(default)s]",
        )
        if mode == "wikipush":
            parser.add_argument(
                "-l",
                "--login",
                dest="login",
                action="store_true",
                help="login to source wiki for access permission",
            )
            parser.add_argument(
                "-s", "--source", dest="source", help="source wiki id", required=True
            )
            parser.add_argument(
                "-f",
                "--force",
                dest="force",
                action="store_true",
                help="force to overwrite existing pages",
            )
            parser.add_argument(
                "-i",
                "--ignore",
                dest="ignore",
                action="store_true",
                help="ignore upload warnings e.g. duplicate images",
            )
            parser.add_argument(
                "-wi",
                "--withImages",
                dest="withImages",
                action="store_true",
                help="copy images on the given pages",
            )
        elif mode == "wikibackup":
            parser.add_argument(
                "-g",
                "--git",
                dest="git",
                action="store_true",
                help="use git for version control",
            )
            parser.add_argument(
                "-l",
                "--login",
                dest="login",
                action="store_true",
                help="login to source wiki for access permission",
            )
            parser.add_argument(
                "-s", "--source", dest="source", help="source wiki id", required=True
            )
            parser.add_argument(
                "-wi",
                "--withImages",
                dest="withImages",
                action="store_true",
                help="copy images on the given pages",
            )
            parser.add_argument(
                "--backupPath",
                dest="backupPath",
                help="path where the backup should be stored",
                required=False,
            )
        elif mode == "wikinuke":
            parser.add_argument(
                "-f",
                "--force",
                dest="force",
                action="store_true",
                help="force to delete pages - default is 'dry' run only listing pages",
            )
        elif mode == "wikiedit":
            parser.add_argument(
                "--search", dest="search", help="search pattern", required=False
            )
            parser.add_argument(
                "--replace", dest="replace", help="replace pattern", required=False
            )
            parser.add_argument(
                "--context",
                dest="context",
                type=int,
                help="number of context lines to show in dry run diff display",
                default=1,
            )
            parser.add_argument(
                "-f",
                "--force",
                dest="force",
                action="store_true",
                help="force to edit pages - default is 'dry' run only listing pages",
            )
            parser.add_argument(
                "--template",
                dest="template",
                help="Name of the template to edit",
                required=False,
            )
            parser.add_argument(
                "--property",
                dest="property",
                help="Name of the property in the template to edit",
                required=False,
            )
            parser.add_argument(
                "--value",
                dest="value",
                help="Value of the Property. If not set but property name is given the property is removed from the template",
                required=False,
            )
        elif mode == "wikiquery":
            parser.add_argument(
                "-l",
                "--login",
                dest="login",
                action="store_true",
                help="login to source wiki for access permission",
            )
            parser.add_argument(
                "-s", "--source", dest="source", help="source wiki id", required=True
            )
            parser.add_argument("-o", "--output", help="output file path")
            parser.add_argument(
                "--format",
                dest="format",
                default="json",
                help="format to use for query result csv,json,lod or any of the tablefmt options of https://pypi.org/project/tabulate/",
            )
            parser.add_argument(
                "--entityName",
                dest="entityName",
                default="data",
                help="name of the entities that are queried - only needed for some output formats - default is 'data'",
            )
            parser.add_argument(
                "--template",
                help="name of template to extract the data from - the query needs to have a pagetitle mainlabel and retrieve pages",
            )
        elif mode == "wikiupload":
            parser.add_argument(
                "--files", nargs="+", help="list of files to be uploaded", required=True
            )
            parser.add_argument(
                "-f",
                "--force",
                dest="force",
                action="store_true",
                help="force to (re)upload existing files - default is false",
            )
            pass
        elif mode == "wikirestore":
            parser.add_argument(
                "--listFile",
                dest="listFile",
                help="List of pages to restore",
                required=False,
            )
            parser.add_argument(
                "--backupPath",
                dest="backupPath",
                help="path the backup is stored",
                required=False,
            )
            parser.add_argument(
                "-s", "--source", dest="source", help="source wiki id", required=False
            )
            parser.add_argument(
                "-l",
                "--login",
                dest="login",
                action="store_true",
                help="login to source wiki for access permission",
            )
            parser.add_argument(
                "-stdinp",
                dest="stdinp",
                action="store_true",
                help="Use the input from STD IN using pipes",
            )
        if mode in [
            "wikipush",
            "wikiedit",
            "wikinuke",
            "wikibackup",
            "wikiquery",
            "wikirestore",
        ]:
            QueryCmd.add_args(parser=parser)
            parser.add_argument(
                "--progress",
                dest="showProgress",
                action="store_true",
                help="shows progress for query",
            )
            parser.add_argument(
                "-pf",
                "--pageField",
                dest="pageField",
                help="query result field which contains page",
            )
            parser.add_argument(
                "-p",
                "--pages",
                nargs="+",
                help="list of page Titles to be pushed",
                required=False,
            )
            parser.add_argument(
                "-ui",
                "--withGUI",
                dest="ui",
                help="Pop up GUI for selection",
                action="store_true",
                required=False,
            )
            parser.add_argument(
                "-qd",
                "--queryDivision",
                default=1,
                dest="queryDivision",
                type=int,
                help="Divide the query into equidistant subintervals to limit the result size of the individual queries",
                required=False,
            )
        if mode in ["wikiquery"]:
            parser.add_argument("--title", help="the title for the query")
        if not mode in ["wikibackup", "wikiquery"]:
            parser.add_argument(
                "-t", "--target", dest="target", help="target wiki id", required=True
            )
        # Process arguments
        args = parser.parse_args(argv)
        if hasattr(args, "queryDivision"):
            if args.queryDivision < 1:
                raise ValueError("queryDivision argument must be greater equal 1")

        if mode == "wikipush":
            wikipush = WikiPush(
                args.source, args.target, login=args.login, debug=args.debug
            )
            queryWiki = wikipush.fromWiki
        elif mode == "wikibackup":
            wikipush = WikiPush(args.source, None, login=args.login, debug=args.debug)
            queryWiki = wikipush.fromWiki
        elif mode == "wikiquery":
            wikipush = WikiPush(args.source, None, login=args.login, debug=args.debug)
            queryWiki = wikipush.fromWiki
        elif mode == "wikiupload":
            wikipush = WikiPush(None, args.target, debug=args.debug)
        elif mode == "wikirestore":
            wikipush = WikiPush(
                args.source, args.target, login=args.login, debug=args.debug
            )
            queryWiki = wikipush.fromWiki
        else:
            wikipush = WikiPush(None, args.target, debug=args.debug)
            queryWiki = wikipush.toWiki
        # make the full args available to wikipush
        wikipush.args = args
        if mode == "wikiupload":
            wikipush.upload(args.files, args.force)
        else:
            pages = None
            if args.pages:
                pages = args.pages
            elif hasattr(args, "stdinp"):
                if args.stdinp:
                    pages = sys.stdin.readlines()
            if pages is None:
                # set the fixed language for the wikpush toolkit
                # SMW ask
                # see https://www.semantic-mediawiki.org/wiki/Help:Inline_queries
                # Parser function #ask
                args.language = "ask"
                query_cmd = QueryCmd(args=args, with_default_queries=False)
                handled = query_cmd.handle_args()
                if handled:
                    return 0
                query = query_cmd.queryCode
                if mode == "wikiquery":
                    formatedQueryResults = wikipush.formatQueryResult(
                        query,
                        wiki=queryWiki,
                        limit=args.limit,
                        showProgress=args.showProgress,
                        queryDivision=args.queryDivision,
                        outputFormat=args.format,
                        entityName=args.entityName,
                        title=args.title,
                    )
                    if formatedQueryResults:
                        if args.output:
                            with open(args.output, "w") as output_file:
                                print(formatedQueryResults, file=output_file)
                        else:
                            print(formatedQueryResults)
                    else:
                        print(f"Format {args.format} is not supported.")
                else:
                    pages = wikipush.query(
                        query,
                        wiki=queryWiki,
                        pageField=args.pageField,
                        limit=args.limit,
                        showProgress=args.showProgress,
                        queryDivision=args.queryDivision,
                    )
            if pages is None:
                if mode == "wikiquery":
                    # we are finished
                    return 0
                elif mode == "wikirestore":
                    # full restore
                    wikipush.restore(
                        pageTitles=None,
                        backupPath=args.backupPath,
                        listFile=args.listFile,
                    )
                else:
                    raise Exception(
                        "no pages specified - you might want to use the -p, -q -qn or --queryFile option"
                    )
            else:
                if args.ui and len(pages) > 0:
                    pages = Selector.select(
                        pages,
                        action=mode.lower().lstrip("wiki")[0].upper()
                        + mode.lstrip("wiki")[1:],
                        description="GUI program for the mode " + mode,
                        title=mode,
                    )
                    if pages == "Q":  # If GUI window is closed, end the program
                        sys.exit(0)
                if mode == "wikipush":
                    wikipush.push(
                        pages,
                        force=args.force,
                        ignore=args.ignore,
                        withImages=args.withImages,
                    )
                elif mode == "wikibackup":
                    wikipush.backup(
                        pages,
                        git=args.git,
                        withImages=args.withImages,
                        backupPath=args.backupPath,
                    )
                elif mode == "wikinuke":
                    wikipush.nuke(pages, force=args.force)
                elif mode == "wikiedit":
                    # two modes search&replace and WikiSON property edit
                    if args.search or args.replace:
                        # search&replace
                        if args.search and args.replace:
                            modify = WikiPush.getModify(
                                args.search, args.replace, args.debug
                            )
                            wikipush.edit(
                                pages,
                                modify=modify,
                                context=args.context,
                                force=args.force,
                            )
                        else:
                            raise Exception(
                                "In wikiedit search&replace mode both args '--search' and '--replace' need to be set"
                            )
                    else:
                        # WikiSON property edit
                        if len(pages) > 0 and args.template and args.property:
                            wikipush.edit_wikison(
                                page_titles=pages,
                                entity_type_name=args.template,
                                property_name=args.property,
                                value=args.value,
                                force=args.force,
                            )
                        else:
                            raise Exception(
                                "In wikiedit WikiSON edit mode '--pages', '--template' and '--property' need to be defined ('--value' is optional see '--help')"
                            )

                elif mode == "wikirestore":
                    wikipush.restore(
                        pages, backupPath=args.backupPath, stdIn=args.stdinp
                    )
                else:
                    raise Exception("undefined wikipush mode %s" % mode)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        if args.debug:
            print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    sys.exit(mainPush())
