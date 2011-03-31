=======
Network
=======

There are several modules within a Node that use network based configuration, for example, the :doc:`transport <./transport.html>`  and :doc:`http <./http.html>`  modules. Node level network settings allows to set common settings that will be shared among all network based modules (unless explicitly overridden in each module).


The **network.bind_host** setting allows to control the host different network components will bind on. By default, the bind host will be **anyLocalAddress** (typically **0.0.0.0** or **::0**).


The **network.publish_host** setting allows to control the host the node will publish itself within the cluster so other nodes will be able to connect to it. Of course, this can't be the **anyLocalAddress**, and by default, it will be the first non loopback address (if possible), or the local address.


The **network.host** setting is a simple setting to automatically set both **network.bind_host** and **network.publish_host** to the same host value.


Both settings allows to be configured with either explicit host address or host name. The settings also accept logical setting values explained in the following table:


==============================  ======================================================================================
 Logical Host Setting Value      Description                                                                          
==============================  ======================================================================================
**_local_**                     Will be resolved to the local ip address.                                             
**_nonloopback_**               The first non loopback address.                                                       
**_nonloopback:ipv4_**          The first non loopback IPv4 address.                                                  
**_nonloopback:ipv6_**          The first non loopback IPv6 address.                                                  
**_[netowrkInterface]_**        Resolves to the ip address of the provided network interface. For example **_en0_**.  
==============================  ======================================================================================

TCP Settings
============

Any component that uses TCP (like the HTTP, Transport and Memcached) share the following allowed settings:


=====================================  ==================================================================================================
 Setting                                Description                                                                                      
=====================================  ==================================================================================================
**network.tcp.no_delay**               Enable or disable tcp no delay setting. Defaults to **true**.                                     
**network.tcp.keep_alive**             Enable or disable tcp keep alive. By default not explicitly set.                                  
**network.tcp.reuse_address**          Should an address be reused or not. Defaults to **true** on none windows machines.                
**network.tcp.send_buffer_size**       The size of the tcp send buffer size (in size setting format). By default not explicitly set.     
**network.tcp.receive_buffer_size**    The size of the tcp receive buffer size (in size setting format). By default not explicitly set.  
=====================================  ==================================================================================================
