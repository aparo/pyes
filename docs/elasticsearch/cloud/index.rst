Cloud
=====

ElasticSearch aim is to provide native cloud support for different cloud providers. The following cloud providers are supported:


===========================  =====================
 Cloud Provider               Description         
===========================  =====================
:doc:`aws <./aws/index>`     Amazon Web Services  
===========================  =====================

What does native mean? Lets try and analyze two pain points when running in the cloud, and how they are solved with elasticsearch:


Discovery
---------

One of the main problems with running distributed systems on the cloud is discovery. Products that can do "zero conf" discovery use multicast for it (elasticsearch among them), and in most cloud providers (Amazon AWS or Rackspace) multicast is disabled. The typical way to work around it is to use unicast discovery, which requires setting up a specific list of IPs/Hosts (routers or gossip servers).


Unicast discovery is problematic when used on the cloud. Machines can come and go, and their IP is not static. Cloud providers work around that by providing the ability to have a set of "elastic IPs". But, at the end, the management of the cloud installation becomes a pain. At least two servers must be associated with an elastic IP and become a special exception case which needs to be managed. This goes completely against "zero conf" discovery and heavily complicates the cloud installation.


ElasticSearch :doc:`zen <./../modules/discovery/zen/index>` discovery module was built from the ground up to work well in cloud environments (and integrate well with other elasticsearch modules). The cloud extension to it provides "zero conf" discovery in cloud environments.


In a nutshell, when running on the cloud, the list of machines that are already running on the cloud is available through cloud APIs. This information can be used to perform "zero conf" discovery. This follows the motto that the should be embraced by any system running on the cloud: _All Machines are Created Equal_.


So, how do you enabled cloud discovery on the cloud? With a few lines of configuration (using AWS EC2 as an example):


.. code-block:: js


    cloud:
        aws:
            access_key: AKVAIQBF2RECL7FJWGJQ
            secret_key: vExyMThREXeRMm/b/LRzEB8jWwvzQeXgjqMX+6br
    
    discovery:
        type: ec2


Gateway
-------

ElasticSearch has been designed to do reliable asynchronous long term persistency. This enables several features including the ability for fast local :doc:`runtime" storage (including in-memory) while having a long term storage that can be slower. The Gateway concept is described in the "Search Engine Time Machine <.//blog/2010/02/16/searchengine_time_machine.html/index>` post.


But first, a step back. When designing a system that would be deployed on the cloud, lets take a search engine for example ;), things come and go. One of those things that come and go are disks. So, local storage, in cloud environments, is considered transient. In Amazon AWS for example, EBS (Elastic Block Store) was introduced to provide a mountable disk that survives restarts. So, we could configure our search engine to store the index on EBS. But, EBS requires periodic snapshotting to S3 (amazon blob store) for "safe" persistency, since EBS can certainly suffer from failures as well. Of course, this means more money spent on your cloud deployment since now one pays for both EBS and S3.


One way to work around this is to persist directly from the local store to S3 by writing some sort of synchronization script / code. But, if the machines fails we will loose all the data up to the point when the script last ran. The next step is to add replication (and sharding for performance) and so on. All of this is provided by elasticsearch out of the box.


Here is how elasticsearch can be configured to store both its cluster metadata (to survive full cluster failure) and indices in the cloud (AWS s3 as an example):


.. code-block:: js


    cloud:
        aws:
            access_key: AKIAIQBF2RECL7FJWGJQ
            secret_key: vEXyMThREXeRMm/b/LRzEB8jWwvzQeXgjqMX+6br
    
    
    gateway:
        type: s3
        s3:
            bucket: bucket_name

