.. _es-guide-reference-query-dsl-text-query:

==========
Text Query
==========

A family of **text** queries that accept text, analyzes it, and constructs a query out of it. For example:


.. code-block:: js


    {
        "text" : {
            "message" : "this is a test"
        }
    }


Note, even though the name is text, it also supports exact matching (**term** like) on numeric values and dates.


Note, **message** is the name of a field, you can subsitute the name of any field (including **_all**) instead.


Types of Text Queries
---------------------

boolean
"""""""

The default **text** query is of type **boolean**. It means that the text provided is analyzed and the analysis process constructs a boolean query from the provided text. The **operator** flag can be set to **or** or **and** to control the boolean clauses (defaults to **or**).


The **analyzer** can be set to control which analyzer will perform the analysis process on the text. It default to the field explicit mapping definition, or the default search analyzer.


**fuzziness** can be set to a value (depending on the relevant type, for string types it should be a value between **0.0** and **1.0**) to constructs fuzzy queries for each term analyzed. The **prefix_length** and **max_expansions** can be set in this case to control the fuzzy process.


Here is an example when providing additional parameters (note the slight change in structure, **message** is the field name):


.. code-block:: js


    {
        "text" : {
            "message" : {
                "query" : "this is a test",
                "operator" : "and"
            }
        }
    }



phrase
""""""

The **text_phrase** query analyzes the text and creates a **phrase** query out of the analyzed text. For example:


.. code-block:: js


    {
        "text_phrase" : {
            "message" : "this is a test"
        }
    }


Since **text_phrase** is only a **type** of a **text** query, it can also be used in the following manner:


.. code-block:: js


    {
        "text" : {
            "message" : {
                "query" : "this is a test",
                "type" : "phrase"
            }
        }
    }


A phrase query maintains order of the terms up to a configurable **slop** (which defaults to 0).


The **analyzer** can be set to control which analyzer will perform the analysis process on the text. It default to the field explicit mapping definition, or the default search analyzer, for example:


.. code-block:: js


    {
        "text_phrase" : {
            "message" : {
                "query" : "this is a test",
                "analyzer" : "my_analyzer"
            }
        }
    }



text_phrase_prefix
""""""""""""""""""

The **text_phrase_prefix** is the same as **text_phrase**, expect it allows for prefix matches on the last term in the text. For example:


.. code-block:: js


    {
        "text_phrase_prefix" : {
            "message" : "this is a test"
        }
    }


Or:


.. code-block:: js


    {
        "text" : {
            "message" : {
                "query" : "this is a test",
                "type" : "phrase_prefix"
            }
        }
    }


It accepts the same parameters as the phrase type. In addition, it also accepts a **max_expansions** parameter that can control to how many prefixes the last term will be expanded. It is highly recommended to set it to an acceptable value to control the execution time of the query. For example:


.. code-block:: js


    {
        "text_phrase_prefix" : {
            "message" : {
                "query" : "this is a test",
                "max_expansions" : 10
            }
        }
    }



Comparison to query_string / field
----------------------------------

The text family of queries does not go through a "query parsing" process. It does not support field name prefixes, wildcard characters, or other "advance" features. For this reason, chances of it failing are very small / non existent, and it provides an excellent behavior when it comes to just analyze and run that text as a query behavior (which is usually what a text search box does). Also, the **phrase_prefix** can provide a great "as you type" behavior to automatically load search results.

