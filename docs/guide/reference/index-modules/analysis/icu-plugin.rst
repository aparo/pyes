==========
Icu Plugin
==========

The `ICU <http://icu-project.org/>`_  analysis plugin allows for unicode normalization, collation and folding. The plugin is called **analysis-icu** and can be installed by running:


.. code-block:: js

    bin/plugin install analysis-icu


The plugin includes the following analysis components:


ICU Normalization
=================

Normalizes characters as explained `here <http://userguide.icu-project.org/transforms/normalization>`_.  It registers itself by default under **icu_normalizer** or **icuNormalizer** using the default settings. Allows for the name parameter to be provided which can include the following values: **nfc**, **nfkc**, and **nfkc_cf**. Here is a sample settings:


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "collation" : {
                        "tokenizer" : "keyword",
                        "filter" : ["icu_normalizer"]
                    }
                }
            }
        }
    }


ICU Folding
===========

Folding of unicode characters based on **UTR#30**. It registers itself under **icu_folding** and **icuFolding** names. Sample setting:


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "collation" : {
                        "tokenizer" : "keyword",
                        "filter" : ["icu_folding"]
                    }
                }
            }
        }
    }


ICU Collation
=============

Uses collation token filter. Allows to either specify the rules for collation (defined `here <http://www.icu-project.org/userguide/Collate_Customization.html)>`_  using the **rules** parameter (can point to a location or expressed in the settings, location can be relative to config location), or using the **language** parameter (further specialized by country and variant). By default registers under **icu_collation** or **icuCollation** and uses the default locale.


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

