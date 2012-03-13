.. _es-guide-reference-api-admin-indices-templates:

=======================
Admin Indices Templates
=======================

Index templates allow to define templates that will automatically be applied to new indices created. The templates include both settings and mappings, and a simple pattern template that controls if the template will be applied to the index created. For example:


.. code-block:: js

    curl -XPUT localhost:9200/_template/template_1 -d '
    {
        "template" : "te*",
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


Defines a template named template_1, with a template pattern of **te***. The settings and mappings will be applied to any index name that matches the **te*** template.


Deleting a Template
===================

Index templates are identified by a name (in the above case **template_1**) and can be delete as well:


.. code-block:: js

    curl -XDELETE localhost:9200/_template/template_1


GETting a Template
==================

Index templates are identified by a name (in the above case **template_1**) and can be retrieved using the following:


.. code-block:: js

    curl -XGET localhost:9200/_template/template_1


To get list of all index templates you can use :ref:`Cluster State <es-guide-reference-api-admin-cluster-state>`  API and check for the metadata/templates section of the response.


Multiple Template Matching
==========================

Multiple index templates can potentially match an index, in this case, both the settings and mappings are merged into the final configuration of the index. The order of the merging can be controlled using the **order** parameter, with lower order being applied first, and higher orders overriding them. For example:


.. code-block:: js

    curl -XPUT localhost:9200/_template/template_1 -d '
    {
        "template" : "*",
        "order" : 0,
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
    
    curl -XPUT localhost:9200/_template/template_2 -d '
    {
        "template" : "te*",
        "order" : 1,
        "settings" : {
            "number_of_shards" : 1
        },
        "mappings" : {
            "type1" : {
                "_source" : { "enabled" : true }
            }
        }
    }
    '


The above will disable storing the **_source** on all **type1** types, but for indices of that start with **te***, source will still be enabled. Note, for mappings, the merging is "deep", meaning that specific object/property based mappings can easily be added/overridden on higher order templates, with lower order templates providing the basis.


Config
======

Index templates can also be placed within the config location (**path.config**) under the **templates** directory (note, make sure to place them on all master eligible nodes). For example, a file called **template_1.json** can be placed under **config/templates** and it will be added if it matches an index. Here is a sample of a the mentioned file:


.. code-block:: js

    {
        "template_1" : {
            "template" : "*",
            "settings" : {
                "index.number_of_shards" : 2
            },
            "mappings" : {
                "_default_" : {
                    "_source" : {
                        "enabled" : false
                    }
                },
                "type1" : {
                    "_all" : {
                        "enabled" : false
                    }
                }
            }
        }
    }

