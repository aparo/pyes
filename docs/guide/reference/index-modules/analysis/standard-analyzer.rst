=================
Standard Analyzer
=================

An analyzer of type **standard** that is built of using :doc:`Standard Tokenizer <./standard-tokenizer.html>`,  with :doc:`Standard Token Filter <./standard-tokenfilter.html>`,  :doc:`Lower Case Token Filter <./lowercase-tokenfilter.html>`,  and :doc:`Stop Token Filter <./stop-tokenfilter.html>`.  

The following are settings that can be set for a **standard** analyzer type:


======================  ==================================================================================================================
 Setting                 Description                                                                                                      
======================  ==================================================================================================================
**stopwords**           A list of stopword to initialize the stop filter with. Defaults to the english stop words.                        
**max_token_length**    The maximum token length. If a token is seen that exceeds this length then it is discarded. Defaults to **255**.  
======================  ==================================================================================================================
