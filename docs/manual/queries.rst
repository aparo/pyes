Queries
=======

Indexing data
-------------

Before query data you should put some data in ElasticSearch.

Creating a connection:

.. code-block:: python

    >>> from pyes import *
    >>> conn = ES('127.0.0.1:9200')


Create an index

.. code-block:: python

   >>> conn.create_index("test-index")


Putting some document type.

.. code-block:: python

   >>> mapping = { u'parsedtext': {'boost': 1.0,
                         'index': 'analyzed',
                         'store': 'yes',
                         'type': u'string',
                         "term_vector" : "with_positions_offsets"},
                 u'name': {'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "term_vector" : "with_positions_offsets"},
                 u'title': {'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "term_vector" : "with_positions_offsets"},
                 u'pos': {'store': 'yes',
                            'type': u'integer'},
                 u'uuid': {'boost': 1.0,
                           'index': 'not_analyzed',
                           'store': 'yes',
                           'type': u'string'}}
   >>> conn.put_mapping("test-type", {'properties':mapping}, ["test-index"])
   >>> conn.put_mapping("test-type2", {"_parent" : {"type" : "test-type"}}, ["test-index"])

Index some data:

.. code-block:: python

   >>> conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, "test-index", "test-type", 1)
   >>> conn.index({"name":"data1", "value":"value1"}, "test-index", "test-type2", 1, parent=1)
   >>> conn.index({"name":"Bill Baloney", "parsedtext":"Bill Testere nice guy", "uuid":"22222", "position":2}, "test-index", "test-type", 2)
   >>> conn.index({"name":"data2", "value":"value2"}, "test-index", "test-type2", 2, parent=2)
   >>> conn.index({"name":"Bill Clinton", "parsedtext":"""Bill is not
                nice guy""", "uuid":"33333", "position":3}, "test-index", "test-type", 3)

TIP: you can define deafult search indices setting the default_indices variable.

.. code-block:: python

   >>> conn.default_indices=["test-index"]

TIP: Remember to refresh the index before query to obtain latest insert document

.. code-block:: python

   >>> conn.refresh()


Quering
-------

You can query ES with :

    - a Query object or derivated

    - a Search object or derivated

    - a dict

    - a json string

A Query wrapped in a Search it's the more safe and simple way.


Execute a query

.. code-block:: python

    >>> q = TermQuery("name", "joe")
    >>> results = self.conn.search(query = q)

Iterate on results:

.. code-block:: python

    >>> for r in results:
    >>>    print r

For more examples looks at the tests.
