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


**group** set to **-1** (the default) is equivalent to "split". Using Using group >= 0 selects the matching group as the token. For example, if you have:


<pre>
pattern = \'([^\']+)\'
group = 0
input = aaa 'bbb' 'ccc'


the output will be two tokens: 'bbb' and 'ccc' (including the ' marks).  With the same input but using group=1, the output would be: bbb and ccc (no ' marks).


