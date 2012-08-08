.. _es-guide-reference-mapping-conf-mappings:

=============
Conf Mappings
=============

Creating new mappings can be done using the **put_mapping** API. When a document is indexed with no mapping associated with it in the specific index, the :ref:`dynamic / default mapping <es-guide-reference-mapping-dynamic-mapping>`  feature will kick in and automatically create mapping definition for it.


Mappings can also be provided on the node level, meaning that each index created will automatically be started with all the mappings defined within a certain location.


Mappings can be defined within files called **[mapping_name].json** and be placed either under **config/mappings/_default** location, or under **config/mappings/[index_name]** (for mappings that should be associated only with a specific index).

