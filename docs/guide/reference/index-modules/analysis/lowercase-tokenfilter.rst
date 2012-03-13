.. _es-guide-reference-index-modules-analysis-lowercase-tokenfilter:

=====================
Lowercase Tokenfilter
=====================

A token filter of type **lowercase** that normalizes token text to lower case.


Lowercase token filter supports Greek and Turkish lowercase token filters through the **language** parameter. Below is a usage example in a custom analyzer


.. code-block:: js

    index :
        analysis :
            analyzer : 
                myAnalyzer2 :
                    type : custom
                    tokenizer : myTokenizer1
                    filter : [myTokenFilter1, myGreekLowerCaseFilter]
                    char_filter : [my_html]
            tokenizer :
                myTokenizer1 :
                    type : standard
                    max_token_length : 900
            filter :
                myTokenFilter1 :
                    type : stop
                    stopwords : [stop1, stop2, stop3, stop4]
                myGreekLowerCaseFilter :
                    type : lowercase
                    language : greek
            char_filter :
                  my_html :
                    type : html_strip
                    escaped_tags : [xxx, yyy]
                    read_ahead : 1024

