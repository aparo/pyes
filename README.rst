=============================
 pyes - Python ElasticSearch
=============================

:Web: http://pypi.python.org/pypi/pyes/
:Download: http://pypi.python.org/pypi/pyes/
:Source: http://github.com/aparo/pyes/
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


Changelog
=========

v. 0.18.7-rc1:

    Tested against 0.18.7, with all tests passing

    Added support for index_stats

v. 0.17.0:

    API BREAKING: Added new searcher iterator API. (To use the old code rename ".search" in ".search_raw")

    Tests refactory.

TODO
----

- add coverage
- add jython native client protocol

License
=======

This software is licensed under the ``New BSD License``. See the ``LICENSE``
file in the top distribution directory for the full license text.

.. # vim: syntax=rst expandtab tabstop=4 shiftwidth=4 shiftround
