.. _es-guide-reference-index-modules-analysis-icu-plugin:

==========
Icu Plugin
==========

The `ICU <http://icu-project.org/>`_  analysis plugin allows for unicode normalization, collation and folding. The plugin is called `elasticsearch-analysis-icu <https://github.com/elasticsearch/elasticsearch-analysis-icu>`_.  


The plugin includes the following analysis components:


ICU Normalization
=================

Normalizes characters as explained `here <http://userguide.icu-project.org/transforms/normalization>`_.  It registers itself by default under **icu_normalizer** or **icuNormalizer** using the default settings. Allows for the name parameter to be provided which can include the following values: **nfc**, **nfkc**, and **nfkc_cf**. Here is a sample settings:


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "normalization" : {
                        "tokenizer" : "keyword",
                        "filter" : ["icu_normalizer"]
                    }
                }
            }
        }
    }


ICU Folding
===========

Folding of unicode characters based on **UTR#30**. It registers itself under **icu_folding** and **icuFolding** names. 

The filter also does lowercasing, which means the lowercase filter can normally be left out. Sample setting:

.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "folding" : {
                        "tokenizer" : "keyword",
                        "filter" : ["icu_folding"]
                    }
                }
            }
        }
    }


Filtering
---------

The folding can be filtered by a set of unicode characters with the parameter **unicodeSetFilter**. This is useful for a non-internationalized search engine where retaining a set of national characters which are primary letters in a specific language is wanted. See syntax for the UnicodeSet `here2 <http://icu-project.org/apiref/icu4j/com/ibm/icu/text/UnicodeSet.html>`_.  

The Following example excempt Swedish characters from the folding. Note that the filtered characters are NOT lowercased which is why we add that filter below.


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "folding" : {
                        "tokenizer" : "standard",
                        "filter" : ["my_icu_folding", "lowercase"]
                    }
                }
                "filter" : {
                    "my_icu_folding" : {
                        "type" : "icu_folding"
                        "unicodeSetFilter" : "[^åäöÅÄÖ]"
                    }
                }
            }
        }
    }


ICU Collation
=============

Uses collation token filter. Allows to either specify the rules for collation (defined `here3 <http://www.icu-project.org/userguide/Collate_Customization.html)>`_  using the **rules** parameter (can point to a location or expressed in the settings, location can be relative to config location), or using the **language** parameter (further specialized by country and variant). By default registers under **icu_collation** or **icuCollation** and uses the default locale.


Here is a sample settings:


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "collation" : {
                        "tokenizer" : "keyword",
                        "filter" : ["icu_collation"]
                    }
                }
            }
        }
    }


And here is a sample of custom collation:


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "collation" : {
                        "tokenizer" : "keyword",
                        "filter" : ["myCollator"]
                    }
                },
                "filter" : {
                    "myCollator" : {
                        "type" : "icu_collation",
                        "language" : "en"
                    }
                }
            }
        }
    }    

