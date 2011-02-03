Modules
=======

The modules section describes node level modules that can be configured. Node level modules are modules that are basically singletons on the node level, and different from :doc:`index modules <./../index_modules/index>` which are created on a per index or even per index shard level allowing them to be configured on the index level.


The following lists the available top level modules:


==========================================  ============================================================
 Module                                      Description                                                
==========================================  ============================================================
:doc:`Node <./node/index>`                  Generic, node level settings.                               
:doc:`Transport <./transport/index>`        Native communication layer between nodes.                   
:doc:`HTTP <./http/index>`                  HTTP based communication layer.                             
:doc:`Memcached <./memcached/index>`        Memcached based communication layer.                        
:doc:`Thrift <./thrift/index>`              Thrift based REST communication layer.                      
:doc:`Discovery <./discovery/index>`        Discovery of nodes and cluster state.                       
:doc:`Gateway <./gateway/index>`            Long term persistent storage of cluster meta data.          
:doc:`JMX <./jmx/index>`                    JMX monitoring.                                             
:doc:`Thread Pool <./threadpool/index>`     ThreadPool type and configuration.                          
:doc:`Indices <./indices/index>`            Indices level settings and configuration.                   
:doc:`Scripting <./scripting/index>`        Configuration and Execution of scripts in different langs.  
==========================================  ============================================================
