.. _es-guide-reference-api-admin-indices-put-mapping:

=========================
Admin Indices Put Mapping
=========================

The put mapping API allows to register specific mapping definition for a specific type.


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/tweet/_mapping' -d '
    {
        "tweet" : {
            "properties" : {
                "message" : {"type" : "string", "store" : "yes"}
            }
        }
    }
    '


The above example creates a mapping called **tweet** within the **twitter** index. The mapping simply defines that the **message** field should be stored (by default, fields are not stored, just indexed) so we can retrieve it later on using selective loading. 


More information on how to define type mappings can be found in the :ref:`mapping <es-guide-reference-mapping>`  section. 


Merging &amp; Conflicts
=======================

When an existing mapping already exists under the given type, the two mapping definitions, the one already defined, and the new ones are merged. The **ignore_conflicts** parameters can be used to control if conflicts should be ignored or not, by default, it is set to **false** which means conflicts are *not* ignored.


The definition of conflict is really dependent on the type merged, but in general, if a different core type is defined, it is considered as a conflict. New mapping definitions can be added to object types, and core type mapping can be upgraded to **multi_field** type.


Multi Index
===========

The put mapping API can be applied to more than one index with a single call, or even on **_all** the indices.


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/kimchy,elasticsearch/tweet/_mapping' -d '
    {
        "tweet" : {
            "properties" : {
                "message" : {"type" : "string", "store" : "yes"}
            }
        }
    }
    '

