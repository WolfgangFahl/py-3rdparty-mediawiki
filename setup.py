# ! important
# see https://stackoverflow.com/a/27868004/1497139
from setuptools import setup
from wikibot.version import Version
# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=Version.name,
    version=Version.version,

    packages=['wikibot',],
    classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            #'Programming Language :: Python :: 3.11'
    ],

    install_requires=[
      'gitpython',
      'jinja2',
      'pywikibot~=7.3',
      'pycryptodome~=3.15.0',
      'mwclient~=0.10.1',
      'mwparserfromhell~=0.6.4',
      'wikitextparser~=0.47.5'
    ],
    entry_points={
      'console_scripts': [
        'wikibackup = wikibot.wikipush:mainBackup',
        'wikiedit = wikibot.wikipush:mainEdit',
        'wikinuke = wikibot.wikipush:mainNuke',
        'wikipush = wikibot.wikipush:mainPush',
        'wikiquery = wikibot.wikipush:mainQuery',
        'wikiupload = wikibot.wikipush:mainUpload',
        'wikirestore = wikibot.wikipush:mainRestore',
        'wikiuser = wikibot.wikiuser:main',
      ],
    },
    author='Wolfgang Fahl',
    maintainer='Wolfgang Fahl',
    url='https://github.com/WolfgangFahl/py-3rdparty-mediawiki',
    license='Apache License',
    description='Wrapper for pywikibot with improvements for 3rd party wikis',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
