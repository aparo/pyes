EC2 Discovery
=============

ec2 discovery allows to use the ec2 APIs to perform automatic discovery (similar to multicast in non hostile multicast environments). Here is a simple sample configuration:


.. code-block:: js


    cloud:
        aws:
            access_key: AKVAIQBF2RECL7FJWGJQ
            secret_key: vExyMThREXeRMm/b/LRzEB8jWwvzQeXgjqMX+6br
    
    discovery:
        type: ec2


The following are a list of settings (prefixed with **discovery.ec2**) that can further control the discovery:


========================  =============================================================================================================================================================================
 Setting                   Description                                                                                                                                                                 
========================  =============================================================================================================================================================================
**groups**                Either a comma separated list or array based list of (security) groups. Only instances with the provided security groups will be used in the cluster discovery.              
**host_type**             The type of host type to use to communicate with other instances. Can be one of **private_ip**, **public_ip**, **private_dns**, **public_dns**. Defaults to **private_ip**.  
**availability_zones**    Either a comma separated list or array based list of availability zones. Only instances within the provided availability zones will be used in the cluster discovery.        
**any_group**             If set to **false**, will require all security groups to be present for the instance to be used for the discovery. Defaults to **true**.                                     
========================  =============================================================================================================================================================================

Filtering by Tags
-----------------

The ec2 discovery can also filter machines to include in the cluster based on tags (and not just groups). The settings to use include the **discovery.ec2.tag.** prefix. For example, setting **discovery.ec2.tag.stage** to **dev** will only filter instances with a tag key set to **stage**, and a value of **dev**. Several tags set will require all of those tags to be set for the instance to be included.


