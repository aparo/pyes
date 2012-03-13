.. _es-guide-reference-index-modules-analysis-truncate-tokenfilter:

====================
Truncate Tokenfilter
====================

The **truncate** token filter can be used to truncate tokens into a specific length. This can come in handy with keyword (single token) based mapped fields that are used for sorting in order to reduce memory usage.


It accepts a **length** parameter which control the number of characters to truncate to, defaults to **10**.

