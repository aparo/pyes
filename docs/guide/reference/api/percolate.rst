.. _es-guide-reference-api-percolate:

=========
Percolate
=========

The percolator allows to register queries against an index, and then send **percolate** requests which include a doc, and getting back the queries that match on that doc out of the set of registered queries.


Think of it as the reverse operation of indexing and then searching. Instead of sending docs, indexing them, and then running queries. One sends queries, registers them, and then sends docs and finds out which queries match that doc.


As an example, a user can register an interest (a query) on all tweets that contain the word "elasticsearch". For every tweet, one can percolate the tweet against all registered user queries, and find out which ones matched.


Here is a quick sample, first, lets create a **test** index:


.. code-block:: js

    curl -XPUT localhost:9200/test


Next, we will register a percolator query with a specific name called **kuku** against the **test** index:


.. code-block:: js

    curl -XPUT localhost:9200/_percolator/test/kuku -d '{
        "query" : {
            "term" : {
                "field1" : "value1"
            }
        }
    }'


And now, we can percolate a document and see which queries match on it (note, its not really indexed!):


.. code-block:: js

    curl -XGET localhost:9200/test/type1/_percolate -d '{
        "doc" : {
            "field1" : "value1"
        }
    }'


And the matches are part of the response:


.. code-block:: js

    {"ok":true, "matches":["kuku"]}


You can unregister the previous percolator query with the same API you use to delete any document in an index:


.. code-block:: js

    curl -XDELETE localhost:9200/_percolator/test/kuku


Filtering Executed Queries
==========================

Since the registered percolator queries are just docs in an index, one can filter the queries that will be used to percolate a doc. For example, we can add a **color** field to the registered query:


.. code-block:: js

    curl -XPUT localhost:9200/_percolator/test/kuku -d '{
        "color" : "blue",
        "query" : {
            "term" : {
                "field1" : "value1"
            }
        }
    }'


And then, we can percolate a doc that only matches on blue colors:


.. code-block:: js

    curl -XGET localhost:9200/test/type1/_percolate -d '{
        "doc" : {
            "field1" : "value1"
        },
        "query" : {
            "term" : {
                "color" : "blue"
            }
        }
    }'


How it Works
============

The **_percolator** which holds the repository of registered queries is just a another index. The query is registered under a concrete index that exists (or will exist). That index name is represented as the type in the **_percolator** index (a bit confusing, I know...).


The fact that the queries are stored as docs in another index (**_percolator**) gives us both the persistency nature of it, and the ability to filter out queries to execute using another query.


The **_percolator** index uses the **index.auto_expand_replica** setting to make sure that each data node will have access locally to the registered queries, allowing for fast query executing to filter out queries to run against a percolated doc.


The percolate API uses the whole number of shards as percolating processing "engines", both primaries and replicas. In our above case, if the **test** index has 2 shards with 1 replica, 4 shards will round robing in handing percolate requests. (dynamically) increasing the number of replicas will increase the number of percolation power.


Note, percolate request will prefer to be executed locally, and will not try and round robin across shards if a shard exists locally on a node that received a request (for example, from HTTP). Its important to do some roundrobin in the client code among nodes (in any case its recommended). If this behavior is not desired, the **prefer_local** parameter can be set to **false** to disable it.

