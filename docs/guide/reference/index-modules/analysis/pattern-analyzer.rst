.. _es-guide-reference-index-modules-analysis-pattern-analyzer:

================
Pattern Analyzer
================

An analyzer of type **pattern** that can flexibly separate text into terms via a regular expression. Accepts the following settings:


The following are settings that can be set for a **pattern** analyzer type:


===============  ==========================================================
 Setting          Description                                              
===============  ==========================================================
**lowercase**    Should terms be lowercased or not. Defaults to **true**.  
**pattern**      The regular expression pattern, defaults to **\W+**.      
**flags**        The regular expression flags.                             
===============  ==========================================================

*IMPORTANT*: The regular expression should match the *token separators*, not the tokens themselves.


Flags should be pipe-separated, eg **`CASE_INSENSITIVE|COMMENTS"**. Check "Java Pattern API <http://download.oracle.com/javase/6/docs/api/java/util/regex/Pattern.html#field_summary>`_  for more details about **flags** options.


Pattern Analyzer Examples
-------------------------

In order to try out these examples, you should delete the **test** index before running each example:


.. code-block:: js

        curl -XDELETE localhost:9200/test



Whitespace tokenizer
""""""""""""""""""""

.. code-block:: js

        curl -XPUT 'localhost:9200/test' -d '
        {
            :ref:`settings <es-guide-reference-index-modules-analysis-{>`  s <es-guide-reference-index-modules-analysis-{>`  
                :ref:`analysis <es-guide-reference-index-modules-analysis>`  is <es-guide-reference-index-modules-analysis>`  {
                    :ref:`analyzer <es-guide-reference-index-modules-analysis>`  er <es-guide-reference-index-modules-analysis>`  {
                        :ref:`whitespace <es-guide-reference-index-modules-analysis-{>`  e <es-guide-reference-index-modules-analysis-{>`  
                            :ref:`type <es-guide-reference-index-modules-analysis>`  pe <es-guide-reference-index-modules-analysis>`  "pattern",
                            :ref:`pattern <es-guide-reference-index-modules-analysis-"\\s+">`  -guide-reference-index-modules-analysis-"\\s+">`  
                        }
                    }
                }
            }
        }'
    
        curl 'localhost:9200/test/_analyze?pretty=1&analyzer=whitespace' -d 'foo,bar baz'
        # "foo,bar", "baz"


Non-word character tokenizer
""""""""""""""""""""""""""""

.. code-block:: js

    
        curl -XPUT 'localhost:9200/test' -d '
        {
            :ref:`settings <es-guide-reference-index-modules-analysis-{>`  s <es-guide-reference-index-modules-analysis-{>`  
                :ref:`analysis <es-guide-reference-index-modules-analysis>`  is <es-guide-reference-index-modules-analysis>`  {
                    :ref:`analyzer <es-guide-reference-index-modules-analysis>`  er <es-guide-reference-index-modules-analysis>`  {
                        :ref:`nonword <es-guide-reference-index-modules-analysis-{>`  d <es-guide-reference-index-modules-analysis-{>`  
                            :ref:`type <es-guide-reference-index-modules-analysis>`  pe <es-guide-reference-index-modules-analysis>`  "pattern",
                            :ref:`pattern <es-guide-reference-index-modules-analysis-"[^\\w]+">`  ide-reference-index-modules-analysis-"[^\\w]+">`  
                        }
                    }
                }
            }
        }'
    
        curl 'localhost:9200/test/_analyze?pretty=1&analyzer=nonword' -d 'foo,bar baz'
        # "foo,bar baz" becomes "foo", "bar", "baz"
    
        curl 'localhost:9200/test/_analyze?pretty=1&analyzer=nonword' -d 'type_1-type_4'
        # "type_1","type_4"
    


CamelCase tokenizer
"""""""""""""""""""

.. code-block:: js

    
        curl -XPUT 'localhost:9200/test?pretty=1' -d '
        {
            :ref:`settings <es-guide-reference-index-modules-analysis-{>`  s <es-guide-reference-index-modules-analysis-{>`  
                :ref:`analysis <es-guide-reference-index-modules-analysis>`  is <es-guide-reference-index-modules-analysis>`  {
                    :ref:`analyzer <es-guide-reference-index-modules-analysis>`  er <es-guide-reference-index-modules-analysis>`  {
                        :ref:`camel <es-guide-reference-index-modules-analysis-{>`  l <es-guide-reference-index-modules-analysis-{>`  
                            :ref:`type <es-guide-reference-index-modules-analysis>`  pe <es-guide-reference-index-modules-analysis>`  "pattern",
                            :ref:`pattern <es-guide-reference-index-modules-analysis-"([^\\p{L}\\d]+)|(?<=\\D)(?=\\d)|(?<=\\d)(?=\\D)|(?<=[\\p{L}&&[^\\p{Lu}]])(?=\\p{Lu})|(?<=\\p{Lu})(?=\\p{Lu}[\\p{L}&&[^\\p{Lu}]])">`  )|(?<=\\p{Lu})(?=\\p{Lu}[\\p{L}&&[^\\p{Lu}]])">`  
                        }
                    }
                }
            }
        }'
    
        curl 'localhost:9200/test/_analyze?pretty=1&analyzer=camel' -d '
            MooseX::FTPClass2_beta
        '
        # "moose","x","ftp","class","2","beta"
    


The regex above is easier to understand as:

.. code-block:: js

    
          ([^\\p{L}\\d]+)                 # swallow non letters and numbers,
        | (?<=\\D)(?=\\d)                 # or non-number followed by number,
        | (?<=\\d)(?=\\D)                 # or number followed by non-number,
        | (?<=[ \\p{L} && [^\\p{Lu}]])    # or lower case
          (?=\\p{Lu})                     #   followed by upper case,
        | (?<=\\p{Lu})                    # or upper case
          (?=\\p{Lu}                      #   followed by upper case
            [\\p{L}&&[^\\p{Lu}]]          #   then lower case
          )




