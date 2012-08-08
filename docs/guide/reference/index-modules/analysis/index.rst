.. _es-guide-reference-index-modules-analysis-index:
.. _es-guide-reference-index-modules-analysis:

========
Analysis
========

The index analysis module acts as a configurable registry of Analyzers that can be used in order to both break indexed (analyzed) fields when a document is indexed and process query strings. It maps to the Lucene **Analyzer**. 


Analyzers are (generally) composed of a single **Tokenizer** and zero or more **TokenFilters**. A set of **CharFilters** can be associated with an analyzer to process the characters prior to other analysis steps. The analysis module allows one to register **TokenFilters**, **Tokenizers** and **Analyzers** under logical names that can then be referenced either in mapping definitions or in certain APIs. The Analysis module automatically registers (*if not explicitly defined*) built in analyzers, token filters, and tokenizers. 


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


All analyzers, tokenizers, and token filters can be configured with a **version** parameter to control which Lucene version behavior they should use. Possible values are: **3.0**, **3.1**, **3.2**, **3.3**, **3.4** and **3.5** (the highest version number is the default option).


Types
=====

Analyzer
--------

Analyzers in general are broken down into a **Tokenizer** with zero or more **TokenFilter** applied to it. The analysis module allows one to register **TokenFilters**, **Tokenizers** and **Analyzers** under logical names which can then be referenced either in mapping definitions or in certain APIs. Here is a list of analyzer types:


Char Filter
-----------

Char filters allow one to filter out the stream of text before it gets tokenized (used within an **Analyzer**). 


Tokenizer
---------

Tokenizers act as the first stage of the analysis process (used within an **Analyzer**).


Token Filter
------------

Token filters act as additional stages of the analysis process (used within an **Analyzer**).


Default Analyzers
=================

An analyzer is registered under a logical name. It can then be referenced from mapping definitions or certain APIs. When none are defined, defaults are used. There is an option to define which analyzers will be used by default when none can be derived.


The **default** logical name allows one to configure an analyzer that will be used both for indexing and for searching APIs. The **default_index** logical name can be used to configure a default analyzer that will be used just when indexing, and the **default_search** can be used to configure a default analyzer that will be used just when searching.


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

.. toctree::
    :maxdepth: 1

    custom-analyzer
    keyword-analyzer
    lang-analyzer
    pattern-analyzer
    simple-analyzer
    snowball-analyzer
    standard-analyzer
    stop-analyzer
    whitespace-analyzer

    asciifolding-tokenfilter
    compound-word-tokenfilter
    edgengram-tokenfilter
    elision-tokenfilter
    kstem-tokenfilter
    length-tokenfilter
    lowercase-tokenfilter
    ngram-tokenfilter
    pattern_replace-tokenfilter
    phonetic-tokenfilter
    porterstem-tokenfilter
    reverse-tokenfilter
    shingle-tokenfilter
    snowball-tokenfilter
    standard-tokenfilter
    standard-tokenizer
    stemmer-tokenfilter
    stop-tokenfilter
    synonym-tokenfilter
    trim-tokenfilter
    word-delimiter-tokenfilter

    edgengram-tokenizer
    keyword-tokenizer
    letter-tokenizer
    lowercase-tokenizer
    ngram-tokenizer
    pathhierarchy-tokenizer
    pattern-tokenizer
    uaxurlemail-tokenizer
    truncate-tokenfilter
    whitespace-tokenizer
    unique-tokenfilter

    htmlstrip-charfilter
    mapping-charfilter

    icu-plugin
