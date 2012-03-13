.. _es-guide-reference-index-modules-analysis-pathhierarchy-tokenizer:

=======================
Pathhierarchy Tokenizer
=======================

The **path_hierarchy** tokenizer takes something like this:


<pre>
/something/something/else


And produces tokens:


<pre>
/something
/something/something
/something/something/else


=================  ==========================================================================
 Setting            Description                                                              
=================  ==========================================================================
**delimiter**      The character delimiter to use, defaults to **/**.                        
**replacement**    An optional replacement character to use. Defaults to the **delimiter**.  
**buffer_size**    The buffer size to use, defaults to **1024**.                             
**reverse**        Generates tokens in reverse order, defaults to **false**.                 
**skip**           Controls initial tokens to skip, defaults to **0**.                       
=================  ==========================================================================
