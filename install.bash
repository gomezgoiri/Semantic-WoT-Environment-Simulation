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


patch ./.virtualenvs/netuse/lib/python2.7/site-packages/rdflib-2.4.2-py2.7-linux-x86_64.egg/rdflib/syntax/parsers/n3p/n3meta.py ./.virtualenvs/netuse/src/netuse/patches/n3meta.py.diff
patch ./.virtualenvs/netuse/lib/python2.7/site-packages/FuXi/Syntax/InfixOWL.py ./.virtualenvs/netuse/src/netuse/patches/InfixOWL.py.patch


mkdir dev

svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/ -N dev/dataset
svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/base_ontologies/ dev/dataset/base_ontologies
svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/data/ dev/dataset/data