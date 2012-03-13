.. _es-guide-reference-index-modules-analysis-mapping-charfilter:

==================
Mapping Charfilter
==================

A char filter of type **mapping** replacing characters of an analyzed text with given mapping.


Here is a sample configuration:


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "char_filter" : {
                    "my_mapping" : {
                        "type" : "mapping",
                        "mappings" : ["ph=>f", "qu=>q"]
                    }
                },
                "analyzer" : {
                    "custom_with_char_filter" : {
                        "tokenizer" : "standard",
                        "char_filter" : ["my_mapping"]
                    },
                }
            }
        }
    }


Otherwise the setting **mappings_path** can specify a file where you can put the list of char mapping :


.. code-block:: js

    ph => f
    qu => k

