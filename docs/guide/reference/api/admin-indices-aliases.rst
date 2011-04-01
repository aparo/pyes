.. _es-guide-reference-api-admin-indices-aliases:

=====================
Admin Indices Aliases
=====================

APIs in elasticsearch accept an index name when working against a specific index, and several indices when applicable. The index aliases API allow to alias an index with a name, with all APIs automatically converting the alias name to the actual index name. An alias can also be mapped to more than one index, and when specifying it, the alias will automatically expand to the aliases indices. 


Here is a sample of associating the alias **alias1** with index **test1**:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_aliases' -d '
    {
        "actions" : [
            { "add" : { "index" : "test1", "alias" : "alias1" } }
        ]
    }'


An alias can also be removed, for example:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_aliases' -d '
    {
        "actions" : [
            { "remove" : { "index" : "test1", "alias" : "alias1" } }
        ]
    }'


Renaming an index is a simple **remove** then **add** operation within the same API:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_aliases' -d '
    {
        "actions" : [
            { "remove" : { "index" : "test1", "alias" : "alias1" } },
            { "add" : { "index" : "test1", "alias" : "alias2" } }
        ]
    }'


Associating an alias with more then one index are simply several **add** actions:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_aliases' -d '
    {
        "actions" : [
            { "add" : { "index" : "test1", "alias" : "alias1" } },
            { "add" : { "index" : "test2", "alias" : "alias1" } }
        ]
    }'


It is an error to index to an alias which points to more than one index.

