Porter Filter
=============

A token filter of type **porterStem** that transforms the token stream as per the Porter stemming algorithm. 


Note, the input to the stemming filter must already be in lower case, so you will need to use :doc:`Lower Case Token Filter <./../lowercase/index>` or :doc:`Lower Case Tokenizer <./../../tokenizer/lowercase/index>` farther down the Tokenizer chain in order for this to work properly!. For example, when using custom analyzer, make sure the **lowercase** filter comes before the **porterStem** filter in the list of filters.

