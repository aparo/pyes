Index Mapper Module
===================

The mapper module acts as a registry for the type mapping definitions added to an index using the :doc:`put mapping </elasticsearch/rest_api/admin/indices/put_mapping/index>`. It also handles the dynamic mapping support for types that have no explicit mappings pre defined. For more information about mapping definitions, check out the :doc:`mapping section </elasticsearch/mapping/index>`. 

Dynamic / Default Mappings
--------------------------

Dynamic mappings allow to automatically apply generic mapping definition to types that do not have mapping pre defined or applied to new mapping definitions (overridden). This is mainly done thanks to the fact that the :doc:`object mapping </elasticsearch/mapping/object_type/index>` and namely the :doc:`root object mapping </elasticsearch/mapping/root_object_type/index>` allow for schema less dynamic addition of unmapped fields.


The default mapping definition is plain mapping definition that is embedded within ElasticSearch:


.. code-block:: js


    {
        _default_ : {
        }
    }


Pretty short, no? Basically, everything is defaulted, especially the dynamic nature of the root object mapping. The default mapping definition can be overridden in several manners. The simplest manner is to simply define a file called **default-mapping.json** and placed it under the **config** directory (which can be configured to exist in a different location). It can also be explicitly set using the **index.mapper.default_mapping_location** setting.


Dynamic creation of mappings for unmapped types can be completely disabled by setting **index.mapper.dynamic** to **false**.



