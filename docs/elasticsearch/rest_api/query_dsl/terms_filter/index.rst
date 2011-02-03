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


Optimization
------------

Note, if the terms tend to repeat in other **term** or **terms** filter, it is considered better to have a an **or** filter wrapping single **term** filters. 


Caching
-------

The result of the filter is automatically cached by default. The `_cache` can be set to `false` to turn it off.

