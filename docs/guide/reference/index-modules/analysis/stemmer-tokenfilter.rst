.. _es-guide-reference-index-modules-analysis-stemmer-tokenfilter:

===================
Stemmer Tokenfilter
===================

A filter that stems words (similar to **snowball**, but with more options). The **language**/**name** parameter controls the stemmer with the following available values:


armenian, basque, bulgarian, catalan, danish, dutch, english, finnish, french, german, german2, greek, hungarian, italian, kp, lovins, norwegian, porter, porter2, portuguese, romanian, russian, spanish, swedish, turkish, minimal_english, possessive_english, light_finish, light_french, minimal_french, light_german, minimal_german, hindi, light_hungarian, indonesian, light_italian, light_portuguese, minimal_portuguese, portuguese, light_russian, light_spanish, light_swedish.


For example:


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "my_analyzer" : {
                        "tokenizer" : "standard",
                        "filter" : ["standard", "lowercase", "my_stemmer"]
                    }
                },
                "filter" : {
                    "my_stemmer" : {
                        "type" : "stemmer",
                        "name" : "light_german"
                    }
                }
            }
        }
    }

