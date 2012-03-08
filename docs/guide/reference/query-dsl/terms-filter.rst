.. _es-guide-reference-query-dsl-terms-filter:

============
Terms Filter
============

Filters documents that have fields that match any of the provided terms (*not analyzed*). For example:


.. code-block:: js


    {
        "constant_score" : {
            "filter" : {
                "terms" : { "user" : ["kimchy", "elasticsearch"]}
            }
        }
    }


The **terms** filter is also aliased with **in** as the filter name for simpler usage.


Execution Mode
--------------

The way terms filter executes is by iterating over the terms provided and finding matches docs (loading into a bitset) and caching it. Sometimes, we want a different execution model that can still be achieved by building more complex queries in the DSL, but we can support them in the more compact model that terms filter provides.


The **execution** option now has the following options :


* **plain**: The default. Works as today. Iterates over all the terms, building a bit set matching it, and filtering. The total filter is cached (keyed by the terms).
* **bool**: Builds a bool filter wrapping each term in a term filter that is cached (the single term filter). The bool filter is optimized in this case since it bitwise or's the different term filter bitsets. The total filter is not cached by default in this case as it makes little sense to do so (each term on its own is cached).
* **and**: Builds an and filter wrapping each term in term filter that is cached. The total filter is not cached by default in this case. Most times, bool should be used as its faster thanks to its bitwise execution.

The "total" terms filter caching can still be explicitly controlled using the **_cache** option. Note the default value for it depends on the execution value.


For example:


.. code-block:: js


    {
        "constant_score" : {
            "filter" : {
                "terms" : { 
                    "user" : ["kimchy", "elasticsearch"],
                    "execution" : "bool"
                }
            }
        }
    }



Caching
=======

The result of the filter is automatically cached by default. The `_cache` can be set to `false` to turn it off.

