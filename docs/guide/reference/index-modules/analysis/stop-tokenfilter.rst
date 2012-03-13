.. _es-guide-reference-index-modules-analysis-stop-tokenfilter:

================
Stop Tokenfilter
================

A token filter of type **stop** that removes stop words from token streams.


The following are settings that can be set for a **stop** token filter type:


================================  =====================================================================================================================
 Setting                           Description                                                                                                         
================================  =====================================================================================================================
**stopwords**                     A list of stop words to use. Defaults to english stop words.                                                         
**stopwords_path**                A path (either relative to **config** location, or absolute) to a stopwords file configuration.                      
**enable_position_increments**    Set to **true** if token positions should record the removed stop words, **false** otherwise. Defaults to **true**.  
**ignore_case**                   Set to **true** to lower case all words first. Defaults to **false**.                                                
================================  =====================================================================================================================

stopwords allow for custom language specific expansion of default stopwords. It follows the **_lang_** notation and supports: arabic, armenian, basque, brazilian, bulgarian, catalan, czech, danish, dutch, english, finnish, french, galician, german, greek, hindi, hungarian, indonesian, italian, norwegian, persian, portuguese, romanian, russian, spanish, swedish, turkish.

