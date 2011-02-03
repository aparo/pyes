Count
=====

The count API is very similar to the :doc:`Java count API </elasticsearch/java_api/count/index>`. The Groovy extension allows to provide the query to execute as a **Closure** (similar to GORM criteria builder):


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


The query follows the same :doc:`JSON Query DSL </elasticsearch/rest_api/query_dsl/index>` provided for the REST API.

