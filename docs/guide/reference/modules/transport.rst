.. _es-guide-reference-modules-transport:

=========
Transport
=========

The transport module is used for internal communication between nodes within the cluster. Each call that goes from one node to the other uses the transport module (for example, when an HTTP GET request is processed by one node, and should actually be processed by another node that holds the data).


The transport mechanism is completely asynchronous in nature, meaning that there is no blocking thread waiting for a response. The benefit of using asynchronous communication is first solving the `C10k problem <http://en.wikipedia.org/wiki/C10k_problem>`_,  as well as being the idle solution for scatter (broadcast) / gather operations such as search in ElasticSearch.


TCP Transport
=============

The TCP transport is an implementation of the transport module using TCP. It allows for the following settings:


===================================  =======================================================================================
 Setting                              Description                                                                           
===================================  =======================================================================================
**transport.tcp.port**               A bind port range. Defaults to **9300-9400**.                                          
**transport.tcp.connect_timeout**    The socket connect timeout setting (in time setting format). Defaults to **2s**.       
**transport.tcp.compress**           Set to **true** to enable compression (LZF) between all nodes. Defaults to **false**.  
===================================  =======================================================================================

It also shares the uses the common :ref:`network settings <es-guide-reference-modules-network>`.  

Local Transport
===============

This is a handy transport to use when running integration tests within the JVM. It is automatically enabled when using **NodeBuilder#local(true)**.


