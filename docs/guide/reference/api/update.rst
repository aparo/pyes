.. _es-guide-reference-api-update:

======
Update
======

The update API allows to update a document based on a script provided. The operation gets the document (collocated with the shard) from the index, runs the script (with optional script language and parameters), and index back the result (also allows to delete, or ignore the operation). It uses versioning to make sure no updates have happened during the "get" and "reindex". (available from **0.19** onwards).


Note, this operation still means full reindex of the document, it just removes some network roundtrips and reduces chances of version conflicts between the get and the index. The **_source** field need to be enabled for this feature to work.


For example, lets index a simple doc:


.. code-block:: js

    curl -XPUT localhost:9200/test/type1/1 -d '{
        "counter" : 1,
        "tags" : ["red"]
    }'


Now, we can execute a script that would increment the counter:


.. code-block:: js

    curl -XPOST 'localhost:9200/test/type1/1/_update' -d '{
        "script" : "ctx._source.counter += count",
        "params" : {
            "count" : 4
        }
    }'


We can also add a tag to the list of tags (note, if the tag exists, it will still add it, since its a list):


.. code-block:: js

    curl -XPOST 'localhost:9200/test/type1/1/_update' -d '{
        "script" : "ctx._source.tags += tag",
        "params" : {
            "tag" : "blue"
        }
    }'


We can also add a new field to the document:


.. code-block:: js

    curl -XPOST 'localhost:9200/test/type1/1/_update' -d '{
        "script" : "ctx._source.text = \"some text\""
    }'


We can also remove a field from the document:


.. code-block:: js

    curl -XPOST 'localhost:9200/test/type1/1/_update' -d '{
        "script" : "ctx._source.remove(\"text\")"
    }'


And, we can delete the doc if the tags contain blue, or ignore (noop):


.. code-block:: js

    curl -XPOST 'localhost:9200/test/type1/1/_update' -d '{
        "script" : "ctx._source.tags.contains(tag) ? ctx.op = \"delete\" : ctx.op = \"none\"",
        "params" : {
            "tag" : "blue"
        }
    }'


The update operation supports similar parameters as the index API, including:


* **routing**: Sets the routing that will be used to route the document to the relevant shard.
* **parent**: Simply sets the routing.
* **timeout**: Timeout waiting for a shard to become available.
* **replication**: The replication type for the delete/index operation (sync or async).
* **consistency**: The write consistency of the index/delete operation.
* **percolate**: Enables percolation and filters out which percolator queries will be executed.
* **refresh**: Refresh the index immediately after the operation occurs, so that the updated document appears in search results immediately.

And also support **retry_on_conflict** which controls how many times to retry if there is a version conflict between getting the document and indexing / deleting it. Defaults to **0**.


It also allows to update the **ttl** of a document using **ctx._ttl** and timestamp using **ctx._timestamp**. Note that if the timestamp is not updated and not extracted from the **_source** it will be set to the update date.
