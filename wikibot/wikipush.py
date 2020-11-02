'''
Created on 2020-10-29

@author: wf

 script to read push wikipages from one MediaWiki to another
  
  use: python3 wikipush.py --source [sourceId] --target [targetId] --pages [pageTitleList]
  @param sourceId - id of the source wiki
  @param targetId - id of the target wiki
  @param pages - pageList to transfer
  
  example: 
      python3 wikipush -s wikipedia-de -t test Berlin

  @author:     wf
  @copyright:  Wolfgang Fahl. All rights reserved.

'''
from wikibot.wikibot import WikiBot
from pywikibot.page import Page
from pywikibot.specialbots import UploadRobot
import pywikibot
import os
import sys
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class WikiPush(object):
    '''
    Push pages from one MediaWiki to another
    '''


    def __init__(self, fromWikiId, toWikId,verbose=True,debug=False):
        '''
        Constructor
        '''
        self.verbose=verbose
        self.debug=debug
        self.fromWikiId=fromWikiId
        self.fromWiki=WikiBot.ofWikiId(fromWikiId)
        self.toWikiId=toWikId
        self.toWiki=WikiBot.ofWikiId(toWikId)
        
    def push(self,*pageTitles):
        '''
        push the given page titles
        '''
        if self.verbose:
            print("copying %d pages from %s to %s" % (len(pageTitles),self.fromWikiId,self.toWikiId))
        for pageTitle in pageTitles:
            if self.verbose:
                print ("copying %s ..." % pageTitle, end='')
            page=self.fromWiki.getPage(pageTitle)
            newPage=Page(self.toWiki.site,pageTitle)
            newPage.text=page.text
            newPage.save("pushed by wikipush")
            if self.verbose:
                print ("✓")
            self.pushImages(page.imagelinks())
            
    def pushImages(self,imageList):
        '''
        push the images in the given image List
        
        Args:
            imageList(list): a list of images to be pushed
        '''
        
        # see also https://gerrit.wikimedia.org/g/pywikibot/core/+/HEAD/scripts/imagetransfer.py
        for image in imageList:
            if self.verbose:
                print("copying image %s ..." % image, end='')
                print()
                targetTitle = 'File:' + image.title().split(':', 1)[1]
                targetImage=Page(self.toWiki.site,targetTitle)
                try:
                    targetImage.get()
                    imageExists=True
                except pywikibot.NoPage:  
                    imageExists=False
                    pass
                if not imageExists:
                    # upload the image
                    # see https://gerrit.wikimedia.org/g/pywikibot/core/+/HEAD/scripts/upload.py
                    pass
                                 

__version__ = 0.1
__date__ = '2020-10-31'
__updated__ = '2020-10-31'
DEBUG=False

def main(argv=None): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)   
    
    program_name = os.path.basename(sys.argv[0]) 
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    user_name="Wolfgang Fahl"
    
    program_license = '''%s

  Created by %s on %s.
  Copyright 2020 Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc,user_name, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug",   action="count", help="set debug level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)

        parser.add_argument("-s", "--source", dest="source", help="source wiki id", required=True)
        parser.add_argument("-t", "--target", dest="target", help="target wiki id", required=True)    
        parser.add_argument("-p", "--pages", nargs='+', help="list of page Titles to be pushed", required=True)
        # Process arguments
        args = parser.parse_args()
        
        wikipush=WikiPush(args.source,args.target)
        
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
    sys.exit(main())