'''
Created on 2020-05-29

@author: wf
'''
import re
import sys
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
    
class SplitClause():
    '''
    Query parameter to be used for splitting e.g. Modification date, Creation Date, could be potentially
    any parameter that is ordered and countable
    Currently we assume a parameter of type Date and use Modification date by default
    '''
    
    def __init__(self,name="Modification date",label="mdate"):
        '''
        construct me
        '''
        self.name=name
        self.label=label
        
    def queryBounds(self,lowerBound,upperBound)->str:
        '''
        get the query bounds
        e.g. [[Modification date::>=2021-01-01T12:00

        Args:
            lowerBound(datetime): start of the time interval
            upperBound(datetime): end of the time interval

        Returns:
            Returns the SMW ask part for the boundary
        '''
        result=f"[[{self.name}:: >={lowerBound.isoformat()}]]|[[{self.name}:: <={upperBound.isoformat()}]]"
        return result

    def getFirst(self)->str:
        '''
        get the first element
        '''
        result=f"?{self.name}={self.label}|sort={self.name}|limit=1"
        return result
    
    def deserialize(self,values):
        '''
        deserialize my query result
        '''
        # dict: {
        #    'Property:Foaf:knows': {
        #       '': 'Property:Foaf:knows', 
        #       'Modification date': datetime.datetime(2020, 11, 28, 17, 40, 36)
        #    }
        # }
        date=None
        vlist=list(values)
        if len(vlist)>0:
            innerValue = vlist[0]
            if self.label in innerValue:
                date=innerValue[self.label]
        return date
        

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
    def __init__(self, site=None,prefix="/",showProgress=False, queryDivision=1,debug=False):
        '''
        Constructor
        Args:
            site: the site to use (optional)
            showProgess(bool): if progress should be shown
            queryDivision(int): Defines the number of subintervals the query is divided into (must be greater equal 1)
            debug(bool): if debugging should be activated - default: False
        '''
        self.site=site
        self.prefix=prefix
        self.showProgress=showProgress
        self.queryDivision=queryDivision
        self.splitClause=SplitClause()
        self.debug=debug
    
    def deserialize(self,rawresult):
        """ deserialize the given rawresult according to 
        https://www.semantic-mediawiki.org/wiki/Serialization_(JSON)
        
        Args:
            rawresult(dict): contains printrequests and results which need to be merged
            
        Returns:
            list: list of dicts with results
        """
        resultDict={}
        if rawresult is None:
            return resultDict
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

    argumentRegex = staticmethod(lambda arg: r"\| *" + arg + r" *= *\d+(?=\s|\||$)")

    @staticmethod
    def getOuterMostArgumentValueOfQuery(argument, query):
        """
        Extracts the integer value of the given argument from the given query
        Args:
            argument(string): Argument that should be extracted
            query(string): smw query where the given argument is assumed
        Returns:
            Returns integer value of the given argument in the given query.
            If the argument occurs multiple times the last one is returned.
            If it does not occur return None.
        """
        if not argument or not query:
            return None
        args = re.compile(SMW.argumentRegex(argument), re.IGNORECASE).findall(query)
        if not args:
            return None
        return int(re.compile("[0-9]+").search(args[-1]).group())


class SMWClient(SMW):
    '''
    Semantic MediaWiki access using mw client library
    '''
    
    def __init__(self, site=None,prefix="/",showProgress=False, queryDivision=1,debug=False):
        super(SMWClient,self).__init__(site,prefix,showProgress=showProgress, queryDivision=queryDivision,debug=debug)
        pass
    
    def info(self):
        """ see https://www.semantic-mediawiki.org/wiki/Help:API:smwinfo"""
        results = self.site.raw_api('smwinfo', http_method='GET')
        self.site.handle_api_result(results)  # raises APIError on error
        
        return results
    
    def ask(self, query:str, title:str=None, limit:int=None):
        """
        Ask a query against Semantic MediaWiki.

        API doc: https://semantic-mediawiki.org/wiki/Ask_API

        The query is devided into multiple subqueries if the results of the query exeed the defined threshold.
        If this happens the query is executed multiple times to retrieve all results without passing the threshold.


        Args:
            query(str): SMW ask query to be executed
            title(str): title of query (optional)
            limit(int): the maximum number of results to be returned - 
                please note that SMW configuration will also limit results on the server side
        
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
        #kwargs = {}
        #if title is None:
        #    kwargs['title'] = title

        if limit is None:
            # if limit is not defined (via cmd-line), check if defined in query
            limit = SMW.getOuterMostArgumentValueOfQuery("limit", query)
        results = None
        if self.queryDivision == 1:
            try:
                results = self.askForAllResults(query, limit)
            except QueryResultSizeExceedException as e:
                print(e)
                results = e.getResults()
        else:
            results = self.askPartitionQuery(query, limit)
        for res in results:
            yield res

    def askPartitionQuery(self, query, limit=None):
        """
        Splits the query into multiple subqueries by determining the 'modification date' interval in which all results
        lie. This interval is then divided into subintervals. The number of subintervals is defined by the user via
        commandline. The results of all subqueries are then returned.
        Args:
            query(string): the SMW inline query to be send via api
            limit(string): limit of the query
        Returns:
            All results of the given query.
        """
        (start, end) = self.getBoundariesOfQuery(query)
        results = []
        if start is None or end is None:
            return results
        if self.showProgress:
            print(f"Start: {start}, End: {end}", file=sys.stderr, flush=True)
        numIntervals = self.queryDivision
        calcIntervalBound = lambda start, n: (start + n * lenSubinterval).replace(microsecond=0)
        calcLimit = lambda limit, numRes: None if limit is None else limit - numResults
        done = False
        numResults = 0
        while not done:
            lenSubinterval = (end - start) / numIntervals
            for n in range(numIntervals):
                if self.showProgress:
                    print(f"Query {n+1}/{numIntervals}:")
                tempLowerBound = calcIntervalBound(start,n)
                tempUpperBound = calcIntervalBound(start,n+1) if (n+1 < numIntervals) else end
                queryBounds = self.splitClause.queryBounds(tempLowerBound, tempUpperBound)
                queryParam=f"{query}|{queryBounds}"
                try:
                    tempRes = self.askForAllResults(queryParam, calcLimit(limit, numResults))
                    if tempRes is not None:
                        for res in tempRes:
                            results.append(res)
                            query_field=res.get("query")
                            if query_field is not None:
                                meta_field=query_field.get("meta")
                                if meta_field is not None:
                                    numResults += int(meta_field.get("count"))
                except QueryResultSizeExceedException as e:
                    # Too many results for current subinterval n -> print error and return the results upto this point
                    print(e)
                    if e.getResults():
                        for res in e.getResults():
                            results.append(res)
                    numResults = 0
                    break
                if limit is not None and limit <= numResults:
                    if self.showProgress:
                        print(f"Defined limit of {limit} reached - ending querying")
                    done = True
                    break
            done=True
        return results
    
    def getTimeStampBoundary(self,queryparam,order):
        '''
        query according to a DATE e.g. MODIFICATION_DATE in the given order
        
        Args:
           
        '''
        queryparamBoundary = f"{queryparam}|order={order}"
        resultsBoundary = self.site.raw_api('ask', query=queryparamBoundary, http_method='GET')
        self.site.handle_api_result(resultsBoundary)
        deserializedResult=self.deserialize(resultsBoundary)
       
        deserializedValues=deserializedResult.values()
        date=self.splitClause.deserialize(deserializedValues)
        return date

    def getBoundariesOfQuery(self, query):
        """
        Retrieves the time interval, lower and upper bound, based on the modification date in which the results of the
        given query lie.
        Args:
            query(string): the SMW inline query to be send via api
        Returns:
            (Datetime, Datetime): Returns the time interval (based on modification date) in which all results of the
            query lie potentially the start end end might be None if an error occured or the input is invalid
        """
        first=self.splitClause.getFirst()
        queryparam = f"{query}|{first}"
        start=self.getTimeStampBoundary(queryparam,'asc')
        end=self.getTimeStampBoundary(queryparam,'desc')
        return (start,end)
    
    def askForAllResults(self, query, limit=None, kwargs={}):
        """
        Executes the query until all results are received of the given limit is reached.
        If the SMW results limit is reached before all results are retrieved the QueryResultSizeExceedException is raised.
        Args:
            query(string): the SMW inline query to be send via api
            limit(int): limit for the query results, None (default) for all results
            kwargs:
        Returns:
            query results
        Raises:
            QueryResultSizeExceedException: Raised if not all results can be retrieved
        """
        endShowProgress = lambda showProgress, c: print("\n" if not c % 80 == 0 else "") if showProgress else None
        offset = 0
        done = False
        count = 0
        res = []
        while not done:
            count += 1
            if self.showProgress:
                sep = "\n" if count % 80 == 0 else ""
                print(".", end=sep, flush=True)

            queryParam = u'{query}|offset={offset}'.format(query=query, offset=offset)
            if limit is not None:
                queryParam += "|limit={limit}".format(limit=limit)
            # print(f"QueryPram: {queryParam}")   #debug purposes
            results = self.site.raw_api('ask', query=queryParam, http_method='GET', **kwargs)
            self.site.handle_api_result(results)  # raises APIError on error
            continueOffset = results.get('query-continue-offset')
            if continueOffset is None:
                done = True
            else:
                if limit is not None and continueOffset >= limit:
                    done = True
                elif (results.get('query') is not None and not results.get('query').get('results')) or continueOffset < offset:
                    # contine-offset is set but result is empty
                    endShowProgress(self.showProgress, count)
                    res.append(results)
                    raise QueryResultSizeExceedException(result=res)
                if continueOffset < offset:
                    done = True
            offset = continueOffset
            res.append(results)
        endShowProgress(self.showProgress, count)
        return res
    
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
                singleResults=None
                if 'query' in singleResult:
                    if 'results' in singleResult['query']:
                        singleResults=singleResult['query']['results']
                if singleResults is not None:
                    if 'query' in result:
                        if 'results' in result['query']:
                            results=result['query']['results']
                            results.update(singleResults)
                        else:
                            result['query']['results']=singleResults
                    else:
                        result['query']={}
                        result['query']['results'] = singleResults
        return result
        
    def query(self,askQuery:str,title:str=None,limit:int=None):
        '''
        run query and return list of Dicts
        
        Args:
            askQuery(string): the SMW inline query to be send via api
            title(string): the title (if any)
            limit(int): the maximum number of records to be retrieved (if any)
            
        Return:
            list: List of Dicts
            
        '''
        rawresult=self.rawquery(askQuery, title, limit)
        lod=self.deserialize(rawresult)
        return lod

    def updateProgress(self, count):
        if self.showProgress:
            sep = "\n" if count % 80 == 0 else ""
            print(".", end=sep, flush=True)
    
class SMWBot(SMW):
    '''
    Semantic MediaWiki access using pywikibot library
    '''
    def __init__(self, site=None,prefix="/",showProgress=False,debug=False):
        super(SMWBot,self).__init__(site,prefix,showProgress=showProgress,debug=debug) 
        pass
    
    def submit(self, parameters):
        """ submit the request with the given parameters
        Args:
            parameters(list): the parameters to use for the SMW API request
        Returns:
            dict: the submit result"""
        if not "Request" in sys.modules:
            from pywikibot.data.api import Request
                
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


class QueryResultSizeExceedException(BaseException):
    """Raised if the results of a query can not completely be queried due to SMW result limits."""
    def __init__(self, result=[], message="Query can not completely be queried due to SMW result limits."):
        super().__init__(message)
        self.result=result

    def getResults(self):
        """ Returns the queried results before the exception was raised """
        return self.result


