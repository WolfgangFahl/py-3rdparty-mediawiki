# ! important
# see https://stackoverflow.com/a/27868004/1497139
from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='py-3rdparty-mediawiki',
    version='0.4.11',

    packages=['wikibot',],
    classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
    ],

    install_requires=[
      'gitpython',
      'jinja2',
      'pywikibot',
      'pycrypto',
      'mwclient',
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
