.. _es-guide-reference-api-admin-indices-update-settings:

=============================
Admin Indices Update Settings
=============================

Change specific index level settings. The only setting supported is the **index.number_of_replicas** setting allowing to dynamically change the number of replicas an index has.


The REST endpoint is **/_settings** (to update all indices) or **{index}/_settings** to update one (or more) indices settings. The body of the request includes the updated settings, for example:


.. code-block:: js

    {
        "index" : {
            "number_of_replicas" : 4
        }
    }


The above will change the number of replicas to 4 from the current number of replicas. Here is a curl example:


.. code-block:: js

    curl -XPUT 'localhost:9200/my_index/_settings' -d '
    {
        "index" : {
            "number_of_replicas" : 4
        }
    }
    '

