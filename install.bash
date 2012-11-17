#!/bin/bash

export env_name=netuse
export virtualenv_path=~/.virtualenvs


mkvirtualenv $env_name
workon $env_name

sudo aptitude install python2.7-dev libfreetype6-dev

pip install simpy
easy_install -U "rdflib<3a"
pip install ez_setup
pip install fuxi
pip install pymongo
pip install mongoengine
pip install mock
pip install numpy
pip install matplotlib


pip install -e git+https://gomezgoiri@bitbucket.org/gomezgoiri/networkusage.git#egg=netuse


patch $virtualenv_path/$env_name/lib/python2.7/site-packages/rdflib-2.4.2-py2.7-linux-x86_64.egg/rdflib/syntax/parsers/n3p/n3meta.py $virtualenv_path/$env_name/src/netuse/patches/n3meta.py.diff


mkdir dev

svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/ -N dev/dataset
svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/base_ontologies/ dev/dataset/base_ontologies
svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/data/ dev/dataset/data