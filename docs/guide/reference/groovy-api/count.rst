.. _es-guide-reference-groovy-api-count:

=====
Count
=====

The count API is very similar to the :ref:`Java count API <es-guide-reference-groovy-api-guide-reference-java-api-count>`.  The Groovy extension allows to provide the query to execute as a **Closure** (similar to GORM criteria builder):


.. code-block:: js

    def count = client.count {
        indices "test"
        types "type1"
        query {
            term {
                test = "value"
            }
        }
    }


The query follows the same :ref:`Query DSL <es-guide-reference-groovy-api-guide-reference-query-dsl>`.  
