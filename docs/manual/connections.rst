Connections
===========

Import the module:

    >>> import pyes

pyes is able to use standard http or thrift protocol. If your port starts with "92" http protocol is used, otherwise thrift.


For a single connection (which is _not_ thread-safe), pass a list of servers.

For thrift:

.. code-block:: python

    >>> conn = pyes.ES() # Defaults to connecting to the server at '127.0.0.1:9500'
    >>> conn = pyes.ES(['127.0.0.1:9500'])

For http:

.. code-block:: python

    >>> conn = pyes.ES(['127.0.0.1:9200'])

Connections are robust to server failures. Upon a disconnection, it will attempt to connect to each server in the list in turn. If no server is available, it will raise a NoServerAvailable exception.

Timeouts are also supported and should be used in production to prevent a thread from freezing while waiting for the server to return.

.. code-block:: python

    >>> conn = pyes.ES(timeout=3.5) # 3.5 second timeout
    (Make some pyes calls and the connection to the server suddenly becomes unresponsive.)

    Traceback (most recent call last):
    ...
    pyes.connection.NoServerAvailable

Note that this only handles socket timeouts.
