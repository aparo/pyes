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

The unicast discovery uses the :ref:`transport <es-guide-reference-transport>`  module to perform the discovery.


Master Election
===============

As part of the initial ping process a master of the cluster is either elected or joined to. This is done automatically. The **discovery.zen.ping_timeout** (which defaults to **3s**) allows to configure the election to handle cases of slow or congested networks (higher values assure less chance of failure). Note, this setting was changed from 0.15.1 onwards, prior it was called **discovery.zen.initial_ping_timeout**.


Nodes can be excluded from becoming a master by setting **zen.master** to **false**. Note, once a node is a client node (**node.client** set to **true**), it will not be allowed to become a master (**zen.master** is automatically set to **false**).


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
