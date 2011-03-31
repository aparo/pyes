===================
Lowercase Tokenizer
===================

A tokenizer of type **lowercase** that performs the function of :doc:`Letter Tokenizer <./letter-tokenizer.html>`  and :doc:`Lower Case Token Filter <./lowercase-tokenfilter.html>`  together. It divides text at non-letters and converts them to lower case.  While it is functionally equivalent to the combination of :doc:`Letter Tokenizer <./letter-tokenizer.html>`  and :doc:`Lower Case Token Filter <./lowercase-tokenizer.html>`,  there is a performance advantage to doing the two tasks at once, hence this (redundant) implementation.

