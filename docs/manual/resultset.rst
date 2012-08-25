.. _pyes-resultset:

ResultSet
=========

This object is returned as result of a query. It's lazy.

.. code-block:: python

    >>> resultset = self.conn.search(Search(MatchAllQuery(), size=20), self.index_name, self.document_type)

It contains the matched and limited records. Very useful to use in pagination.

.. code-block:: python

    >>> len([p for p in resultset])
    20

The total matched results is in the total property.

.. code-block:: python

    >>> resultset.total
    1000

You can slice it.

.. code-block:: python

    >>> resultset = self.conn.search(Search(MatchAllQuery(), size=10), self.index_name, self.document_type)
    >>> len([p for p in resultset[:10]])
    10

Remember all result are default ElasticSearchModel objects

.. code-block:: python

    >>> resultset[10].uuid
    "11111"

