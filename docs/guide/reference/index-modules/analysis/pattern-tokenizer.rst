.. _es-guide-reference-index-modules-analysis-pattern-tokenizer:

=================
Pattern Tokenizer
=================

A tokenizer of type **pattern** that can flexibly separate text into terms via a regular expression. Accepts the following settings:


=============  =================================================================
 Setting        Description                                                     
=============  =================================================================
**pattern**    The regular expression pattern, defaults to **\W+**.             
**flags**      The regular expression flags.                                    
**group**      Which group to extract into tokens. Defaults to **-1** (split).  
=============  =================================================================

*IMPORTANT*: The regular expression should match the *token separators*, not the tokens themselves.

