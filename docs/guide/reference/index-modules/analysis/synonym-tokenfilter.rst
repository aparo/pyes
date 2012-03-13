.. _es-guide-reference-index-modules-analysis-synonym-tokenfilter:

===================
Synonym Tokenfilter
===================

The **synonym** token filter allows to easily handle synonyms during the analysis process. Synonyms are configured using a configuration file. Here is an example:


.. code-block:: js


    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "synonym" : {
                        "tokenizer" : "whitespace",
                        "filter" : ["synonym"]
                    }
                },
                "filter" : {
                    "synonym" : {
                        "type" : "synonym",
                        "synonyms_path" : "analysis/synonym.txt"
                    }
                }
            }
        }
    }


The above configures a **synonym** filter, with a path of **analysis/synonym.txt** (relative to the **config** location). The **synonym** analyzer is then configured with the filter. Additional settings are: **ignore_case** (defaults to **false**), and **expand** (defaults to **true**).


The **tokenizer** parameter controls the tokenizers that will be used to tokenize the synonym, and defaults to the **whitespace** tokenizer.


As of elasticsearch 0.17.9 two synonym formats are supported: Solr, WordNet.


Solr synonyms
-------------

The following is a sample format of the file:


.. code-block:: js

    # blank lines and lines starting with pound are comments.
    
    #Explicit mappings match any token sequence on the LHS of "=>"
    #and replace with all alternatives on the RHS.  These types of mappings
    #ignore the expand parameter in the schema.
    #Examples:
    i-pod, i pod => ipod,
    sea biscuit, sea biscit => seabiscuit
    
    #Equivalent synonyms may be separated with commas and give
    #no explicit mapping.  In this case the mapping behavior will
    #be taken from the expand parameter in the schema.  This allows
    #the same synonym file to be used in different synonym handling strategies.
    #Examples:
    ipod, i-pod, i pod
    foozball , foosball
    universe , cosmos
    
    # If expand==true, "ipod, i-pod, i pod" is equivalent to the explicit mapping:
    ipod, i-pod, i pod => ipod, i-pod, i pod
    # If expand==false, "ipod, i-pod, i pod" is equivalent to the explicit mapping:
    ipod, i-pod, i pod => ipod
    
    #multiple synonym mapping entries are merged.
    foo => foo bar
    foo => baz
    #is equivalent to
    foo => foo bar, baz


You can also define synonyms for the filter directly in the configuration file (note use of **synonyms** instead of **synonyms_path**):


.. code-block:: js


    {
        "filter" : {
            "synonym" : {
                "type" : "synonym",
                "synonyms" : [
                    "i-pod, i pod => ipod",
                    "universe, cosmos"
                ] 
            }
        }
    }


However, it is recommended to define large synonyms set in a file using **synonyms_path**.


WordNet synonyms
----------------

Synonyms based on `WordNet <http://wordnet.princeton.edu/>`_  format can be declared using **format**:


.. code-block:: js


    {
        "filter" : {
            "synonym" : {
                "type" : "synonym",
                "format" : "wordnet",
                "synonyms" : [
                    "s(100000001,1,'abstain',v,1,0).",
                    "s(100000001,2,'refrain',v,1,0).",
                    "s(100000001,3,'desist',v,1,0)."
                ]
            }
        }
    }


Using **synonyms_path** to define WordNet synonyms in a file is supported as well.

