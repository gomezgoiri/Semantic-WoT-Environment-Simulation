Project to assess the network usage of our proposed solution.


Installation
------------

First of all, install the project and its dependencies using pip:
  (Recommended option for development: checkout the code and edit it whenever you need)
	 pip install -e svn+https://dev.morelab.deusto.es/svn/aigomez/trunk/NetworkUsage/#egg=netuse
	 
  (If you have already download the code and don't need to edit it to be synchronized with the SVN)
     pip install ./
  (If a previous version was already installed use this:)
     sudo pip install ./ --upgrade
  (And to uninstall:)
     sudo pip uninstall netuse
     
During the installation process, some dependencies won't be installed correctly.
While the setup.py is fixed, install them manually:
     sudo pip install numpy
     sudo pip install simpy

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



Configuration
-------------

 * Dataset:
     - By default, the dataset is supposed to be in ~/dev/dataset.
     - Even though, all the entry points which need it should receive it as a parameter (e.g. '-ds','--data-set).
 * Mongodb:
     - The database connection can be changed in src/netuse/database/__init__.py


Usage
-----

Soon...



Tests
-----

To run any tests, just execute the desired one using:
     python test/[subfolder/]name.py