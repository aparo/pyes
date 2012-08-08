.. _es-guide-reference-api-search-indices-types:

=============
Indices Types
=============

The search API can be applied to multiple types within an index, and across multiple indices with support for the :ref:`multi index syntax <es-guide-reference-api-multi-index>`.  For example, we can search on all documents across all types within the twitter index:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/_search?q=user:kimchy'


We can also search within specific types:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet,user/_search?q=user:kimchy'


We can also search all tweets with a certain tag across several indices (for example, when each user has his own index):


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/kimchy,elasticsearch/tweet/_search?q=tag:wow'


Or we can search all tweets across all available indices using **_all** placeholder:


.. code-block:: js

    $ curl - XGET 'http://localhost:9200/_all/tweet/_search?q=tag:wow'


Or even search across all indices and all types:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_search?q=tag:wow'

