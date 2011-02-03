Mapping
=======

Mapping is the process of defining how a document should be mapped to the Search Engine, including its searchable characteristics. ElasticSearch allows for support of multiple typed mapping definitions registered with the same index, and different types registered with different indices.


Explicit mapping is defined on an index type level. By default, here isn't a need to define explicit mappings are they are automatically created and registered once new type or new field is introduced (with no performance overhead) and have sensible defaults. Only when the defaults need to be overridden then mappings should be set.


Attributes
----------

The following sections cover all the aspects of how mapping work:


=====================================================  ======================================================================================
 Section                                                Description                                                                          
=====================================================  ======================================================================================
:doc:`core_types <./core_types/index>`                 The basic types support when mapping a JSON document.                                 
:doc:`array_type <./array_type/index>`                 Mapping JSON array types.                                                             
:doc:`object_type <./object_type/index>`               Mapping JSON inner objects.                                                           
:doc:`root_object_type <./root_object_type/index>`     Mapping the root JSON object.                                                         
:doc:`id_field <./id_field/index>`                     Allow to control the automatically created **_id** field                              
:doc:`type_field <./type_field/index>`                 Allow to control the automatically created **_type** field                            
:doc:`boost_field <./boost_field/index>`               Allow to control the boosting of a document using an external value.                  
:doc:`source_field <./source_field/index>`             Allow to control the **_source** field storing the actual JSON indexed.               
:doc:`index_field <./index_field/index>`               Allows to control indexing the **_index** a document belongs to.                      
:doc:`analyzer_field <./analyzer_field/index>`         Allows to control the analyzer used for indexing based on a document field value      
:doc:`routing_field <./routing_field/index>`           Allows to control routing aspect of a doc.                                            
:doc:`parent_field <./parent_field/index>`             Allow to set a relationship from a child doc to its parent.                           
:doc:`all_field <./all_field/index>`                   Allows to automatically create an **_all** field that includes all the other fields.  
:doc:`geo_point <./geo_point/index>`                   Mapping that represents a geo point.                                                  
:doc:`ip <./ip/index>`                                 Mapping that represents an ipv4 field.                                                
:doc:`meta <./meta/index>`                             Additional custom meta data stored on the mapping level.                              
:doc:`attachment <./attachment/index>`                 A plugin extension to index **attachment** types.                                     
=====================================================  ======================================================================================
