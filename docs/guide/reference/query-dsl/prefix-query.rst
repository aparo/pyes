.. _es-guide-reference-query-dsl-prefix-query:

============
Prefix Query
============

Matches documents that have fields containing terms with a specified prefix (*not analyzed*). The prefix query maps to Lucene **PrefixQuery**. The following matches documents where the user field contains a term that starts with **ki**:


.. code-block:: js


    {
        "prefix" : { "user" : "ki" }
    }


A boost can also be associated with the query:


.. code-block:: js


    {
        "prefix" : { "user" :  { "value" : "ki", "boost" : 2.0 } }
    }


Or :


.. code-block:: js


    {
        "prefix" : { "user" :  { "prefix" : "ki", "boost" : 2.0 } }
    }


This multi term query allows to control how it gets rewritten using the :ref:`rewrite <es-guide-reference-query-dsl-multi-term-rewrite>`  parameter.
