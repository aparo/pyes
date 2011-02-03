Create Index
============

The create index API allows to instantiate an index. ElasticSearch provides support for multiple indices, including executing operations across several indices. Each index created can have specific settings associated with it.


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/'
    
    $ curl -XPUT 'http://localhost:9200/twitter/' -d '
    index :
        number_of_shards : 3
        number_of_replicas : 2
    '


The above second example curl shows how an index called **twitter** can be created with specific settings for it using `YAML <http://www.yaml.org>`. In this case, creating an index with 3 shards, each with 2 replicas. The index settings can also defined with `JSON <http://www.json.org:>` 

.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/' -d \
    '
    { 
        index : {
            number_of_shards : 3,
            number_of_replicas : 2
        }
    }
    '


Mappings
--------

The create index API allows to provide a set of one or more mappings:


.. code-block:: js

    curl -XPOST localhost:9200/test -d '
    {
        "settings" : {
            "number_of_shards" : 1
        },
        "mappings" : {
            "type1" : {
                "_source" : { "enabled" : false }
            }
        }
    }
    '


Index Settings
--------------

For more information regarding all the different index level settings that can be set when creating an index, please check the :doc:`index modules </elasticsearch/index_modules/index>` section.

