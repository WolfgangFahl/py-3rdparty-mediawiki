"""
Created on 2024-09-26

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
                "version": "MediaWiki 1.43.6",
            },
            "cr": {
                "email": "noreply@nouser.com",
                "url": "https://cr.bitplan.com",
                "scriptPath": "",
                "version": "MediaWiki 1.35.5",
            },
            "wiki": {
                "email": "noreply@nouser.com",
                "url": "https://wiki.bitplan.com",
                "scriptPath": "",
                "version": "MediaWiki 1.39.7",
            },
            "genealogy": {
                "email": "noreply@nouser.com",
                "url": "https://wiki.genealogy.net",
                "scriptPath": "/",
                "version": "MediaWiki 1.35.11",
                "is_smw": False,
            },
            "wikipedia_en": {
                "email": "noreply@nouser.com",
                "url": "https://en.wikipedia.org",
                "scriptPath": "/w",
                "version": "MediaWiki 1.44.0",
                "is_smw": False,
            },
        }
        return configs
