Analyzer
========

Analyzers in general are broken down into a **Tokenizer** with zero or more **TokenFilter** applied to it. The analysis module allows to register **TokenFilters**, **Tokenizers** and **Analyzers** under logical names which can then be referenced either in mapping definitions or in certain APIs. Here is a list of analyzer types:


=========================================  ==================================================================================================================================================================================================================================================================================================
 Type                                       Description                                                                                                                                                                                                                                                                                      
=========================================  ==================================================================================================================================================================================================================================================================================================
:doc:`standard <./standard/index>`         An analyzer that is built of using :doc:`Standard Tokenizer <./../tokenizer/standard/index>`, ard, :doc:`Standard Token Filter <./../tokenfilter/standard/index>`, :doc:`Lower Case Token Filter <./../tokenfilter/lowercase/index>`, ase, and "Stop Token Filter":../tokenfilter/stop/index>`.   
:doc:`simple <./simple/index>`             An analyzer that is built using a :doc:`Lower Case Tokenizer <.//tokenizer/lowercase/index>`.                                                                                                                                                                                                     
:doc:`stop <./stop/index>`                 An analyzer that is built using a :doc:`Lower Case Tokenizer <./../tokenizer/lowercase/index>`, ase, with "Stop Token Filter":../tokenfilter/stop/index>`.                                                                                                                                        
:doc:`whitespace <./whitespace/index>`     An analyzer that is built using a :doc:`Whitespace Tokenizer <.//tokenizer/whitespace/index>`.                                                                                                                                                                                                    
:doc:`keyword <./keyword/index>`           An analyzer that "tokenizes" an entire stream as a single token. This is useful for data like zip codes, ids and so on. Note, when using mapping definitions, it make more sense to simply mark the field as **not_analyzed**.                                                                    
:doc:`custom <./custom/index>`             An analyzer that allows to combine a **Tokenizer** with zero or more **Token Filters**. The custom analyzer accepts a logical/registered name of the tokenizer to use, and a list of logical/registered names of token filters.                                                                   
:doc:`pattern <./pattern/index>`           An analyzer that breaks text into terms using a regular expression.                                                                                                                                                                                                                               
:doc:`lang <./lang/index>`                 Language based analyzers.                                                                                                                                                                                                                                                                         
=========================================  ==================================================================================================================================================================================================================================================================================================

Default Analyzers
-----------------

An analyzer is registered under a logical name and can then be referenced from mapping definitions or certain APIs. When none are defined, defaults are used. There is an option to define which analyzers will be used as default when none can be derived.


The **default** logical name allows to configure an analyzer that will be used both for indexing and for searching APIs. The **default_index** logical name can be used to configure a default analyzer that will be used just when indexing, and the **default_search** can be used to configure a default analyzer that will be used just when indexing.


Aliasing Analyzers
------------------

Analyzers can be aliased to have several registered lookup names associated with them. For example:


.. code-block:: js

    index :
      analysis :
        analyzer :
          standard :
            alias: [alias1, alias2]
            type : standard
            stopwords : [test1, test2, test3]


Will allow the **standard** analyzer to also be referenced with **alias1** and **alias2** values.


Built in Analyzers
------------------

If not explicitly defined (for example, by configuring an analyzer with the same logical name), the following analyzers are automatically registered (under their respective logical names) and available for use:


=========================  =====================================================================================================
 Analyzer Logical Name      Description                                                                                         
=========================  =====================================================================================================
**standard**               A :doc:`Standard Analyzer <./standard/index>` andard registered with default settings/index>`.       
**simple**                 A :doc:`Simple Analyzer <./simple/index>` simple registered with default settings/index>`.           
**stop**                   A :doc:`Stop Analyzer <./stop/index>` ./stop registered with default settings/index>`.               
**whitespace**             A :doc:`Whitespace Analyzer <./whitespace/index>` espace registered with default settings/index>`.   
**keyword**                A :doc:`Keyword Analyzer <./keyword/index>` eyword registered with default settings/index>`.         
=========================  =====================================================================================================
