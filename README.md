Evaluation of _Energy-aware Architecture for Information Search..._
===================================================================

Evaluation of the paper entiled [Energy-aware Architecture for Information Search in the Semantic Web of Things](http://gomezgoiri.net/publications/gomezgoiri-energy.html).
This project has evolved during more than a year.
Consequently, it may be difficult to understand.
I did my best to make a neat design and now I'm really trying to clearly document it.
However, if after carefully reading the documentation and the source code, you don't understand something or you cannot run something, just mail me and I'll do my best to help you ;-)


Directory structure
-------------------

 * _src_ contains the source code of the different modules which compose this project.
  * _clueseval_ has the code and the evaluation for the _clues_
   * _clues_ has the code about this core data structure (i.e. utility methods, parsing and serializations)
   * _evaluation_ has the evaluation for the Section 6.1
  * _netuse_
   * _database_ contains the simulation results are persisted using [mongoDB](http://www.mongodb.org/). This module contains the data models stored through [mongoengine](http://mongoengine.org/).
   * _debugging_ (ignore it)
   * _evaluation_ has the parametrization and processing for the evaluations of sections 6.2 ( _number&#95;requests_ ), 6.3 ( _activity_ ) and 6.4 ( _dynamism_ )
   * _mdns_ has the code to simulate the [mDNS](http://tools.ietf.org/html/rfc6762) and [DNS-SD](http://www.ietf.org/rfc/rfc6763.txt) protocols
   * _tracers_ contains the code to write the simulated [HTTP](http://www.ietf.org/rfc/rfc2616.txt) and [UDP](http://www.ietf.org/rfc/rfc768.txt) traces in a file or in mongoDB
   * _triplespace_ contains the semantic management classes. It is called like that, because this project originally evolved from another used to assess different _Triple Space_ implementations. For more information, see [this paper](http://gomezgoiri.net/publications/gomezgoiri-assesing.html).
  * _commons_ has the code which is used by both _clueseval_ and _netuse_ modules
  * _testing_ has code used by the unit tests
 * _test_ contains the unit tests for the different modules of the project.


Installation
------------


### Short procedure

Use the bash script on the project's top directory:

    bash install.bash

### Manual procedure

First of all, install the project and its dependencies using pip:

 * Recommended option for development: checkout the code and edit it whenever you need
 
     pip install -e git+https://gomezgoiri@bitbucket.org/gomezgoiri/networkusage.git#egg=netuse
     
 * If you have already downloaded the code and you don't need to edit it, you can simply do...
 
     pip install ./
     
 * If a previous version was already installed use this:
 
     sudo pip install ./ --upgrade
     
And to uninstall it:

     sudo pip uninstall netuse


During the installation process, some dependencies won't be installed correctly.
While the setup.py is broken, install them manually:

     sudo pip install numpy
     sudo pip install simpy

After installing them, you should patch "n3meta.py" (issue related with n3 parsing) and "InfixOWL.py":

     patch [installation-path]/rdflib/syntax/parsers/n3p/n3meta.py ./patches/n3meta.py.diff
     patch [installation-path]/FuXi/Syntax/InfixOWL.py ./patches/InfixOWL.py.patch

Then, download the semantic files needed for the simulation.
Note that there is a subfolder with too much unnecessary base-data.
To avoid downloading it, mark the checkout as as not recursive (-N) and then just download the needed folders.

     svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/ -N [localfolder]/
     svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/base_ontologies/ [localfolder]/base_ontologies
     svn co https://dev.morelab.deusto.es/svn/aigomez/trunk/dataset/data/ [localfolder]/data

Then, create a symbolic link to point from ~/dev/dataset to the actual location of the dataset:

     ln -s  path/[localfolder] ~/dev/dataset


### Dependencies

The dependencies are described in the _setup.py_ file.
However, I have not used it in a while.
So, just in case, I've also added all the modules installed ( _pip freeze_ ) in the [virtualenvwrapper](https://bitbucket.org/dhellmann/virtualenvwrapper) environment I have been using to run the simulations.

These requirements can be found in the _requirements.txt_ file. 
To install them in you python environment, simply run:

    pip install -r requirements.txt


Configuration
-------------

 * Dataset:
     - By default, the dataset is supposed to be located in ~/dev/dataset.
     - However, all the entry points which need it, can receive a different path as a parameter (e.g. '-ds','--data-set).
 * Mongodb:
     - The database connection details can be changed in src/netuse/database/__init__.py


Usage
-----

Soon...



Tests
-----

To run any tests, just execute the desired one using:
     python test/[subfolder/]name.py


License
-------

Check _COPYING.txt_.
