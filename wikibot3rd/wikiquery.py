'''
Created on 2021-02-16

@author: wf
'''
import sys
import wikibot3rd.wikipush 
DEBUG=False

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(wikibot3rd.wikipush.mainQuery())