.. _es-guide-reference-java-api-index:

========
Java Api
========

This section describes the Java API elasticsearch provides. All of elasticsearch APIs are executed using a :ref:`Client <es-guide-reference-java-api-client>`,  and are completely asynchronous in nature (either accepts a listener, or return a future).


Note, all the :ref:`APIs <es-guide-reference-api-index>`  are exposed through the Java API (actually, the Java API is used internally to execute them).


Maven Repository
----------------

elasticsearch is hosted on `Sonatype <http://www.sonatype.org/>`_,  with both a `releases repo <http://oss.sonatype.org/content/repositories/releases/>`_  and a `snapshots repo <http://oss.sonatype.org/content/repositories/snapshots>`_.  


.. toctree::
    :maxdepth: 1

    client
    count
    delete-by-query
    delete
    get
    index_
    query-dsl
    search
