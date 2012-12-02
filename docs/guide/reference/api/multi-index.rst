.. _es-guide-reference-api-multi-index:
.. _es-guide-reference-api-multi:

===========
Multi Index
===========

Many of elasticearch APIs support operating across several indices. The format usually includes an index name, or a comma separated index names. It also supports using aliases, or a comma delimited list of aliases and indexes for the APIs.


Using the APIs against all indices is simple by usually either using the **_all** index, or simply omitting the index.


For multi index APIs (like search), there is also support for using wildcards (since **0.19.8**) in order to resolve indices and aliases. For example, if we have an indices **test1**, **test2** and **test3**, we can simply specify **test*** and automatically operate on all of them. The syntax also support the ability to add (**+**) and remove (**-**), for example: **+test*,-test3**.

