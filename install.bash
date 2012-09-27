#!/bin/bash

mkvirtualenv netuse
workon netuse


pip install simpy
easy_install -U "rdflib<3a"
pip install ez_setup
pip install fuxi
pip install pymongo
pip install mongoengine
pip install mock
pip install numpy
pip install matplotlib


pip install -e svn+https://dev.morelab.deusto.es/svn/aigomez/trunk/NetworkUsage/#egg=netuse


patch installation-path/rdflib/syntax/parsers/n3p/n3meta.py ./patches/n3meta.py.diff