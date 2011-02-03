Index Analysis Module
=====================

The index analysis module acts as a configurable registry of :doc:`Analyzers <./analyzer/index>` that can be used in order to both break indexed (analyzed) fields when a document is indexed and process query strings. It maps to Lucene **Analyzer**. 


Analyzers in general are broken down into a :doc:`Tokenizer <./tokenizer/index>` with zero or more :doc:`Token Filter <./tokenfilter/index>` applied to it. A set of :doc:`Char Filters <./charfilter/index>` can be associated with it to filter out the text stream. The analysis module allows to register **TokenFilters**, **Tokenizers** and **Analyzers** under logical names which can then be referenced either in mapping definitions or in certain APIs. The Analysis module automatically registers (*if not explicitly defined*) built in analyzers, token filters, and tokenizers. 


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


Plugins
-------

The following is a list of plugins extending the built in analyzers, tokenizers and token filters:


===========================  =========================================================================================================
 Plugin                       Description                                                                                             
===========================  =========================================================================================================
:doc:`icu <./icu/index>`     A plugin that uses `ICU <http://icu-project.org/>` for unicode normalization, collation and folding>`.   
===========================  =========================================================================================================
