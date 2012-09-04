Usage
=====

Creating a connection. (See more details here :ref:`pyes-connections`)

.. code-block:: python

    >>> from pyes import *
    >>> conn = ES('127.0.0.1:9200') #for http

Deleting an index:

.. code-block:: python

    >>> try:
    >>>     conn.delete_index("test-index")
    >>> except:
    >>>     pass

(an exception is raised if the index is not present)

Create an index:

.. code-block:: python

    >>> conn.create_index("test-index")

Creating a mapping via dictionary:

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

Creating a mapping via objects:

.. code-block:: python

    >>> from pyes.mappings import *
    >>> docmapping = DocumentObjectField(name=self.document_type)
    >>> docmapping.add_property(
    >>>     StringField(name="parsedtext", store=True, term_vector="with_positions_offsets", index="analyzed"))
    >>> docmapping.add_property(
    >>>     StringField(name="name", store=True, term_vector="with_positions_offsets", index="analyzed"))
    >>> docmapping.add_property(
    >>>     StringField(name="title", store=True, term_vector="with_positions_offsets", index="analyzed"))
    >>> docmapping.add_property(IntegerField(name="position", store=True))
    >>> docmapping.add_property(StringField(name="uuid", store=True, index="not_analyzed"))
    >>> nested_object = NestedObject(name="nested")
    >>> nested_object.add_property(StringField(name="name", store=True))
    >>> nested_object.add_property(StringField(name="value", store=True))
    >>> nested_object.add_property(IntegerField(name="num", store=True))
    >>> docmapping.add_property(nested_object)
    >>> settings.add_mapping(docmapping)
    >>> conn.ensure_index(self.index_name, settings)


Index some documents:

.. code-block:: python

    >>> conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, "test-index", "test-type", 1)
    >>> conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, "test-index", "test-type", 2)

Refresh an index:

.. code-block:: python

    >>> conn.refresh("test-index")
    >>> conn.refresh(["test-index"])

Execute a query. (See :ref:`pyes-queries`)

.. code-block:: python

    >>> q = TermQuery("name", "joe")
    >>> results = conn.search(query = q)

results is a (See :ref:`pyes-resultset`), you can iterate it. It caches some results and pages them. The default returned objects are ElasticSearchModel (See :ref:`pyes-models`).

Iterate on results:

.. code-block:: python

    >>> for r in results:
    >>>    print r

Execute a query via queryset, via a simple ORM django like interface. (See :ref:`pyes-queryset`)

.. code-block:: python

    >>> model = generate_model("test-index", "test-type")
    >>> results = model.objects.all()
    >>> results = model.objects.filter(name="joe")



The tests directory there are a lot of examples of functionalities.
