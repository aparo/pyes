.. _es-guide-reference-modules-discovery-ec2:

===
Ec2
===

ec2 discovery allows to use the ec2 APIs to perform automatic discovery (similar to multicast in non hostile multicast environments). Here is a simple sample configuration:


.. code-block:: js


    cloud:
        aws:
            access_key: AKVAIQBF2RECL7FJWGJQ
            secret_key: vExyMThREXeRMm/b/LRzEB8jWwvzQeXgjqMX+6br
    
    discovery:
        type: ec2


You'll need to install the **cloud-aws** plugin, by running **bin/plugin install cloud-aws** before (re)starting elasticsearch.


The following are a list of settings (prefixed with **discovery.ec2**) that can further control the discovery:


========================  =============================================================================================================================================================================
 Setting                   Description                                                                                                                                                                 
========================  =============================================================================================================================================================================
**groups**                Either a comma separated list or array based list of (security) groups. Only instances with the provided security groups will be used in the cluster discovery.              
**host_type**             The type of host type to use to communicate with other instances. Can be one of **private_ip**, **public_ip**, **private_dns**, **public_dns**. Defaults to **private_ip**.  
**availability_zones**    Either a comma separated list or array based list of availability zones. Only instances within the provided availability zones will be used in the cluster discovery.        
**any_group**             If set to **false**, will require all security groups to be present for the instance to be used for the discovery. Defaults to **true**.                                     
**ping_timeout**          How long to wait for existing EC2 nodes to reply during discovery. Defaults to 3s.                                                                                           
========================  =============================================================================================================================================================================

Filtering by Tags
=================

The ec2 discovery can also filter machines to include in the cluster based on tags (and not just groups). The settings to use include the **discovery.ec2.tag.** prefix. For example, setting **discovery.ec2.tag.stage** to **dev** will only filter instances with a tag key set to **stage**, and a value of **dev**. Several tags set will require all of those tags to be set for the instance to be included.


One practical use for tag filtering is when an ec2 cluster contains many nodes that are not running elasticsearch. In this case (particularly with high **ping_timeout** values) there is a risk that a new node's discovery phase will end before it has found the cluster (which will result in it declaring itself master of a new cluster with the same name - highly undesirable). Tagging elasticsearch ec2 nodes and then filtering by that tag will resolve this issue.


Region
======

The **cloud.aws.region** can be set to a region and will automatically use the relevant settings for both **ec2** and **s3**. The available values are: **us-east-1**, **us-west-1**, **ap-southeast-1**, **eu-west-1**.


Automatic Node Attributes
=========================

Though not dependent on actually using **ec2** as discovery (but still requires the cloud aws plugin installed), the plugin can automatically add node attributes relating to ec2 (for example, availability zone, that can be used with the awareness allocation feature). In order to enable it, set **cloud.node.auto_attributes** to **true** in the settings.
