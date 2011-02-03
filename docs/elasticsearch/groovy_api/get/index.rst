Get
===

The get API is very similar to the :doc:`Java get API </elasticsearch/java_api/get/index>`. The main benefit of using groovy is handling the source content. It can be automatically converted to a **Map** which means using Groovy to navigate it is simple:


.. code-block:: js

    def getF = node.client.get {
        index "test"
        type "type1"
        id "1"
    }
    
    println "Result of field2: $getF.response.source.complex.field2"

