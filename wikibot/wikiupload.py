'''
Created on 2020-11-12

@author: wf
'''
import sys
import wikibot.wikipush 
DEBUG=False

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(wikibot.wikipush.mainUpload())