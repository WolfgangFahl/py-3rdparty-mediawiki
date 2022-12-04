'''
Created on 31.01.2021

@author: wf
'''
from lodstorage.query import Query
from jinja2 import Template,Environment
import html
import re

class Code(object):
    '''
    a piece of code
    '''
    
    def __init__(self, name:str,text:str,lang:str='python'):
        '''
        construct me from the given text and language
        '''
        self.name=name
        self.text=text
        self.lang=lang
        
    def execute(self,context):
        '''
        https://stackoverflow.com/questions/701802/how-do-i-execute-a-string-containing-python-code-in-python
        https://stackoverflow.com/questions/436198/what-is-an-alternative-to-execfile-in-python-3
        https://stackoverflow.com/questions/2220699/whats-the-difference-between-eval-exec-and-compile
        '''
        if self.lang == "jinja":
            self.executeTemplate(context)
        else:
            exec(self.text)
        pass

    def executeTemplate(self, context):
        """
        Renders the jinja-template with the query results placed in the given context and stores the result as wiki page.
        The name of the wiki page is either given through the template with set parameters.
        E.g.:
            {% set pagetitle = ""%}
            {% set pagetitle_prefix = "List of "%}
        If the pagetitle is empty, like in the example, the name variable of the query results is used as pagetitle.
        The pagetitle_prefix is added in all cases, if not defined a empty string is added.
        Assumption: self.text is a jinja template
        """
        getAttribute = lambda template, name : re.search("\{% *set +" + name + " += *['\"](?P<name>.*)['\"] *%\}",template).group("name")
        raw_template = LambdaAction.unescapeHTML(self.text)
        template = Template(raw_template)
        title = getAttribute(raw_template, "pagetitle")
        pagetitle_prefix = getAttribute(raw_template, "pagetitle_prefix")
        if not pagetitle_prefix:
            pagetitle_prefix=""
        user = context["wikiclient"].wikiUser.user
        for row in context["rows"]:
            page_content = template.render({"row": row, "smw": context["smw"]})
            if not title:
                if not row['name']:
                    raise ValueError(f"Can't save wikipage without a title. Either provide a page title in the "
                                     f"template or provide the name variable for each query result")
                pagetitle = pagetitle_prefix + row['name']
            else:
                pagetitle = pagetitle_prefix + title
            page = context['wikiclient'].getPage(pagetitle)
            # ToDo
            page.edit(page_content, f"Created with the template [[{self.name}]] by {user} through LambdaActions")


class LambdaAction(object):
    '''
    a lambda action
    '''

    def __init__(self, name:str,query:Query,code:Code):
        '''
        Constructor
        '''
        self.name=name
        self.query=query
        self.code=code
        
    def executeQuery(self,context):
        rows=None
        if self.query.lang == "sql":
            if "sqlDB" in context:
                db=context["sqlDB"]
                rows=db.query(self.query.query)
        elif self.query.lang == "sparql":
            # ToDo
            pass
        elif self.query.lang == "smw":
            if "smw" in context:
                smw = context["smw"]
                query = LambdaAction.unescapeHTML(self.query.query)
                query_results = smw.query(query)
                rows = list(query_results.values())
        else:
            print(f"Queries of type {self.query.lang} are currently not supported by LambdaActions.")
        context["rows"] = rows
        return rows
            
    def getMessage(self,context):
        message=None
        if 'result' in context:
            result=context['result']
            if 'message' in result:
                message=result["message"]
        return message
        
    def execute(self,context):
        '''
        run my query and feed the result into the given code
        
        Args:
            context(dict): a dictionary for the exchange of parameters
        '''
        self.executeQuery(context)
        self.code.execute(context)

    @staticmethod
    def unescapeHTML(value:str):
        """
        Unescapes received html value and removes html tags.
        Replaces:
            <br /> -> "\n"
            <pre> -> ""
        Args:
            value(str): html encoded string
        Returns:
            Returns the received value but without the html tags and unescaped.
        """
        if value.startswith("<pre>"):
            return html.unescape(value).replace("<br />", "\n")[5:][:-6]
        return value

