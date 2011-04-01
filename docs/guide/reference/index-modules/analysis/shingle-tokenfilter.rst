.. _es-guide-reference-index-modules-analysis-shingle-tokenfilter:

===================
Shingle Tokenfilter
===================

A token filter of type **shingle** that constructs shingles (token n-grams) from a token stream. In other words, it creates combinations of tokens as a single token. For example, the sentence "please divide this sentence into shingles" might be tokenized into shingles "please divide", "divide this", "this sentence", "sentence into", and "into shingles".


This filter handles position increments > 1 by inserting filler tokens (tokens with termtext "_"). It does not handle a position increment of 0.



The following are settings that can be set for a **shingle** token filter type:


======================  =======================
 Setting                 Description           
======================  =======================
**max_shingle_size**    Defaults to **2**.     
**output_unigrams**     Defaults to **true**.  
======================  =======================
