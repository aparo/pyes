.. _es-guide-reference-index-modules-analysis-pattern_replace-tokenfilter:

===========================
Pattern_Replace Tokenfilter
===========================

The **pattern_replace** token filter allows to easily handle string replacements based on a regular expression. The regular expression is defined using the **pattern** parameter, and the replacement string can be provided using the **replacement** parameter (supporting referencing the original text, as explained `here <http://docs.oracle.com/javase/6/docs/api/java/util/regex/Matcher.html#appendReplacement(java.lang.StringBuffer>`_,  java.lang.String)).

