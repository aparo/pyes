===============
Dynamic Mapping
===============

Default mappings allow to automatically apply generic mapping definition to types that do not have mapping pre defined. This is mainly done thanks to the fact that the :doc:`object mapping <./object-type.html>`  and namely the :doc:`root object mapping <./root-object-type.html>`  allow for schema-less dynamic addition of unmapped fields.


The default mapping definition is plain mapping definition that is embedded within the distribution:


.. code-block:: js


    {
        "_default_" : {
        }
    }


Pretty short, no? Basically, everything is defaulted, especially the dynamic nature of the root object mapping. The default mapping definition can be overridden in several manners. The simplest manner is to simply define a file called **default-mapping.json** and placed it under the **config** directory (which can be configured to exist in a different location). It can also be explicitly set using the **index.mapper.default_mapping_location** setting.


The dynamic creation of mappings for unmapped types can be completely disabled by setting **index.mapper.dynamic** to **false**.


As an example, here is how we can change the default :doc:`date_formats <./date-format.html>`  used in the root and inner object types:


.. code-block:: js


    {
        "_default_" : {
            "date_formats" : ["yyyy-MM-dd", "dd-MM-yyyy", "date_optional_time"],
        }
    }

