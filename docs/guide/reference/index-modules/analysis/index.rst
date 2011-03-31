========
Analysis
========

The index analysis module acts as a configurable registry of Analyzers that can be used in order to both break indexed (analyzed) fields when a document is indexed and process query strings. It maps to Lucene **Analyzer**. 


Analyzers in general are broken down into a **Tokenizer** with zero or more **TokenFilters** applied to it. A set of **CharFilters** can be associated with it to filter out the text stream. The analysis module allows to register **TokenFilters**, **Tokenizers** and **Analyzers** under logical names which can then be referenced either in mapping definitions or in certain APIs. The Analysis module automatically registers (*if not explicitly defined*) built in analyzers, token filters, and tokenizers. 


Here is a sample configuration:


.. code-block:: js

    index :
        analysis :
            analyzer : 
                standard : 
                    type : standard
                    stopwords : [stop1, stop2]
                myAnalyzer1 :
                    type : standard
                    stopwords : [stop1, stop2, stop3]
                    max_token_length : 500
                # configure a custom analyzer which is 
                # exactly like the default standard analyzer
                myAnalyzer2 :
                    tokenizer : standard
                    filter : [standard, lowercase, stop]
            tokenizer :
                myTokenizer1 :
                    type : standard
                    max_token_length : 900
                myTokenizer2 :
                    type : keyword
                    buffer_size : 512
            filter :
                myTokenFilter1 :
                    type : stop
                    stopwords : [stop1, stop2, stop3, stop4]
                myTokenFilter2 :
                    type : length
                    min : 0
                    max : 2000


Types
=====

Analyzer
--------

Analyzers in general are broken down into a **Tokenizer** with zero or more **TokenFilter** applied to it. The analysis module allows to register **TokenFilters**, **Tokenizers** and **Analyzers** under logical names which can then be referenced either in mapping definitions or in certain APIs. Here is a list of analyzer types:


Char Filter
-----------

Char filters allow to filter out the stream of text before it gets tokenized (used within an **Analyzer**). 


Tokenizer
---------

Tokenizers act as the first stage of the analysis process (used within an **Analyzer**).


Token Filter
------------

Token filters act as the additional stages of the analysis process (used within an **Analyzer**).


Default Analyzers
=================

An analyzer is registered under a logical name and can then be referenced from mapping definitions or certain APIs. When none are defined, defaults are used. There is an option to define which analyzers will be used as default when none can be derived.


The **default** logical name allows to configure an analyzer that will be used both for indexing and for searching APIs. The **default_index** logical name can be used to configure a default analyzer that will be used just when indexing, and the **default_search** can be used to configure a default analyzer that will be used just when indexing.


Aliasing Analyzers
==================

Analyzers can be aliased to have several registered lookup names associated with them. For example:


.. code-block:: js

    index :
      analysis :
        analyzer :
          standard :
            alias: [alias1, alias2]
            type : standard
            stopwords : [test1, test2, test3]


Will allow the **standard** analyzer to also be referenced with **alias1** and **alias2** values.

