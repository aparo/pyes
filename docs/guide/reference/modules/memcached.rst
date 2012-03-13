.. _es-guide-reference-modules-memcached:

=========
Memcached
=========

The memcached module allows to expose *elasticsearch* :ref:`API <es-guide-reference-api>`  over the memcached protocol (as closely as possible). 


It is provided as a plugin called **transport-memcached** and installing is explained `here <https://github.com/elasticsearch/elasticsearch-transport-memcached>`_  . Another option is to download the memcached plugin and placing it under the **plugins** directory.


The memcached protocol supports both the binary and the text protocol, automatically detecting the correct one to use.


Mapping REST to Memcached Protocol
==================================

Memcached commands are mapped to REST and handled by the same generic REST layer in elasticsearch. Here is a list of the memcached commands supported:


GET

The memcached **GET** command maps to a REST **GET**. The key used is the URI (with parameters). The main downside is the fact that the memcached **GET** does not allow body in the request (and **SET** does not allow to return a result...). For this reason, most REST APIs (like search) allow to accept the "source" as a URI parameter as well.


SET

The memcached **SET** command maps to a REST **POST**. The key used is the URI (with parameters), and the body maps to the REST body.


DELETE
------

The memcached **DELETE** command maps to a REST **DELETE**. The key used is the URI (with parameters).


QUIT
----

The memcached **QUIT** command is supported and disconnects the client.


Settings
========

The following are the settings the can be configured for memcached:


====================  =================================================
 Setting               Description                                     
====================  =================================================
**memcached.port**    A bind port range. Defaults to **11211-11311**.  
====================  =================================================

It also shares the uses the common :ref:`network settings <es-guide-reference-modules-network>`.  

Disable memcached
=================

The memcached module can be completely disabled and not started using by setting **memcached.enabled** to **false**. By default it is enabled once it is detected as a plugin.

