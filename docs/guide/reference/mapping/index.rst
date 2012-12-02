.. _es-guide-reference-mapping-index:
.. _es-guide-reference-mapping:

=======
Mapping
=======

Mapping is the process of defining how a document should be mapped to the Search Engine, including its searchable characteristics such as which fields are searchable and if/how they are tokenized. In ElasticSearch, an index may store documents of different "mapping types". ElasticSearch allows one to associate multiple mapping definitions for each mapping type.


Explicit mapping is defined on an index/type level. By default, there isn't a need to define an explicit mapping, since one is automatically created and registered when a new type or new field is introduced (with no performance overhead) and have sensible defaults. Only when the defaults need to be overridden must a mapping definition be provided.


Mapping Types
-------------

Mapping types are a way to try and divide the documents indexed into the same index into logical groups. Think of it as tables in a database. Though there is separation between types, it's not a full separation (all end up as a document within the same Lucene index).


Field names with the same name across types are highly recommended to have the same type and same mapping characteristics (analysis settings for example). There is an effort to allow to explicitly "choose" which field to use by using type prefix (**my_type.my_field**), but its not complete, and there are places where it will never work (like faceting on the field).


In practice though, this restriction is almost never an issue. The field name usually ends up being a good indication to its "typeness" (e.g. "first_name" will always be a string). Note also, that this does not apply to the cross index case.


Mapping API
-----------

To create a mapping, you will need the :ref:`Put Mapping API <es-guide-reference-api-admin-indices-put-mapping>`,  or you can add multiple mappings when you :ref:`create an index <es-guide-reference-api-admin-indices-create-index>`.  

.. toctree::
    :maxdepth: 1

    all-field
    analyzer-field
    array-type
    attachment-type
    boost-field
    conf-mappings
    core-types
    date-format
    dynamic-mapping
    geo-point-type
    id-field
    index-field
    ip-type
    meta
    multi-field-type
    nested-type
    object-type
    parent-field
    root-object-type
    routing-field
    size-field
    source-field
    timestamp-field
    ttl-field
    type-field
    uid-field