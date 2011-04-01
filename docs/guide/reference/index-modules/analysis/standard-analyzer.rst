.. _es-guide-reference-index-modules-analysis-standard-analyzer:

=================
Standard Analyzer
=================

An analyzer of type **standard** that is built of using :ref:`Standard Tokenizer <es-guide-reference-index-modules-analysis-standard-tokenizer>`,  with :ref:`Standard Token Filter <es-guide-reference-index-modules-analysis-standard-tokenfilter>`,  :ref:`Lower Case Token Filter <es-guide-reference-index-modules-analysis-lowercase-tokenfilter>`,  and :ref:`Stop Token Filter <es-guide-reference-index-modules-analysis-stop-tokenfilter>`.  

The following are settings that can be set for a **standard** analyzer type:


======================  ==================================================================================================================
 Setting                 Description                                                                                                      
======================  ==================================================================================================================
**stopwords**           A list of stopword to initialize the stop filter with. Defaults to the english stop words.                        
**max_token_length**    The maximum token length. If a token is seen that exceeds this length then it is discarded. Defaults to **255**.  
======================  ==================================================================================================================
