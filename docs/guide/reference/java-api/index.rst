.. _es-guide-reference-java-api-index:
.. _es-guide-reference-java-api:

========
Java Api
========

This section describes the Java API that elasticsearch provides. All elasticsearch operations are executed using a :ref:`Client <es-guide-reference-java-api-client>`  object. All operations are completely asynchronous in nature (either accepts a listener, or return a future).  


Additionally, operations on a client may be accumulated and executed in :ref:`Bulk <es-guide-reference-java-api-bulk>`.   


Note, all the :ref:`APIs <es-guide-reference-java-api>`  are exposed through the Java API (actually, the Java API is used internally to execute them).


Maven Repository
----------------

elasticsearch is hosted on `Sonatype <http://www.sonatype.org/>`_,  with both a `releases repo <http://oss.sonatype.org/content/repositories/releases/>`_  and a `snapshots repo <http://oss.sonatype.org/content/repositories/snapshots>`_.  


.. toctree::
    :maxdepth: 1

    bulk
    client
    count
    delete-by-query
    delete
    get
    index_
    percolate
    query-dsl
    search
