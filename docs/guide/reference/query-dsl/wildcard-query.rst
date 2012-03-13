.. _es-guide-reference-query-dsl-wildcard-query:

==============
Wildcard Query
==============

Matches documents that have fields matching a wildcard expression (*not analyzed*). Supported wildcards are *****, which matches any character sequence (including the empty one), and **?**, which matches any single character. Note this query can be slow, as it needs to iterate over many terms. In order to prevent extremely slow wildcard queries, a wildcard term should not start with one of the wildcards ***** or **?**. The wildcard query maps to Lucene **WildcardQuery**.


.. code-block:: js


    {
        "wildcard" : { "user" : "ki*y" }
    }


A boost can also be associated with the query:


.. code-block:: js


    {
        "wildcard" : { "user" : { "value" : "ki*y", "boost" : 2.0 } }
    }    


Or :


.. code-block:: js


    {
        "wildcard" : { "user" : { "wildcard" : "ki*y", "boost" : 2.0 } }
    }    


This multi term query allows to control how it gets rewritten using the :ref:`rewrite <es-guide-reference-query-dsl-multi-term-rewrite>`  query-dsl-multi-term-rewrite>`  parameter.
