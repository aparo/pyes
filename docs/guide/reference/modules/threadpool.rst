.. _es-guide-reference-modules-threadpool:

==========
Threadpool
==========

A node holds several thread pools in order to improve how threads are managed and memory consumption within a node. There are several thread pools, but the important ones include:


* **index**: For index/delete operations (defaults to **cached** type).
* **search**: For get/count/search operations (defaults to **cached** type).
* **bulk**: For bulk operations (defaults to **cached** type).
* **refresh**: For refresh operations (defaults to **cached** type).

Changing a specific thread pool can be done by setting its type and specific type parameters, for example, changing the **index** thread pool to **blocking** type:


.. code-block:: js

    threadpool:
        index:
            type: blocking
            min: 1
            size: 30
            wait_time: 30s


The following are the types of thread pools that can be used and their respective parameters:


cache
-----

The **cache** thread pool is an unbounded thread pool that will spawn a thread if there are pending requests. Here is an example of how to set it:


.. code-block:: js

    threadpool:
        index:
            type: cached


fixed
-----

The **fixed** thread pool holds a fixed size of threads to handle the requests with a queue (optionally bounded) for pending requests that have no threads to service them.


The **size** parameter controls the number of threads, and defaults to the number of cores times 5.


The **queue_size** allows to control the size of the queue of pending requests that have no threads to execute them. By default, it is set to **-1** which means its unbounded. When a request comes in and the queue is full, the **reject_policy** parameter can control how it will behave. The default, **abort**, will simply fail the request. Setting it to **caller** will cause the request to execute on an IO thread allowing to throttle the execution on the networking layer.


.. code-block:: js

    threadpool:
        index:
            type: fixed
            size: 30
            queue: 1000
            reject_policy: caller


blocking
--------

The **blocking** pool allows to configure a **min** (defaults to **1**) and **size** (defaults to the number of cores times 5) parameters for the number of threads. 


It also has a backlog queue with a default **queue_size** of **1000**. Once the queue is full, it will wait for the provided **wait_time** (defaults to **60s**) on the calling IO thread, and fail if it has not been executed.


.. code-block:: js

    threadpool:
        index:
            type: blocking
            min: 1
            size: 30
            wait_time: 30s

