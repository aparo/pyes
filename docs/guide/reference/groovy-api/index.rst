.. _es-guide-reference-groovy-api-index:
.. _es-guide-reference-groovy-api:

==========
Groovy Api
==========

This section describes the `Groovy <http://groovy.codehaus.org/>`_  API elasticsearch provides. All of elasticsearch APIs are executed using a :ref:`GClient <es-guide-reference-groovy-api-client>`,  and are completely asynchronous in nature (either accepts a listener, or return a future).


The Groovy API is a wrapper on top of the :ref:`Java API <es-guide-reference-java-api>`  exposing it in a groovier manner. The execution options for each API follow a similar manner and covered in :ref:`the anatomy of a Groovy API <es-guide-reference-groovy-api-anatomy>`.

Maven Repository
----------------

elasticsearch is hosted on `Sonatype <http://www.sonatype.org/>`_,  with both a `releases repo <http://oss.sonatype.org/content/repositories/releases/>`_  and a `snapshots repo <http://oss.sonatype.org/content/repositories/snapshots>`_.


.. toctree::
    :maxdepth: 1

    anatomy
    client
    count
    delete
    get
    index_
    search
