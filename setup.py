# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

from setuptools import setup, find_packages

'''
To install/reinstall/uninstall the project and its dependencies using pip:
     sudo pip install ./
     sudo pip install ./ --upgrade
     sudo pip uninstall netuse
'''
setup(name="netuse",
      version="0.21",
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
                          'fuxi',
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
           'process.strat = netuse.evaluation.number_requests.strategies.processor:main',
           'diagram.strat = netuse.evaluation.number_requests.strategies.diagram:main',
           'del.execution_set = netuse.database.management.delete_execution_set:main',
           'del.execution = netuse.database.management.delete_execution:main',
           'dump.execution = netuse.database.management.dump_execution_into_file:main',
           'get.execution = netuse.database.management.get_execution_by_characteristics:main',           
        ],
      }
      #zip_safe=False
)