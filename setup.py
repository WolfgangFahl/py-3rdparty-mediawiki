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
    version='0.2.1',

    packages=['wikibot',],

    install_requires=[
      'gitpython',
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
        'wikiupload = wikibot.wikipush:mainUpload',
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
