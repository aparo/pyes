Nodes Stats
===========

The cluster nodes stats API allows to retrieve one or more (or all) of the cluster nodes statistics.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/nodes/stats'
    
    $ curl -XGET 'http://localhost:9200/_cluster/nodes/nodeId1,nodeId2/stats'


The first command retrieves stats of all the nodes in the cluster. The second commands selectively retrieves nodes stats of only **nodeId1** and **nodeId2**.


The following is a sample response:


.. code-block:: js


    {
      "cluster_name" : "elasticsearch",
      "nodes" : {
        "5fc74788-facf-4c04-9c90-4f4746d6a2b2" : {
          "name" : "Exodus",
          "os" : {
            "timestamp" : 1281993352855,
            "uptime" : "4 hours, 32 minutes and 5 seconds",
            "uptime_in_millis" : 16325000,
            "load_average" : [ 0.58, 0.64, 0.57 ],
            "cpu" : {
              "sys" : 2,
              "user" : 4,
              "idle" : 93
            },
            "mem" : {
              "free" : "1.2gb",
              "free_in_bytes" : 1344806912,
              "used" : "2.4gb",
              "used_in_bytes" : 2663964672,
              "free_percent" : 78,
              "used_percent" : 21,
              "actual_free" : "2.9gb",
              "actual_free_in_bytes" : 3135725568,
              "actual_used" : "832.6mb",
              "actual_used_in_bytes" : 873046016
            },
            "swap" : {
              "used" : "0b",
              "used_in_bytes" : 0,
              "free" : "3.8gb",
              "free_in_bytes" : 4093632512
            }
          },
          "process" : {
            "timestamp" : 1281993352856,
            "cpu" : {
              "percent" : 2,
              "sys" : "12 seconds and 880 milliseconds",
              "sys_in_millis" : 12880,
              "user" : "22 seconds and 60 milliseconds",
              "user_in_millis" : 22060,
              "total" : "-1 milliseconds",
              "total_in_millis" : -1
            },
            "mem" : {
              "resident" : "124.1mb",
              "resident_in_bytes" : 130207744,
              "share" : "9.7mb",
              "share_in_bytes" : 10264576,
              "total_virtual" : "2.3gb",
              "total_virtual_in_bytes" : 2537869312
            },
            "fd" : {
              "total" : 55
            }
          },
          "jvm" : {
            "timestamp" : 1281993352856,
            "uptime" : "31 minutes, 47 seconds and 805 milliseconds",
            "uptime_in_millis" : 1907805,
            "mem" : {
              "heap_used" : "35.4mb",
              "heap_used_in_bytes" : 37157720,
              "heap_committed" : "265.5mb",
              "heap_committed_in_bytes" : 278462464,
              "non_heap_used" : "24.5mb",
              "non_heap_used_in_bytes" : 25762000,
              "non_heap_committed" : "36.9mb",
              "non_heap_committed_in_bytes" : 38789120
            },
            "threads" : {
              "count" : 43,
              "peak_count" : 46
            },
            "gc" : {
              "collection_count" : 8,
              "collection_time" : "212 milliseconds",
              "collection_time_in_millis" : 212,
              "collectors" : {
                "ParNew" : {
                  "collection_count" : 7,
                  "collection_time" : "82 milliseconds",
                  "collection_time_in_millis" : 82
                },
                "ConcurrentMarkSweep" : {
                  "collection_count" : 1,
                  "collection_time" : "130 milliseconds",
                  "collection_time_in_millis" : 130
                }
              }
            }
          },
          "network" : {
            "tcp" : {
              "active_opens" : 3228,
              "passive_opens" : 163,
              "curr_estab" : 31,
              "in_segs" : 219644,
              "out_segs" : 159961,
              "retrans_segs" : 3977,
              "estab_resets" : 107,
              "attempt_fails" : 34,
              "in_errs" : 0,
              "out_rsts" : 1475
            }
          },
          "thread_pool" : {
            "pool_size" : 1,
            "active_count" : 1,
            "scheduler_pool_size" : 20,
            "scheduler_active_count" : 0
          },
          "transport" : {
            "rx_count" : 3796,
            "rx_size" : "258.8kb",
            "rx_size_in_bytes" : 265024,
            "tx_count" : 3797,
            "tx_size" : "171kb",
            "tx_size_in_bytes" : 175167
          }
        },
        "9a7ef95c-0714-476c-9ac0-f342581916e2" : {
          "name" : "Human Torch II",
          "os" : {
            "timestamp" : 1281993352855,
            "uptime" : "4 hours, 32 minutes and 5 seconds",
            "uptime_in_millis" : 16325000,
            "load_average" : [ 0.58, 0.64, 0.57 ],
            "cpu" : {
              "sys" : 2,
              "user" : 4,
              "idle" : 93
            },
            "mem" : {
              "free" : "1.2gb",
              "free_in_bytes" : 1344806912,
              "used" : "2.4gb",
              "used_in_bytes" : 2663964672,
              "free_percent" : 78,
              "used_percent" : 21,
              "actual_free" : "2.9gb",
              "actual_free_in_bytes" : 3135725568,
              "actual_used" : "832.6mb",
              "actual_used_in_bytes" : 873046016
            },
            "swap" : {
              "used" : "0b",
              "used_in_bytes" : 0,
              "free" : "3.8gb",
              "free_in_bytes" : 4093632512
            }
          },
          "process" : {
            "timestamp" : 1281993352856,
            "cpu" : {
              "percent" : 1,
              "sys" : "13 seconds and 20 milliseconds",
              "sys_in_millis" : 13020,
              "user" : "21 seconds and 470 milliseconds",
              "user_in_millis" : 21470,
              "total" : "-1 milliseconds",
              "total_in_millis" : -1
            },
            "mem" : {
              "resident" : "119.6mb",
              "resident_in_bytes" : 125485056,
              "share" : "9.7mb",
              "share_in_bytes" : 10252288,
              "total_virtual" : "2.3gb",
              "total_virtual_in_bytes" : 2537869312
            },
            "fd" : {
              "total" : 50
            }
          },
          "jvm" : {
            "timestamp" : 1281993352856,
            "uptime" : "31 minutes, 43 seconds and 431 milliseconds",
            "uptime_in_millis" : 1903431,
            "mem" : {
              "heap_used" : "26.1mb",
              "heap_used_in_bytes" : 27435288,
              "heap_committed" : "265.5mb",
              "heap_committed_in_bytes" : 278462464,
              "non_heap_used" : "23.1mb",
              "non_heap_used_in_bytes" : 24282512,
              "non_heap_committed" : "36.9mb",
              "non_heap_committed_in_bytes" : 38785024
            },
            "threads" : {
              "count" : 41,
              "peak_count" : 46
            },
            "gc" : {
              "collection_count" : 8,
              "collection_time" : "177 milliseconds",
              "collection_time_in_millis" : 177,
              "collectors" : {
                "ParNew" : {
                  "collection_count" : 7,
                  "collection_time" : "82 milliseconds",
                  "collection_time_in_millis" : 82
                },
                "ConcurrentMarkSweep" : {
                  "collection_count" : 1,
                  "collection_time" : "95 milliseconds",
                  "collection_time_in_millis" : 95
                }
              }
            }
          },
          "network" : {
            "tcp" : {
              "active_opens" : 3228,
              "passive_opens" : 163,
              "curr_estab" : 31,
              "in_segs" : 219644,
              "out_segs" : 159961,
              "retrans_segs" : 3977,
              "estab_resets" : 107,
              "attempt_fails" : 34,
              "in_errs" : 0,
              "out_rsts" : 1475
            }
          },
          "thread_pool" : {
            "pool_size" : 1,
            "active_count" : 1,
            "scheduler_pool_size" : 20,
            "scheduler_active_count" : 0
          },
          "transport" : {
            "rx_count" : 3797,
            "rx_size" : "171kb",
            "rx_size_in_bytes" : 175167,
            "tx_count" : 3796,
            "tx_size" : "258.8kb",
            "tx_size_in_bytes" : 265024
          }
        }
      }
    }

