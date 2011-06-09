.. _es-guide-reference-index-modules-analysis-stop-analyzer:

=============
Stop Analyzer
=============

An analyzer of type **stop** that is built using a :ref:`Lower Case Tokenizer <es-guide-reference-index-modules-analysis-lowercase-tokenizer>`,  with :ref:`Stop Token Filter <es-guide-reference-index-modules-analysis-stop-tokenfilter>`.  

The following are settings that can be set for a **stop** analyzer type:


====================  =================================================================================================
 Setting               Description                                                                                     
====================  =================================================================================================
**stopwords**         A list of stopword to initialize the stop filter with. Defaults to the english stop words.       
**stopwords_path**    A path (either relative to **config** location, or absolute) to a stopwords file configuration.  
====================  =================================================================================================
