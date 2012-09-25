'''
Created on Sep 7, 2012

@author: tulvur

First of all, install the project and its dependencies using pip:
    sudo pip install ./
    sudo pip install ./ --upgrade
    sudo pip uninstall netuse

After installing, we should patch "n3meta.py" (issue related with n3 parsing)
    patch installation-path/rdflib/syntax/parsers/n3p/n3meta.py ./patches/n3meta.py.diff

Then, download the semantic files needed for the simulation.
Note that there is a folder with too much base-data not necessary.
To avoid downloading it, we mark the checkout as as not recursive (-N) and then we download just the needed folders. 
     svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/ -N [localfolder]/
     svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/base_ontologies/ [localfolder]/base_ontologies
     svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/data/ [localfolder]/data

Then, create a simbolic link to point from ~/dev/dataset to the actual location of the dataset:
     ln -s  path/[localfolder] ~/dev/dataset
'''
from setuptools import setup, find_packages

setup(name="netuse",
      version="0.2",
      description="An evaluation of our approach network usage",
      author="Aitor Gomez-Goiri",
      author_email="aitor.gomez@deusto.es",
      package_dir = {
        '': 'src',
      },
      packages = find_packages('src'),  # include all packages under src
      install_requires = [
                          'SimPy',
                          'rdflib<3a',
                          'mongoengine',
                          'mock', # http://www.voidspace.org.uk/python/mock/
                          'numpy',
                          'matplotlib',
                          ],
      #license = "Apache",
      keywords = "webOfThings wot semanticWeb distribution internetOfThings iot",
      #url = "",
      entry_points = {
       'console_scripts': [
           'parametrize = netuse.evaluation.number_requests.parametrize:main',
           'simulate = netuse.evaluation.simulate:main',
           'process_results = netuse.evaluation.number_requests.strategies.processor:main',
        ],
      }
      #zip_safe=False
)