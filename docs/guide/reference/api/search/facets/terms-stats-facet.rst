.. _es-guide-reference-api-search-facets-terms-stats-facet:

=================
Terms Stats Facet
=================

The **terms_stats** facet combines both the :ref:`terms <es-guide-reference-api-search-facets-terms-facet>`  and :ref:`statistical <es-guide-reference-api-search-facets-statistical-facet>`  allowing to compute stats computed on a field, per term value driven by another field. For example:


.. code-block:: js


    {
        "query" : {
            "match_all" : {  }
        },
        "facets" : {
            "tag_price_stats" : {
                "terms_stats" : {
                    "key_field" : "tag",
                    "value_field" : "price"
                }
            }
        }
    }


The **size** parameter controls how many facet entries will be returned. It defaults to **10**. Setting it to 0 will return all terms matching the hits (be careful not to return too many results).


Ordering is done by setting **order**, with possible values of **term**, **reverse_term**, **count**, **reverse_count**, **total**, **reverse_total**, **min**, **reverse_min**, **max**, **reverse_max**, **mean**, **reverse_mean**. Defaults to **count**.


The value computed can also be a script, using the **value_script** instead of **value_field**, in which case the **lang** can control its language, and **params** allow to provide custom parameters (as in other scripted components).


Note, the terms stats can work with mutli valued key fields, or multi valued value fields, but not when both are multi valued (as ordering is not maintained).
