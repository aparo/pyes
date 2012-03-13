.. _es-guide-reference-setup-dir-layout:

==========
Dir Layout
==========

The directory layout of an installation is as follows:


========  ==========================================================================================================  ========================  ===============
 Type      Description                                                                                                 Default Location          Setting       
========  ==========================================================================================================  ========================  ===============
*home*    Home of elasticsearch installation                                                                                                    **path.home**  
*bin*     Binary scripts including **elasticsearch** to start a node                                                  **{path.home}/bin**                      
*conf*    Configuration files including **elasticsearch.yml**                                                         **{path.home}/config**    **path.conf**  
*data*    The location of the data files of each index / shard allocated on the node. Can hold multiple locations.    **{path.home}/data**      **path.data**  
*work*    Temporal files that are used by different nodes.                                                            **{path.home}/work**      **path.work**  
*logs*    Log files location                                                                                          **{path.home}/logs**      **path.logs**  
========  ==========================================================================================================  ========================  ===============

The multiple data locations allows to stripe it. The striping is simple, placing whole files in one of the locations, and deciding where to place the file based on the location with greatest free space. Note, there is no multiple copies of the same data, in that, its similar to RAID 0. Though simple, it should provide a good solution for people that don't want to mess with raids and the like. Here is how it is configured:

**path.data: /mnt/first,/mnt/second**


Or the in an array format:

**path.data: ["/mnt/first", "/mnt/second"]**

