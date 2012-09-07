'''
Created on Sep 7, 2012

@author: tulvur

sudo pip install ./
sudo pip install ./ --upgrade
sudo pip uninstall netuse
'''
from setuptools import setup, find_packages

setup(name="netuse",
      version="0.1",
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
                          #'matplotlib',
                          ],
      #license = "Apache",
      keywords = "webOfThings wot semanticWeb distribution internetOfThings iot",
      #url = "",
      entry_points = {
       'console_scripts': [
           'parametrize = netuse.main.parametrize:main',
           'parametrize.create = netuse.main.parametrize:create',
           'parametrize.delete = netuse.main.parametrize:delete',
           'simulate = netuse.main.simulate:main',
        ],
      }
      #zip_safe=False
)