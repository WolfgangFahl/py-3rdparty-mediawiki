'''
Created on 2020-05-29

@author: wf
'''
from pywikibot.data.api import Request
import re
from datetime import datetime
from urllib.parse import unquote

class PrintRequest(object):
    debug=False
    """
    construct the given print request
    see https://www.semantic-mediawiki.org/wiki/Serialization_(JSON)
    :ivar smw: SMW context for this printrequest
    :ivar label: the label of the printrequest
    :ivar key: 
    :ivar redi: 
    :ivar typeid: 
    :ivar mode:  
    :ivar format: 
    """
    def __init__(self,smw,record):
        '''
        construct me from the given record
        Args:
            smw(SMW): the SemanticMediaWiki context of this PrintRequest
            record(dict): the dict derived from the printrequest json serialization  
        '''
        self.smw=smw
        if PrintRequest.debug:
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
            
    def deserializeSingle(self,value):
        """ deserialize a single value """
        # FIXME complete list of types according to
        # https://www.semantic-mediawiki.org/wiki/Help:API:ask  
        # Page https://www.semantic-mediawiki.org/wiki/Help:API:ask/Page    
        if self.typeid=="_wpg":  
            value=value["fulltext"]
            if value:
                value=unquote(value)
            pass  
        # Text https://www.semantic-mediawiki.org/wiki/Help:API:ask/Text
        elif self.typeid=="_txt":
            pass
        elif self.typeid=="_qty":    
            pass
        elif self.typeid=="_num":
            value=int(value)            
        elif self.typeid=="_dat":
            ts=int(value['timestamp'])
            value=datetime.utcfromtimestamp(ts)
            # print (date.strftime('%Y-%m-%d %H:%M:%S'))
            pass
        elif self.typeid=="_eid":
            pass
        else:   
            pass
        return value
            
    def deserialize(self,result):
        """ deserialize the given result record
        Args:
            result(dict): a single result record dict from the deserialiation of the ask query
        Returns:    
            object: a single deserialized value according to my typeid   
        """
        po=result['printouts']
        if self.label in po:
            value=po[self.label]
        else:
            value=result
        if isinstance(value,list):
            valueList=[]
            for valueItem in value:
                valueList.append(self.deserializeSingle(valueItem))
            if len(valueList)==1:
                value=valueList[0]
            else:        
                value=valueList  
        else:
            value=self.deserializeSingle(value)                           
        
        if PrintRequest.debug:
            print ("%s(%s)='%s'" % (self.label,self.typeid,value))  
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
    :ivar site: the pywikibot site to use for requests
    :ivar prefix: the path prefix for this site e.g. /wiki/
    '''

    def __init__(self, site=None,prefix="/"):
        '''
        Constructor
        Args:
            site: the site to use (optional)
        '''
        self.site=site
        self.prefix=prefix
        
    def submit(self, parameters):
        """ submit the request with the given parameters
        Args:
            parameters(list): the parameters to use for the SMW API request
        Returns:
            dict: the submit result"""
        request=Request(site=self.site,parameters=parameters)
        return request.submit()    
    
    def info(self):
        """ see https://www.semantic-mediawiki.org/wiki/Help:API:smwinfo"""
        parameters={"action": "smwinfo"}
        return self.submit(parameters)
    
    def rawquery(self,ask):
        """ send a query see https://www.semantic-mediawiki.org/wiki/Help:Inline_queries#Parser_function_.23ask
        Args:
            ask(str): the SMW ASK query as it would be used in MediaWiki markup"""
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
            pr=PrintRequest(self,record)
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
        :param ask: - a "normal" ask query
        :return: the fixed asked query
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