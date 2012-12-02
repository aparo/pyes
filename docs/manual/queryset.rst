.. _pyes-queryset:

Queryset
========

Creating a connection:

.. code-block:: python

    >>> from pyes.queryset import generate_model
    >>> model = generate_model("myindex", "mytype")


Filtering:

.. code-block:: python

   >>> results = model.objects.all()
   >>> len(results)
   3
   >>> results = model.objects.filter("name", "joe")
   >>> len(results)
   1
   >>> results = model.objects.filter(uuid="33333")
   >>> len(results)
   1
   >>> results = model.objects.filter(position=1).filter(position=3)
   >>> len(results)
   0
   >>> results = model.objects.filter(position__gt=1, position__lt=3)
   >>> len(results)
   1
   >>> results.count()
   1
   >>> [r.position for r in results]
   [2]
   >>> results = model.objects.exclude(position__in=[1, 2])
   >>> len(results)
   1
   >>> results.count()
   1

Retrieve an item:

.. code-block:: python

   >>> item = model.objects.get(position=1)
   >>> item.position
   1
   >>> item = model.objects.get(position=0)
   raise DoesNotExist


Ordering:

.. code-block:: python

   >>> items = model.objects.order_by("position")
   >>> items[0].position
   1
   >>> items = model.objects.order_by("-position")
   >>> items[0].position
   3

Get or create:

.. code-block:: python

   >>> item, created = model.objects.get_or_create(position=1, defaults={"name": "nasty"})
   >>> created
   False
   >>> position
   1
   >>> item.get_meta().id
   "1"

   >>> item, created = model.objects.get_or_create(position=10, defaults={"name": "nasty"})
   >>> created
   True
   >>> position
   10
   >>> item.name
   "nasty"

Returns values:

.. code-block:: python

   >>> values = list(model.objects.values("uuid", "position"))
   >>> len(values)
   3
   >>> list(values)
   [{u'position': 1, u'uuid': u'11111'},{u'position': 2, u'uuid': u'22222'},{u'position': 3, u'uuid': u'33333'}]
   >>> values = list(model.objects.values_list("uuid", flat=True))
   >>> len(values)
   3
   >>> list(values)
   [u'11111', u'22222',u'33333']
   >>> model.objects.dates("date", kind="year")
   >>> len(values)
   1
   >>> list(values)
   [datetime(2012, 1, 1, 1, 0)]


        facets = model.objects.facet("uuid").size(0).facets
        uuid_facets=facets["uuid"]
        self.assertEqual(uuid_facets["total"], 3)
        self.assertEqual(uuid_facets["terms"][0]["count"], 1)


Faceting counting (can be concatenated).

.. code-block:: python

   >>> facets = model.objects.facet("uuid").size(0).facets
   >>> facets["uuid"]["total"]
   3
   >>> facets["uuid"][0]["count"]
   1


More examples are available in test_queryset.py in tests dir.
