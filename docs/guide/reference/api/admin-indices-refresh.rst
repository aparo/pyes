=====================
Admin Indices Refresh
=====================

The refresh API allows to explicitly refresh one or more index, making all operations performed since the last refresh available for search. The (near) real-time capabilities depends on the index engine used. For example, the robin one requires refresh to be called, but by default a refresh is scheduled periodically.


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/_refresh'


Multi Index
-----------

The refresh API can be applied to more than one index with a single call, or even on **_all** the indices.


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/kimchy,elasticsearch/_refresh'
    
    $ curl -XPOST 'http://localhost:9200/_refresh'

