===============
Match All Query
===============

A query that matches all documents. Maps to Lucene **MatchAllDocsQuery**.


.. code-block:: js


    {
        "match_all" : { }
    }


Which can also have boost associated with it:


.. code-block:: js


    {
        "match_all" : { "boost" : 1.2 }
    }

