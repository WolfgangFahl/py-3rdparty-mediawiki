# py-3rdparty-mediawiki (Wikipush Toolkit)
[![Join the discussion](https://img.shields.io/badge/Discussion-github-brightgreen)](https://github.com/WolfgangFahl/py-3rdparty-mediawiki/discussions)
[![pypi](https://img.shields.io/pypi/pyversions/py-3rdparty-mediawiki)](https://pypi.org/project/py-3rdparty-mediawiki/)
[![Github Actions Build](https://github.com/WolfgangFahl/py-3rdparty-mediawiki/actions/workflows/build.yml/badge.svg)](https://github.com/WolfgangFahl/py-3rdparty-mediawiki/actions/workflows/build.yml)
[![GitHub issues](https://img.shields.io/github/issues/WolfgangFahl/py-3rdparty-mediawiki.svg)](https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/WolfgangFahl/py-3rdparty-mediawiki.svg)](https://github.com/WolfgangFahl/py-3rdparty-mediawiki/issues/?q=is%3Aissue+is%3Aclosed)
[![PyPI Status](https://img.shields.io/pypi/v/py-3rdparty-mediawiki.svg)](https://pypi.python.org/pypi/py-3rdparty-mediawiki/)
[![API Docs](https://img.shields.io/badge/API-Documentation-blue)](https://WolfgangFahl.github.io/py-3rdparty-mediawiki/)
[![License](https://img.shields.io/github/license/WolfgangFahl/py-3rdparty-mediawiki.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![BITPlan](http://wiki.bitplan.com/images/wiki/thumb/3/38/BITPlanLogoFontLessTransparent.png/198px-BITPlanLogoFontLessTransparent.png)](http://www.bitplan.com)

Python wrapper for mwclient with improvements for 3rd party wikis. Also known as the **[Wikipush Toolkit](https://www.semantic-mediawiki.org/wiki/Wikipush_Toolkit)** — a set of tools for automating MediaWiki page content handling using Python and a command line, presented at SMWCon Fall 2020. Works with any MediaWiki wiki: SMW wikis are queried natively; non-SMW wikis are supported by faking SMW-style queries for categories, enabling page pushing from wikis without Semantic MediaWiki installed.

## Installation

```bash
pip install py-3rdparty-mediawiki
```

For MCP server support (for AI assistants):
```bash
pip install py-3rdparty-mediawiki[mcp]
```

## Examples

### wikipush

Copy pages between wikis:

```bash
wikipush -s smw -t test2 -q "[[Category:City]]|limit=5"
copying 4 pages from smw to test2
copying Demo:Tokyo ...✅
copying image File:SMW-Info-button.png ...✅
copying image File:Tokyo-Tsukishima-0011.jpg ...✅
copying Vienna ...✅
copying Warsaw ...✅
copying image File:6140285934 02e81b845f z.jpg ...✅
copying Demo:Würzburg ...✅
```

### wikiupload

Upload files to a wiki:

```bash
wikiupload -t test --files car.png
uploading 1 files to test
1/1 ( 100%): uploading car.png ...✅
```

### wikinuke

The default behavior is a dry run, listing whether the pages exist:

```bash
wikinuke -t test -p deleteMe1 deleteMe2 deleteMe3
deleting 3 pages in test (dry run)
1/3 (  33%): deleting deleteMe1 ...👍
2/3 (  67%): deleting deleteMe2 ...👍
3/3 ( 100%): deleting deleteMe3 ...👍
```

Use `-f` to force actual deletion:

```bash
wikinuke -t test -p deleteMe1 deleteMe2 deleteMe3 -f
deleting 3 pages in test (forced)
1/3 (  33%): deleting deleteMe1 ...✅
2/3 (  67%): deleting deleteMe2 ...✅
3/3 ( 100%): deleting deleteMe3 ...✅
```

### wikiedit

Search and replace content in wiki pages:

```bash
wikiedit -t test -q "[[isA::CFP]]" --search "CALL FOR PAPER" --replace "CFP"
editing 1 pages in test (dry run)
1/1 ( 100%): editing CALL FOR PAPER Journal: Advances in Multimedia ... 👍
```

### wikiuser

Configure wiki credentials interactively:

```bash
wikiuser
email: john@doe.com
scriptPath: /w
user: jd
url: http://www.semantic-mediawiki.org
version: Mediawiki 1.33
wikiId: smw
password: ****
shall i store jd smw? yes/no y/n
```

## Links
* [Python](https://www.python.org/)
* [mwclient](https://github.com/mwclient/mwclient)
* [pyLoDStorage](https://github.com/WolfgangFahl/pyLoDStorage)
* [Wikipush Toolkit — SMWCon Fall 2020 talk](https://www.semantic-mediawiki.org/wiki/Wikipush_Toolkit)
* [SMWCon Fall 2020](https://www.semantic-mediawiki.org/wiki/SMWCon_Fall_2020)
* [PyPI](https://pypi.org/project/py-3rdparty-mediawiki/)
* [API Documentation](https://WolfgangFahl.github.io/py-3rdparty-mediawiki/)

## Documentation
[Wiki](https://wiki.bitplan.com/index.php/Py-3rdparty-mediawiki)
