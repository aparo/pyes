==========
Threadpool
==========

A node holds several thread pools in order to improve how threads are managed and memory consumption within a node. There are several thread pools, but the important ones include:


* **index**: for index/delete/bulk operations.
* **search**:  For get/count/search operations.

Each pool can have a type associated with it, and based on the type, associated parameters. The types can be **cached**, **fixed**, **scaling**, and **blocking**.