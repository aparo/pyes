Char Filter
===========

Char filters allow to filter out the stream of text before it gets tokenized (used within an **Analyzer**). The following char filters types can be used:


=========================================  =====================================================
 Type                                       Description                                         
=========================================  =====================================================
:doc:`html_strip <./html_strip/index>`     A char filter that removes HTML elements from text.  
=========================================  =====================================================

Built in Char Filters
---------------------

If not explicitly defined (for example, by configuring a char filter with the same logical name), the following char filters are automatically registered (under their respective logical names) and available for use:


==============================  =============================================================================================
 Token Filter Logical Name       Description                                                                                 
==============================  =============================================================================================
**html_strip**/**htmlStrip**    An :doc:`HTML Strip <./html_strip/index>` _strip registered with default settings/index>`.   
==============================  =============================================================================================
