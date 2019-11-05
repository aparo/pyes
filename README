=============================
 pyes - Python ElasticSearch
=============================

:Web: http://pypi.python.org/pypi/pyes/
:Download: http://pypi.python.org/pypi/pyes/
:Source: http://github.com/aparo/pyes/
:Documentation: http://pyes.rtfd.org/
:Keywords: search, elastisearch, distribute search

--

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/aparo/pyes?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

pyes is a pythonic way to use ElasticSearch since 2010. 

This version requires elasticsearch 1.x or above. It's a pre release for pyes 1.x. Give a look to migrations documentation to upgrade you code for ElasticSearch 1.x.

We are working to provide full support to ElasticSearch 1.x (check the develop branch: we are using the git-flow workflow) that'll have:

- connection based on Official ElasticSearch client ??
- full support to ElasticSearch 1.x (removed old support due incompatibility with old version of ES)
- migration from multi_field to >field>.fields
- refactory of old code to be more pythonic
- performance improvements


Features
========

- Python3 support (only HTTP, thrift lib is not available on python3)
- Thrift/HTTP protocols
- Bulk insert/delete
- Index management
- Every search query types
- Facet Support
- Aggregation Support
- Geolocalization support
- Highlighting
- Percolator
- River support

Changelog
=========

v. 0.99.0:

    Migrated many code to ElasticSearch 1.x

    Full coverage for actual queries

v. 0.99:

    Added aggregation

    Fix for python3 compatibility

    Upgraded code to use ElasticSearch 1.x or above

v. 0.90.1:

    Bug Fix releases for some python3 introduced regression

v. 0.90.0:

    A lot of improvements.

    Python 3 support.

Migration to version 0.99
=========================

CustomScoreQuery has been removed. The FunctionScoreQuery with its functions cover the previous functionalities.
For scripting use ScriptScoreFunction.




TODO
----

- much more documentation
- add coverage
- add jython native client protocol

License
=======

This software is licensed under the ``New BSD License``. See the ``LICENSE``
file in the top distribution directory for the full license text.

.. # vim: syntax=rst expandtab tabstop=4 shiftwidth=4 shiftround
