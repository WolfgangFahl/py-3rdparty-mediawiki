"""
Created on 2024-09-26

@author: wf
"""

import getpass
import os
import sys
import traceback
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from wikibot3rd.version import Version
from wikibot3rd.wikiuser import WikiUser

__version__ = Version.version
__date__ = Version.date
__updated__ = Version.updated
DEBUG = False


def main(argv=None):
    """
    WikiUser credential handling
    """
    if argv is None:
        argv = sys.argv[1:]

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = "%%(prog)s %s (%s)" % (
        program_version,
        program_build_date,
    )
    program_shortdesc = "WikiUser credential handling"
    user_name = "Wolfgang Fahl"

    program_license = f"""{program_shortdesc}

  Created by {user_name} on {str(__date__)}.
  Copyright 2020-2024 Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
"""

    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license, formatter_class=RawDescriptionHelpFormatter
        )
        parser.add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="count",
            help="set debug level [default: %(default)s]",
        )
        parser.add_argument("-e", "--email", dest="email", help="email of the user")
        parser.add_argument("-f", "--file", dest="filePath", help="ini-file path")
        parser.add_argument("-i", "--interactive", action="store_true")
        parser.add_argument("-l", "--url", dest="url", help="url of the wiki")
        parser.add_argument(
            "-L",
            "--lenient",
            dest="lenient",
            action="store_true",
            help="be lenient with missing fields",
        )
        parser.add_argument("-p", "--password", dest="password", help="password")
        parser.add_argument(
            "-s",
            "--scriptPath",
            dest="scriptPath",
            help="script path default: %(default)s)",
            default="",
        )
        parser.add_argument(
            "-u",
            "--user",
            dest="user",
            help="os user id default: %(default)s)",
            default=getpass.getuser(),
        )
        parser.add_argument(
            "-v",
            "--wikiVersion",
            dest="version",
            default="MediaWiki 1.39.1",
            help="version of the wiki default: %(default)s)",
        )
        parser.add_argument(
            "-V", "--version", action="version", version=program_version_message
        )
        parser.add_argument("-w", "--wikiId", dest="wikiId", help="wiki Id")
        parser.add_argument(
            "-y",
            "--yes",
            dest="yes",
            action="store_true",
            help="immediately store without asking",
        )
        parser.add_argument(
            "--smw", dest="is_smw", default="true", help="is this a semantic mediawiki?"
        )
        # Process arguments
        args = parser.parse_args(argv)
        argsDict = vars(args)
        wikiuser = WikiUser.ofDict(
            argsDict, encrypted=False, lenient=True, encrypt=False
        )
        wikiuser.interactiveSave(args.yes, args.interactive, args.filePath)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise (e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        if getattr(args, "debug", False):
            print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
