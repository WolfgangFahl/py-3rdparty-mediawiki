'''
Created on 2020-11-01

@author: wf
'''

import os
import sys
from os.path import isdir
from os import makedirs
from wikibot.crypt import Crypt
import datetime

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from pathlib import Path
import getpass

class WikiUser(object):
    '''
    User credentials for a specific wiki
    '''
    
    def __init__(self):
        # set None values for all fields
        for field in WikiUser.getFields():
            self.__dict__[field]=None
    
    def getPassword(self):
        c=Crypt(self.cypher,20,self.salt)
        return c.decrypt(self.secret)
    
    def getWikiUrl(self):
        '''
        return the full url of this wiki
        '''
        url="%s%s" % (self.url,self.scriptPath)
        return url
    
    def interactiveSave(self,yes,filePath=None):
        '''
        save me
        '''
        fields=WikiUser.getFields(encrypted=False)
        for field in fields:
            if field not in self.__dict__ or self.__dict__[field] is None:
                self.__dict__[field]=input("%s: " %field)
        # encrypt
        self.encrypt()
        if not yes:
            answer=input("shall i store %s? yes/no y/n" % self)
            yes="y" in answer or "yes" in answer
        if yes:
            self.save(filePath)
    
    def encrypt(self):
        '''
        encrypt my clear text password
        '''
        crypt=Crypt.getRandomCrypt()
        self.secret=crypt.encrypt(self.password)
        self.cypher=crypt.cypher.decode()
        self.salt=crypt.salt.decode()
    
    def __str__(self):
        return "%s %s" % (self.user,self.wikiId)
    
    @staticmethod
    def getIniPath():
        home = str(Path.home())
        return "%s/.mediawiki-japi" % home
    
    @staticmethod
    def iniFilePath(wikiId):
        user=getpass.getuser()
        iniFilePath="%s/%s_%s.ini" % (WikiUser.getIniPath(),user,wikiId)
        return iniFilePath
    
    @staticmethod
    def ofWikiId(wikiId,lenient=False):
        path=WikiUser.iniFilePath(wikiId)
        try:
            config=WikiUser.readPropertyFile(path)
        except FileNotFoundError as e:
            raise FileNotFoundError('the wiki with the wikiID "%s" does not have a corresponding configuration file ... you might want to create one with the wikiuser command' % (wikiId))
        wikiUser=WikiUser.ofDict(config,lenient=lenient)
        return wikiUser
    
    def save(self,iniFilePath=None):
        '''
        save me to a propertyFile
        '''
        if iniFilePath is None:
            iniPath=WikiUser.getIniPath()
            if not isdir(iniPath):
                makedirs(iniPath)
            iniFilePath=WikiUser.iniFilePath(self.wikiId)
        
        iniFile=open(iniFilePath,"w")
        isodate=datetime.datetime.now().isoformat()
        template="""# Mediawiki JAPI credentials for %s
# created by py-3rdparty-mediawiki WikiUser at %s
"""
        content=template % (self.wikiId,isodate)
        for field in WikiUser.getFields():
            value=self.__dict__[field]
            if value is not None:
                content+="%s=%s\n" % (field,value) 
    
        iniFile.write(content)
        iniFile.close()
       
    @staticmethod
    def readPropertyFile(filepath, sep='=', comment_char='#'):
        """
        Read the file passed as parameter as a properties file.
        https://stackoverflow.com/a/31852401/1497139
        """
        props = {}
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"') 
                    props[key] = value 
        return props
                    
    @staticmethod
    def getWikiUsers():
        wikiUsers={}
        iniPath=WikiUser.getIniPath()
        if os.path.isdir(iniPath):
            with os.scandir(iniPath) as it:
                for entry in it:
                    if entry.name.endswith(".ini") and entry.is_file():
                        try:
                            config=WikiUser.readPropertyFile(entry.path)
                            wikiUser=WikiUser.ofDict(config)
                            wikiUsers[wikiUser.wikiId]=wikiUser
                        except Exception as ex:
                            print ("error in %s: %s" % (entry.path,str(ex)))
        return wikiUsers
    
    @staticmethod
    def getFields(encrypted=True):
        # copy fields
        fields=['email','scriptPath','user','url','version','wikiId']
        passwordFields=['cypher','secret','salt'] if encrypted else ['password']
        result=[]
        result.extend(fields)
        result.extend(passwordFields)
        return result
    
    @staticmethod
    def ofDict(userDict,encrypted=True,lenient=False):
        wikiUser=WikiUser()
        # fix http\: entries from Java created entries
        if 'url' in userDict and userDict['url'] is not None:
            userDict['url']=userDict['url'].replace("\:",":")
            
        for field in WikiUser.getFields(encrypted):
            if field in userDict:
                wikiUser.__dict__[field]=userDict[field]    
            else:
                if not lenient:
                    raise Exception("%s missing " % field)  
        if not encrypted:
            wikiUser.encrypt()   
        return wikiUser
    
__version__ = 0.1
__date__ = '2020-10-31'
__updated__ = '2020-10-31'
DEBUG=False    

def main(argv=None): # IGNORE:C0111
    '''
    WikiUser credential handling
    '''

    if argv is None:
        argv = sys.argv[1:]
    
    program_name = os.path.basename(sys.argv[0]) 
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "WikiUser credential handling"
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

        parser.add_argument("-e", "--email", dest="email", help="email of the user")
        parser.add_argument("-f", "--file", dest="filePath", help="ini-file path")
        parser.add_argument("-l", "--url", dest="url", help="url of the wiki")
        parser.add_argument("-s", "--scriptPath", dest="scriptPath", help="script path")
        parser.add_argument("-p", "--password", dest="password", help="password")
        parser.add_argument("-u", "--user", dest="user", help="os user id")
        parser.add_argument("-v", "--wikiVersion", dest="version", help="version of the wiki")
        parser.add_argument("-w", "--wikiId", dest="wikiId", help="wiki Id")
        parser.add_argument("-y", "--yes", dest="yes", action='store_true', help="immediately store without asking")
        # Process arguments
        args = parser.parse_args(argv)
        argsDict=vars(args)
        wikiuser=WikiUser.ofDict(argsDict,encrypted=False,lenient=True)
        wikiuser.interactiveSave(args.yes,args.filePath)
        
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

if __name__ == '__main__':
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())