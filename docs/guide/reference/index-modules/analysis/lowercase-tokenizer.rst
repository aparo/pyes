.. _es-guide-reference-index-modules-analysis-lowercase-tokenizer:

===================
Lowercase Tokenizer
===================

A tokenizer of type **lowercase** that performs the function of :ref:`Letter Tokenizer <es-guide-reference-index-modules-analysis-letter-tokenizer>`  and :ref:`Lower Case Token Filter <es-guide-reference-index-modules-analysis-lowercase-tokenfilter>`  together. It divides text at non-letters and converts them to lower case.  While it is functionally equivalent to the combination of :ref:`Letter Tokenizer <es-guide-reference-index-modules-analysis-letter-tokenizer>`  and :ref:`Lower Case Token Filter <es-guide-reference-index-modules-analysis-lowercase-tokenizer>`,  there is a performance advantage to doing the two tasks at once, hence this (redundant) implementation.

