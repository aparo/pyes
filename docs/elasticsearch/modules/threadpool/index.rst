ThreadPool Module
=================

The thread pool module allows to control the thread pool type that will be used by the node in order to execute long or non CPU blocking operations. It also allows for scheduled execution of tasks.


The type of the thread pool can be controlled using **threadpool.type** setting, with the following types supported (**cached** is the default):


=====================================  =================================
 Type                                   Description                     
=====================================  =================================
:doc:`cached <./cached/index>`         A cached unbounded thread pool.  
:doc:`scaling <./scaling/index>`       A bounded scaling thread pool.   
:doc:`blocking <./blocking/index>`     A bounded blocking thread pool.  
=====================================  =================================
