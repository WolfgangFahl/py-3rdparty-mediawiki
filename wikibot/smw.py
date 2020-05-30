'''
Created on 29.05.2020

@author: wf
'''
from pywikibot.data.api import Request
import re

class PrintRequest(object):
    """
    construct the given print request
    see https://www.semantic-mediawiki.org/wiki/Serialization_(JSON)
    """
    def __init__(self,record):
        print(record)
        self.label=record['label']
        self.key=record['key']
        self.redi=record['redi']
        self.typeid=record['typeid']
        self.mode=int(record['mode'])
        if 'format' in record:
            self.format=record['format']
        else:
            self.format=None   
            
    def deserialize(self,result):
        po=result['printouts']
        if self.label:
            value=po[self.label]
        else:
            value=result['fullurl']
        return value    
            
    def __repr__(self):
        text="PrintRequest(label='%s' key='%s' redi='%s' typeid='%s' mode=%d format='%s')" % (self.label,self.key,self.redi,self.typeid,self.mode,self.format)
        return text

class SMW(object):
    '''
    Semantic MediaWiki Access e.g. for ask API
    see
    * https://www.semantic-mediawiki.org/wiki/Help:API
    * https://www.semantic-mediawiki.org/wiki/Serialization_(JSON)
    
    adapted from Java SimpleGraph Module 
    https://github.com/BITPlan/com.bitplan.simplegraph/blob/master/simplegraph-smw/src/main/java/com/bitplan/simplegraph/smw/SmwSystem.java
    '''

    def __init__(self, site=None):
        '''
        Constructor
        '''
        self.site=site
        
    def submit(self, parameters):
        """ submit the request with the given parameters"""
        request=Request(site=self.site,parameters=parameters)
        return request.submit()    
    
    def info(self):
        parameters={"action": "smwinfo"}
        return self.submit(parameters)
    
    def rawquery(self,ask):
        """ send a query """
        # allow usage of original Wiki ask content - strip all non needed parts
        fixedAsk=self.fixAsk(ask)
        # set parameters for request
        parameters={"action": "ask","query":fixedAsk}
        result=self.submit(parameters)
        return result
    
    def deserialize(self,rawresult):
        """ deserialize the given rawresult according to 
        https://www.semantic-mediawiki.org/wiki/Serialization_(JSON)
        """
        if not 'query' in rawresult:
            raise Exception("invalid query result - 'query' missing")
        query=rawresult['query']
        if not 'printrequests' in query:
            raise Exception("invalid query result - 'printrequests' missing")
        printrequests=query['printrequests']
        if not 'results' in query:
            raise Exception("invalid query result - 'results' missing")
        results=query['results']
        prdict={}
        for record in printrequests:
            pr=PrintRequest(record)
            prdict[pr.label]=pr
        resultDict={}
        for key in results.keys():
            record=results[key]
            recordDict={}
            for label in prdict.keys():
                pr=prdict[label]
                recordDict[label]=pr.deserialize(record)
            resultDict[key]=recordDict
        return resultDict
    
    def query(self,ask):
        rawresult=self.rawquery(ask)
        result=self.deserialize(rawresult)
        return result
    
    def fixAsk(self,ask):
        """ fix an ask String to be usable for the API
        @param ask
                 - a "normal" ask query
        @return - the fixed asked query
        """
        # ^\\s*\\{\\{
        # remove {{ with surrounding white space at beginning
        fixedAsk = re.sub(r"^\s*\{\{", "",ask)
        # remove #ask:
        fixedAsk = re.sub(r"#ask:", "",fixedAsk)
        # remove }} with surrounding white space at end
        fixedAsk = re.sub(r"\}\}\s*$", "",fixedAsk)
        # split by lines (with side effect to remove newlines)
        parts = fixedAsk.split(r"\n")
        fixedAsk = ""
        for part in parts:
            #  remove whitespace around part
            part = part.strip();
            # remove whitespace around pipe sign
            part = re.sub(r"\s*\|\s*", "|",part);
            # remove whitespace around assignment =
            part = re.sub(r"\s*=\s*", "=",part);
            # remove whitespace in query parts
            part = re.sub(r"\]\s*\[", "][",part);
            # replace blanks with _
            part = re.sub(" ", "_",part);
            fixedAsk = fixedAsk+ part;
        return fixedAsk
    
    def getConcept(self,ask):
        """ get the concept from the given ask query"""
        m=re.search(r"\[\[Concept:(.+?)\]\]",ask)
        if m:
            return m.groups()[0]
        else:
            return None
        
        