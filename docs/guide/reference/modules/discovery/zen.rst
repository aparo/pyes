.. _es-guide-reference-modules-discovery-zen:

===
Zen
===

The zen discovery is the built in discovery module for elasticsearch and the default. It provides both multicast and unicast discovery as well being easily extended to support cloud environments. 


The zen discovery is integrated with other modules, for example, all communication between nodes is done using the :ref:`transport <es-guide-reference-modules-transport>`  module.



It is separated into several sub modules, which are explained below:


Ping
====

This is the process where a node uses the discovery mechanisms to find other nodes. There is support for both multicast and unicast based discovery (can be used in conjunction as well).


Multicast
---------

Multicast ping discovery of other nodes is done by sending one or more multicast requests where existing nodes that exists will receive and respond to. It provides the following settings with the **discovery.zen.ping.multicast** prefix:


=============  ============================================================================================================
 Setting        Description                                                                                                
=============  ============================================================================================================
**group**      The group address to use. Defaults to **224.2.2.4**.                                                        
**port**       The port to use. Defaults to **54328**.                                                                     
**ttl**        The ttl of the multicast message. Defaults to **3**.                                                        
**address**    The address to bind to, defaults to **null** which means it will bind to all available network interfaces.  
=============  ============================================================================================================

Multicast can be disabled by setting **multicast.enabled** to **false**.


Unicast
-------

The unicast discovery allows to perform the discovery when multicast is not enabled. It basically requires a list of hosts to use that will act as gossip routers. It provides the following settings with the **discovery.zen.ping.unicast** prefix:


===========  ===================================================================================================================================================
 Setting      Description                                                                                                                                       
===========  ===================================================================================================================================================
**hosts**    Either an array setting or a comma delimited setting. Each value is either in the form of **host:port**, or in the form of **host[port1-port2]**.  
===========  ===================================================================================================================================================

The unicast discovery uses the :ref:`transport <es-guide-reference-modules-transport>`  module to perform the discovery.


Master Election
===============

As part of the initial ping process a master of the cluster is either elected or joined to. This is done automatically. The **discovery.zen.ping_timeout** (which defaults to **3s**) allows to configure the election to handle cases of slow or congested networks (higher values assure less chance of failure). Note, this setting was changed from 0.15.1 onwards, prior it was called **discovery.zen.initial_ping_timeout**.


Nodes can be excluded from becoming a master by setting **node.master** to **false**. Note, once a node is a client node (**node.client** set to **true**), it will not be allowed to become a master (**node.master** is automatically set to **false**).


The **discovery.zen.minimum_master_nodes** allows to control the minimum number of master eligible nodes a node should "see" in order to operate within the cluster. Its recommended to set it to a higher value than 1 when running more than 2 nodes in the cluster.


Fault Detection
===============

There are two fault detection processes running. The first is by the master, to ping all the other nodes in the cluster and verify that they are alive. And on the other end, each node pings to master to verify if its still alive or an election process needs to be initiated. 


The following settings control the fault detection process using the **discovery.zen.fd** prefix:


===================  ============================================================================================
 Setting              Description                                                                                
===================  ============================================================================================
**ping_interval**    How often a node gets pinged. Defaults to **1s**.                                           
**ping_timeout**     How long to wait for a ping response, defaults to **30s**.                                  
**ping_retries**     How many ping failures / timeouts cause a node to be considered failed. Defaults to **3**.  
===================  ============================================================================================

External Multicast
==================

The multicast discovery also supports external multicast requests to discover nodes. The external client can send a request to the multicast IP/group and port, in the form of:


.. code-block:: js

    {
        "request" : {
            :ref:`cluster_name <es-guide-reference-modules-discovery>`  me <es-guide-reference-modules-discovery>`  "test_cluster"
        }
    }


And the response will be similar to node info response (with node level information only, including transport/http addresses, and node attributes):


.. code-block:: js

    {
        "response" : {
            "cluster_name" : "test_cluster",
            "transport_address" : "...",
            "http_address" : "...",
            "attributes" : {
                "..."
            }
        }
    }


Note, it can still be enabled, with disabled internal multicast discovery, but still have external discovery working by keeping **discovery.zen.ping.multicast.enabled** set to **true** (the default), but, setting **discovery.zen.ping.multicast.ping.enabled** to **false**.
