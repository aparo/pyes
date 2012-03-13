.. _es-guide-reference-index-modules-slowlog:

=======
Slowlog
=======

Search Slow Log
===============

Shard level slow search log allows to log slow search (query and fetch executions) into a dedicated log file.


Thresholds can be set for both the query phase of the execution, and fetch phase, here is a sample:


.. code-block:: js

    #index.search.slowlog.threshold.query.warn: 10s
    #index.search.slowlog.threshold.query.info: 5s
    #index.search.slowlog.threshold.query.debug: 2s
    #index.search.slowlog.threshold.query.trace: 500ms
    
    #index.search.slowlog.threshold.fetch.warn: 1s
    #index.search.slowlog.threshold.fetch.info: 800ms
    #index.search.slowlog.threshold.fetch.debug: 500ms
    #index.search.slowlog.threshold.fetch.trace: 200ms


By default, none are enabled (set to **-1**). Levels (**warn**, **info**, **debug**, **trace**) allow to control under which logging level the log will be logged. Not all are required to be configured (for example, only **warn** threshold can be set). The benefit of several levels is the ability to quickly "grep" for specific thresholds breached.


The logging is done on the shard level scope, meaning the execution of a search request within a specific shard. It does not encompass the whole search request, which can be broadcast to several shards in order to execute. Some of the benefits of shard level logging is the association of the actual execution on the specific machine, compared with request level.


All settings are index level settings (and each index can have different values for it), and can be changed in runtime using the index update settings API.


The logging file is configured by default using the following configuration (found in **logging.yml**):


.. code-block:: js

    index_search_slow_log_file:
      type: dailyRollingFile
      file: ${path.logs}/${cluster.name}_index_search_slowlog.log
      datePattern: "'.'yyyy-MM-dd"
      layout:
        type: pattern
        conversionPattern: "[%d{ISO8601}][%-5p][%-25c] %m%n"

