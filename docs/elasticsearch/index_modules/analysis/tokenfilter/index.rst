Token Filter
============

Token filters act as the additional stages of the analysis process (used within an **Analyzer**). The following token filters types can be used:


=============================================  ==================================================================================================================================================================================================================
 Type                                           Description                                                                                                                                                                                                      
=============================================  ==================================================================================================================================================================================================================
:doc:`stop <./stop/index>`                     A token filter that removes stop words from token streams.                                                                                                                                                        
:doc:`asciifolding <./asciifolding/index>`     A token filter that converts alphabetic, numeric, and symbolic Unicode characters which are not in the first 127 ASCII characters (the "Basic Latin" Unicode block) into their ASCII equivalents, if one exists.  
:doc:`length <./length/index>`                 A token filter that removes words that are too long or too short for the stream.                                                                                                                                  
:doc:`lowercase <./lowercase/index>`           A token filter that normalizes token text to lower case.                                                                                                                                                          
:doc:`porterstem <./porterstem/index>`         A token filter that transforms the token stream as per the Porter stemming algorithm.                                                                                                                             
:doc:`standard <./standard/index>`             A token filter that normalizes tokens extracted with the :doc:`Standard Tokenizer <.//tokenizer/standard/index>`.                                                                                                 
:doc:`nGram <./ngram/index>`                   An NGram token filter.                                                                                                                                                                                            
:doc:`edgeNGram <./edgengram/index>`           An Edge NGram token filter.                                                                                                                                                                                       
:doc:`shingle <./shingle/index>`               A shingle token filter.                                                                                                                                                                                           
=============================================  ==================================================================================================================================================================================================================

Built in Token Filters
----------------------

If not explicitly defined (for example, by configuring a token filter with the same logical name), the following token filters are automatically registered (under their respective logical names) and available for use:


=============================  ==============================================================================================================
 Token Filter Logical Name      Description                                                                                                  
=============================  ==============================================================================================================
**stop**                       A :doc:`Stop Token Filter <./stop/index>` ./stop registered with default settings/index>`.                    
**asciifolding**               A :doc:`ASCII Folding Token Filter <./asciifolding/index>` olding registered with default settings/index>`.   
**length**                     A :doc:`Length Token Filter <./length/index>` length registered with default settings/index>`.                
**lowercase**                  A :doc:`Lower Case Token Filter <./lowercase/index>` ercase registered with default settings/index>`.         
**porterstem**                 A :doc:`Porter Stem Token Filter <./porterstem/index>` erstem registered with default settings/index>`.       
**standard**                   A :doc:`Standard Token Filter <./standard/index>` andard registered with default settings/index>`.            
**nGram**                      A :doc:`NGram Token Filter <./ngram/index>` /ngram registered with default settings/index>`.                  
**edgeNGram**                  A :doc:`EdgeNGram Token Filter <./edgengram/index>` engram registered with default settings/index>`.          
**shingle**                    A :doc:`Shingle Token Filter <./shingle/index>` hingle registered with default settings/index>`.              
=============================  ==============================================================================================================
