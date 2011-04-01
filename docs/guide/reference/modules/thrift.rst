.. _es-guide-reference-modules-thrift:

======
Thrift
======

The thrift transport module allows to expose the REST interface of elasticsearch using thrift. Thrift should provide better performance over http. Since thrift provides both the wire protocol and the transport, it should make using it simpler (thought its lacking on docs...).


Using thrift requires installing the **transport-thrift** plugin using **bin/plugin -install transport-thrift**.


The thrift `schema <http://github.com/elasticsearch/elasticsearch/blob/master/plugins/transport/thrift/elasticsearch.thrift>`_  can be used to generate thrift clients.


=====================  =============================================================================================================================================================================================
 Setting                Description                                                                                                                                                                                 
=====================  =============================================================================================================================================================================================
**thrift.type**        Can be either **threadpool** (not framed), **threadpool_framed** (framed), **nonblocking** (framed), and **hsha** (framed). Defaults to **threadpool** (the default on hbase and cassandra)  
**thrift.port**        The port to bind to. Defaults to 9500-9600                                                                                                                                                   
**thrift.protocol**    Either **compact** or **binary**. Defaults to **binary**                                                                                                                                     
=====================  =============================================================================================================================================================================================
