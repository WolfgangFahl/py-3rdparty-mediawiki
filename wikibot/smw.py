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
        self.debug=PrintRequest.debug
        if self.debug:
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
        """ deserialize a single value 
        Args:
            value(object): the value to be deserialized according to the typeid
            
        Returns:
            the deserialized value
        """
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
            if 'timestamp' in value:
                ts=int(value['timestamp'])
                try:
                    value=datetime.utcfromtimestamp(ts)
                    #  print (date.strftime('%Y-%m-%d %H:%M:%S'))
                except ValueError as ve:
                    if self.debug:
                        print("Warning timestamp %d is invalid: %s" % (ts,str(ve)))
                    pass
            else:
                # ignore faulty values
                if self.debug:
                    print("Warning: timestamp missing for value")
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
            # handle lists
            # empty lists => None
            if len(valueList)==0:
                value=None    
            # lists with one value -> return the item (this unfortunately removes the list property of the value)   
            elif len(valueList)==1:
                value=valueList[0]
            # only if there is a "real" list return it    
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
    * https://www.semantic-mediawiki.org/wiki/Help:API:askargs
    
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
        if results:
            for key in results.keys():
                record=results[key]
                recordDict={}
                for label in prdict.keys():
                    pr=prdict[label]
                    recordDict[label]=pr.deserialize(record)
                resultDict[key]=recordDict
        return resultDict
    
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

class SMWClient(SMW):
    '''
    Semantic MediaWiki access using mw client library
    '''
    
    def __init__(self, site=None,prefix="/"):
        super(SMWClient,self).__init__(site,prefix) 
        pass
    
    def info(self):
        """ see https://www.semantic-mediawiki.org/wiki/Help:API:smwinfo"""
        results = self.site.raw_api('smwinfo', http_method='GET')
        self.site.handle_api_result(results)  # raises APIError on error
        
        return results
    
    def ask(self, query, title=None, limit=None):
        """
        Ask a query against Semantic MediaWiki.

        API doc: https://semantic-mediawiki.org/wiki/Ask_API

        Returns:
            Generator for retrieving all search results, with each answer as a dictionary.
            If the query is invalid, an APIError is raised. A valid query with zero
            results will not raise any error.

        Examples:

            >>> query = "[[Category:my cat]]|[[Has name::a name]]|?Has property"
            >>> for answer in site.ask(query):
            >>>     for title, data in answer.items()
            >>>         print(title)
            >>>         print(data)
        """
        kwargs = {}
        if title is None:
            kwargs['title'] = title

        offset = 0
        while offset is not None:
            results = self.site.raw_api('ask', query=u'{query}|offset={offset}'.format(
                query=query, offset=offset), http_method='GET', **kwargs)
            self.site.handle_api_result(results)  # raises APIError on error
            offset = results.get('query-continue-offset')
            # workaround limit
            if limit is not None and offset is not None and offset>=limit:
                offset=None
            yield results
    
    def rawquery(self,askQuery,title=None,limit=None):
        '''
        run the given askQuery and return the raw result
        Args:
            askQuery(string): the SMW inline query to be send via api
            title(string): the title (if any)
            limit(int): the maximum number of records to be retrieved (if any)
            
        Returns:
            dict: the raw query result as returned by the ask API
        '''
        fixedAsk=self.fixAsk(askQuery)
        result=None
        for singleResult in self.ask(fixedAsk, title, limit):
            if result is None:
                result=singleResult
            else:
                results=result['query']['results']
                singleResults=singleResult['query']['results']
                results.update(singleResults)
        return result
        
    def query(self,askQuery,title=None,limit=None):
        '''
        run query and return list of Dicts
        '''
        rawresult=self.rawquery(askQuery, title, limit)
        lod=self.deserialize(rawresult)
        return lod
    
class SMWBot(SMW):
    '''
    Semantic MediaWiki access using pywikibot library
    '''
    def __init__(self, site=None,prefix="/"):
        super(SMWBot,self).__init__(site,prefix) 
        pass
    
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
    
    def rawquery(self,ask,limit=None):
        """ send a query see https://www.semantic-mediawiki.org/wiki/Help:Inline_queries#Parser_function_.23ask
        Args:
            ask(str): the SMW ASK query as it would be used in MediaWiki markup"""
        # allow usage of original Wiki ask content - strip all non needed parts
        fixedAsk=self.fixAsk(ask)
        # set parameters for request
        parameters={"action": "ask","query":fixedAsk}
        result=self.submit(parameters)
        return result
    
    def query(self,ask,limit=None):
        '''
        send a query and deserialize it
        '''
        rawresult=self.rawquery(ask,limit=limit)
        result=self.deserialize(rawresult)
        return result