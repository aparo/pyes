==================
Standard Tokenizer
==================

A tokenizer of type **standard** providing grammar based tokenizer that is a good tokenizer for most European language documents. It splits words at punctuation characters, removing punctuation. However, a  dot that's not followed by whitespace is considered part of a token. It also splits words at hyphens, unless there's a number in the token, in which case the whole token is interpreted as a product number and is not split. It recognizes email addresses and internet hostnames as one token.


The following are settings that can be set for a **standard** tokenizer type:


======================  ==================================================================================================================
 Setting                 Description                                                                                                      
======================  ==================================================================================================================
**max_token_length**    The maximum token length. If a token is seen that exceeds this length then it is discarded. Defaults to **255**.  
======================  ==================================================================================================================
