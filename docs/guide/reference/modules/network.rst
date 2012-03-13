.. _es-guide-reference-modules-network:

=======
Network
=======

There are several modules within a Node that use network based configuration, for example, the :ref:`transport <es-guide-reference-modules-transport>`  and :ref:`http <es-guide-reference-modules-http>`  modules. Node level network settings allows to set common settings that will be shared among all network based modules (unless explicitly overridden in each module).


The **network.bind_host** setting allows to control the host different network components will bind on. By default, the bind host will be **anyLocalAddress** (typically **0.0.0.0** or **::0**).


The **network.publish_host** setting allows to control the host the node will publish itself within the cluster so other nodes will be able to connect to it. Of course, this can't be the **anyLocalAddress**, and by default, it will be the first non loopback address (if possible), or the local address.


The **network.host** setting is a simple setting to automatically set both **network.bind_host** and **network.publish_host** to the same host value.


Both settings allows to be configured with either explicit host address or host name. The settings also accept logical setting values explained in the following table:


===============================  =============================================================================================
 Logical Host Setting Value       Description                                                                                 
===============================  =============================================================================================
**_local_**                      Will be resolved to the local ip address.                                                    
**_non_loopback_**               The first non loopback address.                                                              
**_non_loopback:ipv4_**          The first non loopback IPv4 address.                                                         
**_non_loopback:ipv6_**          The first non loopback IPv6 address.                                                         
**_[networkInterface]_**         Resolves to the ip address of the provided network interface. For example **_en0_**.         
**_[networkInterface]:ipv4_**    Resolves to the ipv4 address of the provided network interface. For example **_en0:ipv4_**.  
**_[networkInterface]:ipv6_**    Resolves to the ipv6 address of the provided network interface. For example **_en0:ipv6_**.  
===============================  =============================================================================================

When the **cloud-aws** plugin is installed, the following are also allowed as valid network host settings:


=======================  =================================================
 EC2 Host Value           Description                                     
=======================  =================================================
**_ec2:privateIpv4_**    The private IP address (ipv4) of the machine.    
**_ec2:privateDns_**     The private host of the machine.                 
**_ec2:publicIpv4_**     The public IP address (ipv4) of the machine.     
**_ec2:publicDns_**      The public host of the machine.                  
**_ec2_**                Less verbose option for the private ip address.  
**_ec2:privateIp_**      Less verbose option for the private ip address.  
**_ec2:publicIp_**       Less verbose option for the public ip address.   
=======================  =================================================

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
