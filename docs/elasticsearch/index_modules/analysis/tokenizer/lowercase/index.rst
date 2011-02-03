Lowercase Tokenizer
===================

A tokenizer of type **lowercase** that performs the function of :doc:`Letter Tokenizer <./../letter/index>` and :doc:`Lower Case Token Filter <./../../tokenfilter/lowercase/index>` together. It divides text at non-letters and converts them to lower case.  While it is functionally equivalent to the combination of :doc:`Letter Tokenizer <./../letter/index>` and :doc:`Lower Case Token Filter <./../../tokenfilter/lowercase/index>`, there is a performance advantage to doing the two tasks at once, hence this (redundant) implementation.

