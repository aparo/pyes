.. _pyes-queryset:

Queryset
========

Creating a model
----------------

Creating a connection:

.. code-block:: python

    >>> from pyes.queryset import generate_model
    >>> model = generate_model("myindex", "mytype")


Filtering
---------

Filters can concatened

.. code-block:: python

   >>> results = model.objects.filter("name", "joe")
   >>> results = model.objects.filter("name", "joe").filter("uuid", 2)
   >>> results = model.objects.filter("name", "joe").exclude("uuid", 2)


Faceting
--------

Term filtering.

.. code-block:: python

   >>> facets = model.objects.filter("name", "joe").facet("uuid").facets

More examples are available in test_queryset.py in tests dir.
