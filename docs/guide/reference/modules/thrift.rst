.. _es-guide-reference-modules-thrift:

======
Thrift
======

The thrift transport module allows to expose the REST interface of elasticsearch using thrift. Thrift should provide better performance over http. Since thrift provides both the wire protocol and the transport, it should make using it simpler (thought its lacking on docs...).


Using thrift requires installing the **transport-thrift** plugin, located `here <https://github.com/elasticsearch/elasticsearch-transport-thrift>`_.  

The thrift `schema <https://github.com/elasticsearch/elasticsearch-transport-thrift/blob/master/elasticsearch.thrift>`_  can be used to generate thrift clients.


==================  ==============================================================================================================
 Setting             Description                                                                                                  
==================  ==============================================================================================================
**thrift.port**     The port to bind to. Defaults to 9500-9600                                                                    
**thrift.frame**    Defaults to **-1**, which means no framing. Set to a higher value to specify the frame size (like **15mb**).  
==================  ==============================================================================================================
