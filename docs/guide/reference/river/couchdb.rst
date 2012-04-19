.. _es-guide-reference-river-couchdb:

=======
Couchdb
=======

The CouchDB River allows to automatically index couchdb and make it searchable using the excellent `_changes <http://guide.couchdb.org/draft/notifications.html>`_  stream couchdb provides. Setting it up is as simple as executing the following against elasticsearch:


.. code-block:: js

    curl -XPUT 'localhost:9200/_river/my_db/_meta' -d '{
        "type" : "couchdb",
        "couchdb" : {
            "host" : "localhost",
            "port" : 5984,
            "db" : "my_db",
            "filter" : null
        },
        "index" : {
            "index" : "my_db",
            "type" : "my_db",
            "bulk_size" : "100",
            "bulk_timeout" : "10ms"
        }
    }'


This call will create a river that uses the **_changes** stream to index all data within couchdb. Moreover, any "future" changes will automatically be indexed as well, making your search index and couchdb synchronized at all times.


The couchdb river is provided as a plugin and can be installed using **plugin -install river-couchdb**.


On top of that, in case of a failover, the couchdb river will automatically be started on another elasticsearch node, and continue indexing from the last indexed seq.


Bulking
=======

Bulking is automatically done in order to speed up the indexing process. If within the specified **bulk_timeout** more changes are detected, changes will be bulked up to **bulk_size** before they are indexed.


Filtering
=========

The `changes` stream allows to provide a filter with parameters that will be used by couchdb to filter the stream of changes. Here is how ti can be configured:


.. code-block:: js


    {
        "couchdb" : {
            "filter" : "test",
            "filter_params" : {
                "param1" : "value1",
                "param2" : "value2"
            }
        }
    }


Script Filters
==============

Filtering can also be performed by providing a script (default to JavaScript) that will further process each changed item within the changes stream. The json provided to the script is under a var called `ctx` with the relevant seq stream change (for example, `ctx.doc` will refer to the document, or `ctx.deleted` is the flag if its deleted or not).


Note, this feature requires the `lang-javascript` plugin.


The `ctx.doc` can be changed and its value can will be indexed (assuming its not a deleted change). Also, if `ctx.ignore` is set to true, the change seq will be ignore and not applied.


Here is an example setting that adds `field1` with value `value1` to all docs:


.. code-block:: js


    {
        "type" : "couchdb",
        "couchdb" : {
            "script" : "ctx.doc.field1 = 'value1'"
        }
    }

