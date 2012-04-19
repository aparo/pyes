.. _es-guide-reference-setup-dir-layout:

==========
Dir Layout
==========

The directory layout of an installation is as follows:


========  =============================================================================  ========================  ===============
 Type      Description                                                                    Default Location          Setting       
========  =============================================================================  ========================  ===============
*home*    Home of elasticsearch installation                                                                       **path.home**  
*bin*     Binary scripts including **elasticsearch** to start a node                     **{path.home}/bin**                      
*conf*    Configuration files including **elasticsearch.yml**                            **{path.home}/config**    **path.conf**  
*data*    The location of the data files of each index / shard allocated on the node.    **{path.home}/data**      **path.data**  
*work*    Temporal files that are used by different nodes.                               **{path.home}/work**      **path.work**  
*logs*    Log files location                                                             **{path.home}/logs**      **path.logs**  
========  =============================================================================  ========================  ===============
