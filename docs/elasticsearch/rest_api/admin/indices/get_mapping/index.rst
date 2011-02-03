Get Mapping
===========

The get mapping API allows to retrieve mapping definition of index or index/type.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/_mapping'


The following is example output:

.. code-block:: js

    {
      "twitter" : {
        "tweet" : {
          "_boost" : {
            "name" : "_boost"
          },
          "dynamic" : true,
          "enabled" : true,
          "date_formats" : [ "dateOptionalTime", "yyyy/MM/dd HH:mm:ss||yyyy/MM/dd" ],
          "_source" : {
            "enabled" : true,
            "name" : "_source"
          },
          "_id" : {
            "store" : "no"
          },
          "path" : "full",
          "properties" : {
            "message" : {
              "omit_term_freq_and_positions" : false,
              "index_name" : "message",
              "index" : "analyzed",
              "omit_norms" : false,
              "store" : "no",
              "boost" : 1.0,
              "term_vector" : "no",
              "type" : "string"
            },
            "postDate" : {
              "omit_term_freq_and_positions" : true,
              "index_name" : "postDate",
              "index" : "not_analyzed",
              "omit_norms" : true,
              "store" : "no",
              "boost" : 1.0,
              "format" : "dateOptionalTime",
              "precision_step" : 4,
              "term_vector" : "no",
              "type" : "date"
            },
            "user" : {
              "omit_term_freq_and_positions" : false,
              "index_name" : "user",
              "index" : "analyzed",
              "omit_norms" : false,
              "store" : "no",
              "boost" : 1.0,
              "term_vector" : "no",
              "type" : "string"
            }
          },
          "_all" : {
            "enabled" : true,
            "store" : "no",
            "term_vector" : "no"
          },
          "type" : "object"
        }
      }
    }


Multiple Indices and Types
--------------------------

The get mapping API can be used to get more than one index or type mapping with a single call. General usage of the API follows the following syntax: **host:port/{index}/{type}/_mapping** where both **{index}** and **{type}** can stand for comma-separated list of names. To get mappings for all indices you can use **_all** for **{index}**. The following are some examples:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter,kimchy/_mapping'
    
    $ curl -XGET 'http://localhost:9200/_all/tweet,book/_mapping'


If you want to get mappings of all indices and types then the following two examples are equivalent:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_all/_mapping'
    
    $ curl -XGET 'http://localhost:9200/_mapping'

