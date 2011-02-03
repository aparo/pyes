Admin Indices API
=================

This section describes administration APIs that revolve around indices. The following are the APIs:


=====================================================  ===========================================================================================================================
 API                                                    Description                                                                                                               
=====================================================  ===========================================================================================================================
:doc:`status <./status/index>`                         Retrieves the status of the indices.                                                                                       
:doc:`create_index <./create_index/index>`             Creates an index using optional settings.                                                                                  
:doc:`delete_index <./delete_index/index>`             Deletes an index.                                                                                                          
:doc:`aliases <./aliases/index>`                       Aliasing one or more index.                                                                                                
:doc:`update_settings <./update_settings/index>`       Allows to update settings of one or more indices, including changing the **number_of_replicas** and index has.             
:doc:`delete_mapping <./delete_mapping/index>`         Deletes a mapping type with all its data from an index.                                                                    
:doc:`put_mapping <./put_mapping/index>`               Register specific mapping definition for a specific type against one or more indices.                                      
:doc:`get_mapping <./get_mapping/index>`               Retrieves mapping definition of index or index/type.                                                                       
:doc:`flush <./flush/index>`                           Flush the state of the index (clears memory).                                                                              
:doc:`refresh <./refresh/index>`                       Refresh one or more (or all) indices making all operations performed against the index since the last refresh searchable.  
:doc:`gateway_snapshot <./gateway_snapshot/index>`     Explicitly perform a snapshot through the gateway of one or more indices (backup them).                                    
:doc:`optimize <./optimize/index>`                     Optimize one or more indices.                                                                                              
:doc:`open_close <./open_close/index>`                 Close and open an index.                                                                                                   
:doc:`analyze <./analyze/index>`                       Analyzes a custom text and produce its (tokens) results.                                                                   
:doc:`templates <./templates/index>`                   Templates allow to apply settings/mappings to new indices created.                                                         
=====================================================  ===========================================================================================================================
