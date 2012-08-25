=============================
 pyes - Python ElasticSearch
=============================

:Web: http://pypi.python.org/pypi/pyes/
:Download: http://pypi.python.org/pypi/pyes/
:Source: http://github.com/aparo/pyes/
:Documentation: http://packages.python.org/pyes/
:Keywords: search, elastisearch, distribute search

--

pyes is a connector to use elasticsearch from python.

This version requires elasticsearch 0.15 or above.

Features
========

- Thrift/HTTP protocols
- Bulk insert/delete
- Index management
- Every search query types
- Facet Support
- Geolocalization support
- Highlighting
- Percolator
- River support

Documentation
=============

http://pyes.rtfd.org/
http://pyes.readthedocs.org/en/latest/

Changelog
=========

v. 0.19.1:

    Renamed field_name in name in ScriptFields

    Fixed ResultSet slicing.

    Create Manager to manage API action grouped as Elasticsearch.

    Moved tests outside pyes code dir. Update references. Upgraded test elasticsearch to 0.19.9.

    Added documentation links

    Got docs building on readthedocs.org (Wraithan - Chris McDonald)

    Renamed scroll_timeout in scroll

    Moved FacetFactory include

    Renamed field_name in name in ScriptFields

    Using only thrift_connect to manage thrift existence

    Added model and scan to query

    Added exists document call

    Added routing to delete

    Removed minimum_number_should_match parameter.It is not supported by elastic search and causes errors when using a BoolFilter. (Jernej Kos)

    Improved speed json conversion of datetime values

    Add boost argument to TextQuery

    Added boost argument to TextQuery. (Jernej Kos)

    Go back to urllib3 instead of requests. (gsakkis)

    Enhance Twitter River class. (thanks @dendright)

    Add OAuth authentication and filtering abilities to Twitter River. (Jack Riches)

    HasChildFilter expects a Query. (gsakkis)

    Fixed _parent being pulled from _meta rather than the instance itself. (merrellb)

    Add support of all_terms to TermFacet. (mouad)



TODO
----

- add ORM to manage objects
- much more documentation
- add coverage
- add jython native client protocol

License
=======

This software is licensed under the ``New BSD License``. See the ``LICENSE``
file in the top distribution directory for the full license text.

.. # vim: syntax=rst expandtab tabstop=4 shiftwidth=4 shiftround
