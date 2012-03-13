.. _es-guide-reference-index-modules-analysis-standard-tokenizer:

==================
Standard Tokenizer
==================

A tokenizer of type **standard** providing grammar based tokenizer that is a good tokenizer for most European language documents. The tokenizer implements the Unicode Text Segmentation algorithm, as specified in `Unicode Standard Annex #29 <http://unicode.org/reports/tr29/>`_.  

The following are settings that can be set for a **standard** tokenizer type:


======================  ==================================================================================================================
 Setting                 Description                                                                                                      
======================  ==================================================================================================================
**max_token_length**    The maximum token length. If a token is seen that exceeds this length then it is discarded. Defaults to **255**.  
======================  ==================================================================================================================
