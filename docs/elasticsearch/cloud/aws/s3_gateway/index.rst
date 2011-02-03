S3 Gateway
==========

s3 based gateway allows to do long term reliable async persistency of the index directly to Amazon s3. Here is how it can be configured:


.. code-block:: js


    cloud:
        aws:
            access_key: AKVAIQBF2RECL7FJWGJQ
            secret_key: vExyMThREXeRMm/b/LRzEB8jWwvzQeXgjqMX+6br
    
    
    gateway:
        type: s3
        s3:
            bucket: bucket_name


The following are a list of settings (prefixed with **gateway.s3**) that can further control the s3 gateway:


================  ============================================================================================================================
 Setting           Description                                                                                                                
================  ============================================================================================================================
**chunk_size**    Big files are broken down into chunks (to overcome AWS 5g limit and use concurrent snapshotting). Default set to **100m**.  
================  ============================================================================================================================
