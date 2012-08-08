.. _es-guide-reference-modules-http:

====
Http
====

The http module allows to expose *elasticsearch* :ref:`API <es-guide-reference-api>`  over HTTP.


The http mechanism is completely asynchronous in nature, meaning that there is no blocking thread waiting for a response. The benefit of using asynchronous communication for HTTP is solving the `C10k problem <http://en.wikipedia.org/wiki/C10k_problem>`_.  

When possible, consider using `HTTP keep alive <http://en.wikipedia.org/wiki/Keepalive#HTTP_Keepalive>`_  when connecting for better performance and try to get your favorite client not to do `HTTP chunking <http://en.wikipedia.org/wiki/Chunked_transfer_encoding>`_.  

Settings
========

The following are the settings the can be configured for HTTP:


=============================  ======================================================================================
 Setting                        Description                                                                          
=============================  ======================================================================================
**http.port**                  A bind port range. Defaults to **9200-9300**.                                         
**http.max_content_length**    The max content of an HTTP request. Defaults to **100mb**                             
**http.compression**           Support for compression when possible (with Accept-Encoding). Defaults to **false**.  
**http.compression_level**     Defines the compression level to use. Defaults to **6**.                              
=============================  ======================================================================================

It also shares the uses the common :ref:`network settings <es-guide-reference-modules-network>`.  

Disable HTTP
============

The http module can be completely disabled and not started by setting **http.enabled** to **false**. This make sense when creating non :ref:`data nodes <es-guide-reference-modules-node>`  which accept HTTP requests, and communicate with data nodes using the internal :ref:`transport <es-guide-reference-modules-transport>`.  

