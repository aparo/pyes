.. _pyes-models:

Models
======

DotDict
-------

The DotDict is the base model used. It allows to use a dict with the DotNotation.

.. code-block:: python

    >>> dotdict = DotDict(foo="bar")
    >>> dotdict2 = deepcopy(dotdict)
    >>> dotdict2["foo"] = "baz"
    >>> dotdict.foo = "bar"
    >>> dotdict2.foo== "baz"
        True

ElasticSearchModel
------------------

It extends DotDict adding methods for common uses.

Every search return an ElasticSearchModel as result. Iterating on results, you iterate on ElasticSearchModel objects.

You can create a new one with the factory or get one by search/get methods.

.. code-block:: python

        obj = self.conn.factory_object(self.index_name, self.document_type, {"name": "test", "val": 1})
        assert obj.name=="test"

You can change value via dot notation or dictionary.

.. code-block:: python

        obj.name = "aaa"
        assert obj.name == "aaa"
        assert obj.val == 1

You can change ES info via ._meta property or get_meta call.

.. code-block:: python

        assert obj._meta.id is None
        obj._meta.id = "dasdas"
        assert obj._meta.id == "dasdas"

Remember that it works as a dict object.

.. code-block:: python

        assert sorted(obj.keys()) == ["name", "val"]

You can save it.

.. code-block:: python

        obj.save()
        obj.name = "test2"
        obj.save()

        reloaded = self.conn.get(self.index_name, self.document_type, obj._meta.id)
        assert reloaded.name, "test2")
