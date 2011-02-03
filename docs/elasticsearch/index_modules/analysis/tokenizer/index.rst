Tokenizer
=========

Tokenizers act as the first stage of the analysis process (used within an **Analyzer**). The following tokenizer types can be used:


=========================================  =====================================================================================================================================================================================
 Type                                       Description                                                                                                                                                                         
=========================================  =====================================================================================================================================================================================
:doc:`standard <./standard/index>`         A tokenizer providing grammar based tokenizer that is a good tokenizer for most European language documents.                                                                         
:doc:`keyword <./keyword/index>`           A tokenizer that emits the entire input as a single input.                                                                                                                           
:doc:`letter <./letter/index>`             A tokenizer that divides text at non-letters.                                                                                                                                        
:doc:`lowercase <./lowercase/index>`        A tokenizer that performs the function of :doc:`Letter Tokenizer <./letter/index>` lett:doc:`Lower Case Token Filter <./../tokenfilter/lowercase/index>` ercase together/index>`.   
:doc:`whitespace <./whitespace/index>`     A tokenizer that divides text at whitespace.                                                                                                                                         
:doc:`nGram <./ngram/index>`               A tokenizer of type NGram.                                                                                                                                                           
:doc:`edgeNGram <./edgengram/index>`       A tokenizer of type Edge NGram.                                                                                                                                                      
=========================================  =====================================================================================================================================================================================

Built In Tokenizers
-------------------

If not explicitly defined (for example, by configuring a tokenizer with the same logical name), the following tokenizers are automatically registered (under their respective logical names) and available for use:


==========================  ======================================================================================================
 Tokenizer Logical Name      Description                                                                                          
==========================  ======================================================================================================
**standard**                A :doc:`Standard Tokenizer <./standard/index>` andard registered with default settings/index>`.       
**keyword**                 A :doc:`Keyword Tokenizer <./keyword/index>` eyword registered with default settings/index>`.         
**letter**                  A :doc:`Letter Tokenizer <./letter/index>` letter registered with default settings/index>`.           
**lowercase**               A :doc:`Lower Case Tokenizer <./lowercase/index>` ercase registered with default settings/index>`.    
**whitespace**              A :doc:`Whitespace Tokenizer <./whitespace/index>` espace registered with default settings/index>`.   
**nGram**                   A :doc:`NGram Tokenizer <./ngram/index>` /ngram registered with default settings/index>`.             
**edgeNGram**               A :doc:`EdgeNGram Tokenizer <./edgengram/index>` engram registered with default settings/index>`.     
==========================  ======================================================================================================
