"""
Created on 26.09.2024

@author: wf
"""


class WikiConfig:
    """
    Default Wiki Configurations which should be available in public CI
    """

    @classmethod
    def get_configs(cls):
        configs = {
            "smwcopy": {
                "email": "noreply@nouser.com",
                "url": "https://smw.bitplan.com/",
                "scriptPath": "",
                "version": "MediaWiki 1.35.5",
            },
            "smw": {
                "email": "webmaster@semantic-mediawiki.org",
                "url": "https://www.semantic-mediawiki.org",
                "scriptPath": "/w",
                "version": "MediaWiki 1.31.16",
            },
            "or": {
                "email": "noreply@nouser.com",
                "url": "https://www.openresearch.org",
                "scriptPath": "/mediawiki/",
                "version": "MediaWiki 1.31.1",
            },
            "orclone": {
                "email": "noreply@nouser.com",
                "url": "https://confident.dbis.rwth-aachen.de",
                "scriptPath": "/or/",
                "version": "MediaWiki 1.35.1",
            },
            "orcopy": {
                "email": "noreply@nouser.com",
                "url": "https://confident.dbis.rwth-aachen.de",
                "scriptPath": "/or/",
                "version": "MediaWiki 1.35.1",
            },
            "cr": {
                "email": "noreply@nouser.com",
                "url": "http://cr.bitplan.com",
                "scriptPath": "",
                "version": "MediaWiki 1.35.5",
            },
            "genealogy": {
                "email": "noreply@nouser.com",
                "url": "https://wiki.genealogy.net",
                "scriptPath": "/",
                "version": "MediaWiki 1.35.11",
            },
        }
        return configs
