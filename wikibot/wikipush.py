'''
Created on 2020-10-29
  @author:     wf
  @copyright:  Wolfgang Fahl. All rights reserved.

'''
from wikibot.selector import Selector
from wikibot.wikiclient import WikiClient
from mwclient.image import Image
from wikibot.smw import SMWClient
#from difflib import Differ
import difflib
import datetime
from git import Repo
import os
import re
from pathlib import Path
import sys
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class WikiPush(object):
    '''
    Push pages from one MediaWiki to another
    '''
    differ=None
    
    def __init__(self, fromWikiId, toWikiId=None,login=False,verbose=True,debug=False):
        '''
        Constructor
        '''
        self.verbose=verbose
        self.debug=debug
        self.fromWiki=None
        self.toWiki=None
        
        self.fromWikiId=fromWikiId
        if self.fromWikiId is not None:
            self.fromWiki=WikiClient.ofWikiId(fromWikiId,debug=self.debug)
        self.toWikiId=toWikiId
        if self.toWikiId is not None:
            self.toWiki=WikiClient.ofWikiId(toWikiId,debug=self.debug)
        if login and self.fromWikiId is not None:
            if not self.fromWiki.login():
                raise Exception("can't login to source Wiki %s" % fromWikiId )
        if self.toWiki is not None:
            if not self.toWiki.login():
                raise Exception("can't login to target Wiki %s" % toWikiId )
        
    def log(self,msg,end='\n'):
        if self.verbose:
            print (msg,end=end)
     
    def query(self,askQuery,wiki=None,queryField=None,limit=None,showProgress=False):
        '''
        query the given wiki for pages matching the given askQuery
        
        Args:
            askQuery(string): Semantic Media Wiki in line query https://www.semantic-mediawiki.org/wiki/Help:Inline_queries
            wiki(wikibot): the wiki to query - use fromWiki if not specified
            queryField(string): the field to select the pageTitle from
            limit(int): the limit for the query (optional)
            showProgress(bool): true if progress of the query retrieval should be indicated (default: one dot per 50 records ...)
        Returns:
            list: a list of pageTitles matching the given askQuery
        '''
        if wiki is None:
            wiki=self.fromWiki
        smwClient=SMWClient(wiki.getSite(),showProgress=showProgress)
        pageRecords=smwClient.query(askQuery,limit=limit)  
        if queryField is None:
            return pageRecords.keys()
        # use a Dict to remove duplicates
        pagesDict={}
        for pageRecord in pageRecords.values():
            pagesDict[pageRecord[queryField]]=True
        return pagesDict.keys()
    
    def nuke(self,pageTitles,force=False):
        '''
        delete the pages with the given page Titles
        
        Args:
            pageTitles(list): a list of page titles to be transfered from the formWiki to the toWiki
            force(bool): True if pages should be actually deleted - dry run only listing pages is default
        '''
        total=len(pageTitles)
        self.log("deleting %d pages in %s (%s)" % (total,self.toWikiId,"forced" if force else "dry run"))
        for i,pageTitle in enumerate(pageTitles):
            try:
                self.log("%d/%d (%4.0f%%): deleting %s ..." % (i+1,total,(i+1)/total*100,pageTitle), end='')
                pageToBeDeleted=self.toWiki.getPage(pageTitle)   
                if not force:
                    self.log("👍" if pageToBeDeleted.exists else "👎")
                else:
                    pageToBeDeleted.delete("deleted by wiknuke")    
                    self.log("✅")
            except Exception as ex:
                msg=str(ex)
                self.log("❌:%s" % msg )
                
    @staticmethod
    def getDiff(text,newText,n=1,forHuman=True):
        #if WikiPush.differ is None:
        #    WikiPush.differ=Differ()
        # https://docs.python.org/3/library/difflib.html
        #  difflib.unified_diff(a, b, fromfile='', tofile='', fromfiledate='', tofiledate='', n=3, lineterm='\n')¶
        #diffs=WikiPush.differ.compare(,)
        textLines=text.split("\n")
        newTextLines=newText.split("\n")
        diffs=difflib.unified_diff(textLines,newTextLines,n=n)
        if forHuman:
            hdiffs=[]
            for line in diffs:
                unwantedItems=["@@","---","+++"]
                keep=True
                for unwanted in unwantedItems:
                    if unwanted in line:
                        keep=False
                if keep:
                    hdiffs.append(line)    
        else:
            hdiffs=diffs
        diffStr="\n".join(hdiffs)
        return diffStr
    
    @staticmethod
    def getModify(search,replace):
        searchRegex=r"%s" % search
        replaceRegex=r"%s" % replace
        modify=lambda text: re.sub(searchRegex,replaceRegex,text)
        return modify

                
    def edit(self,pageTitles,modify=None,context=1,force=False):
        '''
        edit the pages with the given page Titles
        
        Args:
            pageTitles(list): a list of page titles to be transfered from the formWiki to the toWiki
            force(bool): True if pages should be actually deleted - dry run only listing pages is default
        '''
        if modify is None:
            raise Exception("wikipush edit needs a modify function!")
        total=len(pageTitles)
        self.log("editing %d pages in %s (%s)" % (total,self.toWikiId,"forced" if force else "dry run"))
        for i,pageTitle in enumerate(pageTitles):
            try:
                self.log("%d/%d (%4.0f%%): editing %s ..." % (i+1,total,(i+1)/total*100,pageTitle), end='')
                pageToBeEdited=self.toWiki.getPage(pageTitle)   
                if not force and not pageToBeEdited.exists:
                    self.log("👎")
                else:
                    comment="edited by wikiedit" 
                    text=pageToBeEdited.text()
                    newText=modify(text)
                    if newText!=text:
                        if force:
                            pageToBeEdited.edit(newText,comment)  
                            self.log("✅")
                        else:
                            diffStr=self.getDiff(text, newText,n=context)
                            self.log("👍%s" % diffStr)
                    else:
                        self.log("↔")
            except Exception as ex:
                msg=str(ex)
                self.log("❌:%s" % msg )            
                
    def upload(self,files,force=False):
        '''
        push the given files
        Args:
            files(list): a list of filenames to be transfered to the toWiki
            force(bool): True if images should be overwritten if they exist
        '''
        total=len(files)
        self.log("uploading %d files to %s" % (total,self.toWikiId))
        for i,file in enumerate(files):
            try:
                self.log("%d/%d (%4.0f%%): uploading %s ..." % (i+1,total,(i+1)/total*100,file), end='')
                description="uploaded by wikiupload" 
                filename=os.path.basename(file)
                self.uploadImage(file, filename, description, force)
            except Exception as ex:
                self.log("❌:%s" % str(ex) )
                
    def backup(self,pageTitles,backupPath=None,git=False,withImages=False):
        '''
        backup the given page titles
        Args:
            pageTitles(list): a list of page titles to be downloaded from the fromWiki
            git(bool): True if git should be used as a version control system
            withImages(bool): True if the image on a page should also be copied
        '''
        if backupPath is None:
            backupPath=self.getHomePath("wikibackup/%s" % self.fromWikiId)
        imageBackupPath="%s/images" % backupPath
        total=len(pageTitles)
        self.log("downloading %d pages from %s to %s" % (total,self.fromWikiId,backupPath))
        for i,pageTitle in enumerate(pageTitles):
            try:
                self.log("%d/%d (%4.0f%%): downloading %s ..." % (i+1,total,(i+1)/total*100,pageTitle), end='')
                page=self.fromWiki.getPage(pageTitle)
                wikiFilePath="%s/%s.wiki" % (backupPath,pageTitle)
                self.ensureParentDirectoryExists(wikiFilePath)
                with open (wikiFilePath,"w") as wikiFile:
                    wikiFile.write(page.text())
                self.log("✅")
                if isinstance(page,Image):
                    self.backupImages([page],imageBackupPath)
                if withImages:
                    self.backupImages(page.images(), imageBackupPath)    
                    
            except Exception as ex:
                self.log("❌:%s" % str(ex) )
        if git:
            gitPath="%s/.git" % backupPath
            if not os.path.isdir(gitPath):
                self.log("initializing git repository ...")
                repo=Repo.init(backupPath)
            else:
                repo=Repo(backupPath)
            self.log("committing to git repository")
            repo.git.add(all=True)
            timestamp=datetime.datetime.now().isoformat()
            repo.index.commit("auto commit by wikibackup at %s" % timestamp)
        
    def backupImages(self,imageList,imageBackupPath):
        '''
        '''
        for image in imageList:
            try:
                imagePath,filename=self.downloadImage(image,imageBackupPath);
            except Exception as ex:
                self.handleException(ex)
        
    def push(self,pageTitles,force=False,ignore=False,withImages=False):
        '''
        push the given page titles
        
        Args:
            pageTitles(list): a list of page titles to be transfered from the formWiki to the toWiki
            force(bool): True if pages should be overwritten if they exist
            ignore(bool): True if warning for images should be ignored (e.g if they exist)
            withImages(bool): True if the image on a page should also be copied
        '''
        total=len(pageTitles)
        self.log("copying %d pages from %s to %s" % (total,self.fromWikiId,self.toWikiId))
        for i,pageTitle in enumerate(pageTitles):
            try:
                self.log("%d/%d (%4.0f%%): copying %s ..." % (i+1,total,(i+1)/total*100,pageTitle), end='')
                page=self.fromWiki.getPage(pageTitle)
                if page.exists:
                    # is this an image?
                    if isinstance(page,Image):
                        self.pushImages([page],ignore=ignore)
                    else:
                        newPage=self.toWiki.getPage(pageTitle)
                        if not newPage.exists or force:
                            try:
                                comment="pushed from %s by wikipush" % self.fromWikiId
                                newPage.edit(page.text(),comment)
                                self.log("✅")
                                pageOk=True
                            except Exception as ex:
                                pageOk=self.handleException(ex, ignore)
                            if withImages and pageOk:
                                self.pushImages(page.images(),ignore=ignore)
                        else:
                            self.log("👎")
                else:
                    self.log("❌")
            except Exception as ex:
                self.log("❌:%s" % str(ex) )
                
    def ensureParentDirectoryExists(self,filePath):
        # for pages that have a "/" in the name:
        directory = os.path.dirname(filePath)
        self.ensureDirectoryExists(directory)
        
    def ensureDirectoryExists(self,directory):
        Path(directory).mkdir(parents=True, exist_ok=True)
        
    def getHomePath(self,localPath):
        '''
        get the given home path
        '''
        homePath=str(Path.home() / localPath)
        self.ensureDirectoryExists(homePath)
        return homePath
                    
    def getDownloadPath(self):
        '''
        get the download path
        '''
        return self.getHomePath("Downloads/mediawiki")
        
            
    def pushImages(self,imageList,delim="",ignore=False):
        '''
        push the images in the given image List
        
        Args:
            imageList(list): a list of images to be pushed
            ignore(bool): True to upload despite any warnings.
        '''        
        for image in imageList:
            try:
                self.log("%scopying image %s ..." % (delim,image.name), end='')  
                imagePath,filename=self.downloadImage(image);
                description=image.imageinfo['comment'] 
                self.uploadImage(imagePath,filename,description,ignore)
                if self.debug:
                    print(image.imageinfo)
            except Exception as ex:
                self.handleException(ex,ignore)
                
    def handleException(self,ex,ignoreExists=False):
        '''
        handle the given exception and ignore it if it includes "exists" and ignoreExists is True
        
        Args:
            ex(Exception): the exception to handle
            ignoreExists(bool): True if "exists" should be ignored
            
        Returns:
            bool: True if the exception was handled as ok False if it was logged as an error
        '''
        msg=str(ex)
        return self.handleWarning(msg,marker="❌",ignoreExists=ignoreExists)
        
    def handleAPIWarnings(self,warnings,ignoreExists=False):
        '''
        handle API Warnings
        
        Args:
            warnings(list): a list of API warnings
            ignoreExists(bool): ignore messages that warn about existing content
        '''
        msg=""
        if warnings:
            for warning in warnings:
                msg+="%s\n" % str(warning)
        self.handleWarning(msg,ignoreExists)
        
    def handleWarning(self,msg,marker="⚠️",ignoreExists=False):
        '''
        handle the given warning and ignore it if it includes "exists" and ignoreExists is True
        
        Args:
            msg(string): the warning to handle
            marker(string): the marker to use for the message
            ignoreExists(bool): True if "exists" should be ignored
            
        Returns:
            bool: True if the exception was handled as ok False if it was logged as an error
        '''
        #print ("handling warning %s with ignoreExists=%r" % (msg,ignoreExists))
        if ignoreExists and "exists" in msg:
            # shorten exact duplicate message
            if "exact duplicate in msg":
                msg="exact duplicate"
            marker="👀"
        self.log("%s:%s" % (marker,msg))
        return marker=="👀"
                
    def downloadImage(self,image,downloadPath=None):
        '''
        download the given image
        
        Args:
            image(image): the image to download
            downloadPath(str): the path to download to if None getDownloadPath will be used
        '''
        filename=image.name.replace("File:","")
        if downloadPath is None:
            downloadPath=self.getDownloadPath()
        imagePath="%s/%s" % (downloadPath,filename)
        self.ensureParentDirectoryExists(imagePath)
        with open(imagePath,'wb') as imageFile:
            image.download(imageFile)
        return imagePath,filename
                            
    def uploadImage(self,imagePath,filename,description,ignoreExists=False):
        '''
        upload an image
        
        Args:
            imagePath(str): the path to the image
            filename(str): the filename to use
            description(str): the description to use
            ignoreExists(bool): True if it should be ignored if the image exists
        '''
        with open(imagePath,'rb') as imageFile:
            warnings=None
            response=self.toWiki.site.upload(imageFile,filename,description,ignoreExists)
            if 'warnings' in response:
                warnings=response['warnings']
            if 'upload' in response and 'warnings' in response['upload']:
                warningsDict=response['upload']['warnings']
                warnings=[]
                for item in warningsDict.items():
                    warnings.append(str(item))
            self.handleAPIWarnings(warnings,ignoreExists)
       

__version__ = "0.1.15"
__date__ = '2020-10-31'
__updated__ = '2020-12-05'
DEBUG=False

def mainNuke(argv=None):
    main(argv,mode='wikinuke')
    
def mainEdit(argv=None):
    main(argv,mode='wikiedit')
    
def mainPush(argv=None):
    main(argv,mode='wikipush')
    
def mainUpload(argv=None):
    main(argv,mode='wikiupload')

def mainBackup(argv=None):
    main(argv,mode='wikibackup')
    
def main(argv=None,mode='wikipush'): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv = sys.argv[1:]
    
    program_name = mode
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "wikipush"
    user_name="Wolfgang Fahl"
    
    program_license = '''%s

  Created by %s on %s.
  Copyright 2020 Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

''' % (program_shortdesc,user_name, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug",   action="store_true", help="set debug level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)       
        if mode=="wikipush":
            parser.add_argument("-l", "--login", dest="login", action='store_true', help="login to source wiki for access permission")
            parser.add_argument("-s", "--source", dest="source", help="source wiki id", required=True)
            parser.add_argument("-f", "--force", dest="force", action='store_true', help="force to overwrite existing pages")
            parser.add_argument("-i", "--ignore", dest="ignore", action='store_true', help="ignore upload warnings e.g. duplicate images")
            parser.add_argument("-wi", "--withImages", dest="withImages", action='store_true', help="copy images on the given pages")
        elif mode=="wikibackup": 
            parser.add_argument("-g", "--git", dest="git", action='store_true', help="use git for version control")
            parser.add_argument("-l", "--login", dest="login", action='store_true', help="login to source wiki for access permission")
            parser.add_argument("-s", "--source", dest="source", help="source wiki id", required=True)
            parser.add_argument("-wi", "--withImages", dest="withImages", action='store_true', help="copy images on the given pages")
        elif mode=="wikinuke":
            parser.add_argument("-f", "--force", dest="force", action='store_true', help="force to delete pages - default is 'dry' run only listing pages")            
        elif mode=="wikiedit":
            parser.add_argument("--search", dest="search", help="search pattern", required=True)
            parser.add_argument("--replace", dest="replace", help="replace pattern", required=True)
            parser.add_argument("--context", dest="context",type=int, help="number of context lines to show in dry run diff display",default=1)
            parser.add_argument("-f", "--force", dest="force", action='store_true', help="force to edit pages - default is 'dry' run only listing pages")            
        elif mode=="wikiupload":
            parser.add_argument("--files", nargs='+', help="list of files to be uploaded", required=True)
            parser.add_argument("-f", "--force", dest="force", action='store_true', help="force to (re)upload existing files - default is false")            
            pass
        if mode in  ["wikipush","wikiedit","wikinuke","wikibackup"]: 
            parser.add_argument("--limit",dest="limit",type=int,help="limit for query")
            parser.add_argument("--progress",dest="showProgress",action='store_true',help="shows progress for query")
            parser.add_argument("-q", "--query", dest="query", help="select pages with given SMW ask query", required=False)
            parser.add_argument("-qf", "--queryField",dest="queryField",help="query result field which contains page")
            parser.add_argument("-p", "--pages", nargs='+', help="list of page Titles to be pushed", required=False)
            parser.add_argument("-ui", "--withGUI", dest="ui", help="Pop up GUI for selection", action="store_true",required=False)
        
        if not mode=="wikibackup":
            parser.add_argument("-t", "--target", dest="target", help="target wiki id", required=True)    
        # Process arguments
        args = parser.parse_args(argv)
        
        if mode=="wikipush":
            wikipush=WikiPush(args.source,args.target,login=args.login,debug=args.debug)
            queryWiki=wikipush.fromWiki
        elif mode=="wikibackup":
            wikipush=WikiPush(args.source,None,login=args.login,debug=args.debug)    
            queryWiki=wikipush.fromWiki
        elif mode=="wikiupload":
            wikipush=WikiPush(None,args.target,debug=args.debug)
        else:
            wikipush=WikiPush(None,args.target,debug=args.debug)
            queryWiki=wikipush.toWiki
        if mode=="wikiupload":
            wikipush.upload(args.files,args.force)
        else:    
            pages=None
            if args.pages:
                pages=args.pages
            elif args.query:
                pages=wikipush.query(args.query,wiki=queryWiki,queryField=args.queryField,limit=args.limit,showProgress=args.showProgress)
            if pages is None:
                raise Exception("no pages specified - you might want to use the -p or -q option")
            else:
                if args.ui:
                    pages = Selector.select(pages, action=mode.lower().lstrip("wiki")[0].upper() + mode.lstrip("wiki")[1:],
                                            description='GUI program for the mode ' + mode,title=mode)
                    if pages == 'Q': #If GUI window is closed, end the program
                        sys.exit(0)
                if mode=="wikipush":
                    wikipush.push(pages,force=args.force,ignore=args.ignore,withImages=args.withImages)
                elif mode=="wikibackup":
                    wikipush.backup(pages,git=args.git,withImages=args.withImages)    
                elif mode=='wikinuke':
                    wikipush.nuke(pages,force=args.force)
                elif mode=='wikiedit':
                    modify=WikiPush.getModify(args.search,args.replace)
                    wikipush.edit(pages,modify=modify,context=args.context,force=args.force)
                else:
                    raise Exception("undefined wikipush mode %s" % mode)
        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
                
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(mainPush())