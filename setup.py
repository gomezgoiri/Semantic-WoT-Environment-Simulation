'''
Created on Sep 7, 2012

@author: tulvur

To install/reinstall/uninstall the project and its dependencies using pip:
     sudo pip install ./
     sudo pip install ./ --upgrade
     sudo pip uninstall netuse
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
                          'simpy',
                          'rdflib<3a',
                          'pymongo',
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