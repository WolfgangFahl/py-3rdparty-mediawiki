"""
Created on 2022-03-24

@author: wf
"""

import wikibot3rd


class Version(object):
    """
    Version handling for py-3rdparty-mediawiki
    """

    name = "py-3rdparty-mediawiki"
    version = wikibot3rd.__version__
    date = "2020-10-31"
    updated = "2025-03-08"

    authors = "Wolfgang Fahl, Tim Holzheim"

    description = "Wrapper for mwclient with improvements for 3rd party wikis"

    cm_url = "https://github.com/WolfgangFahl/py-3rdparty-mediawiki"
    chat_url = "https://github.com/WolfgangFahl/py-3rdparty-mediawiki/discussions"
    doc_url = "https://wiki.bitplan.com/index.php/Py-3rdparty-mediawiki"

    license = f"""Copyright 2020-2025 contributors. All rights reserved.
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""
    longDescription = f"""{name} version {version}
{description}
  Created by {authors} on {date} last updated {updated}"""
