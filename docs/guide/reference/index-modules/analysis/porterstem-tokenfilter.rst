.. _es-guide-reference-index-modules-analysis-porterstem-tokenfilter:

======================
Porterstem Tokenfilter
======================

A token filter of type **porterStem** that transforms the token stream as per the Porter stemming algorithm. 


Note, the input to the stemming filter must already be in lower case, so you will need to use :ref:`Lower Case Token Filter <es-guide-reference-index-modules-analysis-lowercase-tokenfilter>`  or :ref:`Lower Case Tokenizer <es-guide-reference-index-modules-analysis-lowercase-tokenizer>`  farther down the Tokenizer chain in order for this to work properly!. For example, when using custom analyzer, make sure the **lowercase** filter comes before the **porterStem** filter in the list of filters.

