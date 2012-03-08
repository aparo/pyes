.. _es-guide-reference-api-multi-get:

=========
Multi Get
=========

Multi GET API allows to get multiple documents based on an index, type (optional) and id (and possibly routing). The response includes a **doc** array with all the documents each element similar in structure to the get API. Here is an example:


.. code-block:: js

    curl 'localhost:9200/_mget' -d '{
        "docs" : [
            {
                "_index" : "test",
                "_type" : "type",
                "_id" : "1"
            },
            {
                "_index" : "test",
                "_type" : "type",
                "_id" : "2"
            }
        ]
    }'


The **mget** endpoint can also be used against an index (in which case its not required in the body):


.. code-block:: js

    curl 'localhost:9200/test/_mget' -d '{
        "docs" : [
            {
                "_type" : "type",
                "_id" : "1"
            },
            {
                "_type" : "type",
                "_id" : "2"
            }
        ]
    }'


And type:


.. code-block:: js

    curl 'localhost:9200/test/type/_mget' -d '{
        "docs" : [
            {
                "_id" : "1"
            },
            {
                "_id" : "2"
            }
        ]
    }'


In which case, the **ids** element can directly be used to simplify the request:


.. code-block:: js

    curl 'localhost:9200/test/type/_mget' -d '{
        "ids" : ["1", "2"]
    }'


Fields
------

Specific fields can be specified to be retrieved per document to get. For example:


.. code-block:: js

    curl 'localhost:9200/_mget' -d '{
        "docs" : [
            {
                "_index" : "test",
                "_type" : "type",
                "_id" : "1",
                "fields" : ["field1", "field2"]
            },
            {
                "_index" : "test",
                "_type" : "type",
                "_id" : "2",
                "fields" : ["field3", "field4"]
            }
        ]
    }'

