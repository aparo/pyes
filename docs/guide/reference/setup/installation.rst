.. _es-guide-reference-setup-installation:

============
Installation
============

After :ref:`downloading <es-guide-reference-setup-download>`  the latest release and extracting it, *elasticsearch* can be started using:


.. code-block:: bash


    $ bin/elasticsearch


Under Unix system, the command will start the process in the background. To run it in the foreground, add the -f switch to it:

.. code-block:: bash


    $ bin/elasticsearch -f


ElasticSearch is built using Java, and requires `Java 6 <http://java.sun.com/javase/downloads/index.jsp>`_  in order to run. The version of Java that will be used can be set by setting the **JAVA_HOME** environment variable.

Environment Variables
=====================

Within the scripts, ElasticSearch comes with built in **JAVA_OPTS** passed to the JVM started. The most important setting for that is the **-Xmx** to control the maximum allowed memory for the process, and **-Xms** to control the minimum allocated memory for the process (in general, the more memory allocated to the process, the better).


Most times it is better to leave the default **JAVA_OPTS** as they are, and use the **ES_JAVA_OPTS** environment variable in order to set / change JVM settings or arguments.


The **ES_HEAP_SIZE** environment variable allows to set the heap memory that will be allocated to elasticsearch java process. It will allocate the same value to both min and max values, though those can be set explicitly (not recommended) by setting **ES_MIN_MEM** (defaults to **256m**), and **ES_MAX_MEM** (defaults to **1gb**).


It is recommended to set the min and max memory to the same value, and enable **mlockall** see later.


UNIX
----

There are added features when using the **elasticsearch** shell script. The first, which was explained earlier, is the ability to easily run the process either in the foreground or the background.


Another feature is the ability to pass **-X** and **-D** directly to the script. When set, both override anything set using either **JAVA_OPTS** or **ES_JAVA_OPTS**. For example:


.. code-block:: bash


    $ bin/elasticsearch -f -Xmx2g -Xms2g -Des.index.storage.type=memory


Important Configurations
========================

File Descriptors
----------------

Make sure to increase the number of open files descriptors on the machine (or for the user running elasticsearch). Setting it to 32k or even 64k is recommended.


In order to test how many open files the process can open, start it with **-Des.max-open-files** set to **true**. This will print the number of open files the process can open on startup.


Memory Settings
---------------

 There is an option to use `mlockall <http://opengroup.org/onlinepubs/007908799/xsh/mlockall.html>`_  to try and lock the process address space so it won't be swapped. For this to work, the **bootstrap.mlockall** should be set to **true** and it is recommended to set both the min and max memory allocation to be the same. 


In order to see if this works or not, set the **common.jna** logging to DEBUG level. A solution to "Unknown mlockall error 0" can be to set **ulimit -l unlimited**.


Note, this is experimental feature, and might cause the JVM or shell session to exit if failing to allocate the memory (because not enough memory is available on the machine).


Running As a Service
====================

It should be simple to wrap the **elasticsearch** script in an **init.d** or the like. But, elasticsearch also supports running it using the `Java Service Wrapper <http://wrapper.tanukisoftware.com/>`_.  

ElasticSearch can be run as a service using the **elasticsearch** script located under **bin/service** location. The repo for it is located `here <http://github.com/elasticsearch/elasticsearch-servicewrapper>`_.  The script accepts a single parameter with the following values:


=============  ====================================================================
 Parameter      Description                                                        
=============  ====================================================================
**console**    Run the elasticsearch in the foreground.                            
**start**      Run elasticsearch int the background.                               
**stop**       Stops elasticsearch if its running.                                 
**install**    Install elasticsearch to run on system startup (init.d / service).  
**remove**     Removes elasticsearch from system startup (init.d / service).       
=============  ====================================================================

The service uses Java Service Wrapper which is a small native wrapper around the Java virtual machine which also monitors it.


Note, passing JVM level configuration (such as -X parameters) should be set within the **elasticsearch.conf** file. 


The **ES_MIN_MEM** and **ES_MAX_MEM** environment variables to set the minimum and maximum memory allocation for the JVM (set in mega bytes). It defaults to **256** and **1024** respectively.

