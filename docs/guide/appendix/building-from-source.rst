.. _es-guide-appendix-building-from-source:

====================
Building From Source
====================

*elasticsearch* codebase is hosted on `github <https://github.com/elasticsearch/elasticsearch>`_,  and its just a **fork** away. To get started with the code, start by either forking or cloning the repo. One can also just download the master code in either `zip <https://github.com/elasticsearch/elasticsearch/zipball/master>`_  or `tar.gz <https://github.com/elasticsearch/elasticsearch/tarball/master>`_.  

Once downloaded, building an elasticsearch distribution is simple. You'll need `Apache Maven <http://maven.apache.org/download.html>`_  
or see below for IDE integration. Then compile ElasticSearch via:

.. code-block:: js


    $ mvn package -DskipTests


If you are running it for the first time, go get a cup of coffee (or better yet, a beer), it will take some time to download all the dependencies *elasticsearch* has. Once finished, a full distribution of the elasticsearch will be created under **target/releases/**.


In order to use it, just get either the **deb** package, the **zip** or **tar.gz** installation, extract it, and fire up **elasticsearch -f**. You now have a fully functional master based *elasticsearch* version running.


Hacking
=======

Maven is supported by all major IDEs these days:

   * `IntelliJ IDEA <http://www.jetbrains.com/idea/features/ant_maven.html>`_     * `NetBeans <http://wiki.netbeans.org/Maven>`_     * `Eclipse <http://maven.apache.org/eclipse-plugin.html>`_  - You'll need a maven plugin