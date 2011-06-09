.. _es-guide-reference-mapping-index:
.. _es-guide-reference-mapping:

=======
Mapping
=======

Mapping is the process of defining how a document should be mapped to the Search Engine, including its searchable characteristics. ElasticSearch allows for support of multiple typed mapping definitions registered with the same index, and different types registered with different indices.


Explicit mapping is defined on an index type level. By default, there isn't a need to define explicit mappings as they are automatically created and registered once new type or new field is introduced (with no performance overhead) and have sensible defaults. Only when the defaults need to be overridden then mappings should be set.

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
    object-type
    parent-field
    root-object-type
    routing-field
    size-field
    source-field
    type-field
    uid-field