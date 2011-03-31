===============
Span Term Query
===============

Matches spans containing a term. The span term query maps to Lucene **SpanTermQuery**. Here is an example:


.. code-block:: js


    {
        "span_term" : { "user" : "kimchy" }
    }    


A boost can also be associated with the query:


.. code-block:: js


    {
        "span_term" : { "user" : { "value" : "kimchy", "boost" : 2.0 } }
    }    


Or :


.. code-block:: js


    {
        "span_term" : { "user" : { "term" : "kimchy", "boost" : 2.0 } }
    }    

