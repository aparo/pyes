.. _faq:

============================
 Frequently Asked Questions
============================

.. contents::
    :local:

.. _faq-general:

General
=======

.. _faq-when-to-use:

What connection type should I use?
----------------------------------

For general usage I suggest to use HTTP connection versus your server.

For more fast performance, mainly in indexing, I suggest to use thrift because its latency is lower.

How you can return a plain dict from a resultset?
=================================================

ResultSet iterates on ElasticSearchModel by default, to change this behaviour you need to pass a an object that
receive a connection and a dict object.

To return plain dict object, you must pass to the search call a model parameter:

.. code-block:: python

    model=lambda x,y:y

