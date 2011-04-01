.. _es-guide-appendix-building-from-source:

====================
Building From Source
====================

*elasticsearch* codebase is hosted on `github <http://github.com/elasticsearch/elasticsearch>`_,  and its just a **fork** away. To get started with the code, start by either forking or cloning the repo. One can also just download the master code in either `zip <https://github.com/elasticsearch/elasticsearch/zipball/master>`_  or `tar.gz <https://github.com/elasticsearch/elasticsearch/tarball/master>`_.  

Once downloaded, building an elasticsearch distribution is simple. From within the source, run:


.. code-block:: js


    $ ./gradlew


If you are running it for the first time, go get a cup of coffee (or better yet, a beer), it will take some time to download all the dependencies *elasticsearch* has. Once finished, a full distribution of the elasticsearch will be created under **build/distributions**.


In order to use it, just get either the **zip** or **tar.gz** installation, extract it, and fire up **elasticsearch -f**. You now have a fully functional master based *elasticsearch* version running.


Hacking
=======

*elasticsearch* comes with built in `IntelliJ IDEA <http://www.jetbrains.com/idea/>`_  project files. Just download the `community edition <http://www.jetbrains.com/idea/download/>`_,  fire it up, and import the project.


In order to get all the dependencies right, you will need to run **gradle** and also **gradle test** once to download all the dependencies.

