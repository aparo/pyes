Usage
=====

Creating a connection:

.. code-block:: python

    >>> from pyes import *
    >>> conn = ES('127.0.0.1:9200')

Deleting an index:

.. code-block:: python

    >>> try:
    >>>     conn.delete_index("test-index")
    >>> except:
    >>>     pass

(an exception is fored if the index is not present)

Create an index:

.. code-block:: python

    >>> conn.create_index("test-index")

Creating a mapping:

.. code-block:: python

    >>> mapping = { u'parsedtext': {'boost': 1.0,
    >>>                  'index': 'analyzed',
    >>>                  'store': 'yes',
    >>>                  'type': u'string',
    >>>                  "term_vector" : "with_positions_offsets"},
    >>>          u'name': {'boost': 1.0,
    >>>                     'index': 'analyzed',
    >>>                     'store': 'yes',
    >>>                     'type': u'string',
    >>>                     "term_vector" : "with_positions_offsets"},
    >>>          u'title': {'boost': 1.0,
    >>>                     'index': 'analyzed',
    >>>                     'store': 'yes',
    >>>                     'type': u'string',
    >>>                     "term_vector" : "with_positions_offsets"},
    >>>          u'pos': {'store': 'yes',
    >>>                     'type': u'integer'},
    >>>          u'uuid': {'boost': 1.0,
    >>>                    'index': 'not_analyzed',
    >>>                    'store': 'yes',
    >>>                    'type': u'string'}}
    >>> conn.put_mapping("test-type", {'properties':mapping}, ["test-index"])

Index some documents:

.. code-block:: python

    >>> conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, "test-index", "test-type", 1)
    >>> conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, "test-index", "test-type", 2)

Refresh an index:

.. code-block:: python

    >>> conn.refresh(["test-index"])

Execute a query

.. code-block:: python

    >>> q = TermQuery("name", "joe")
    >>> results = conn.search(query = q)

Iterate on results:

.. code-block:: python

    >>> for r in results:
    >>>    print r

For more examples looks at the tests.
