Nodes Info
==========

The cluster nodes info API allows to retrieve one or more (or all) of the cluster nodes information.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/nodes'
    
    $ curl -XGET 'http://localhost:9200/_cluster/nodes/nodeId1,nodeId2'


The first command retrieves information of all the nodes in the cluster. The second commands selectively retrieves nodes information of only **nodeId1** and **nodeId2**.


The following is a sample response:


.. code-block:: js


    {
      "cluster_name" : "elasticsearch",
      "nodes" : {
        "5fc74788-facf-4c04-9c90-4f4746d6a2b2" : {
          "name" : "Exodus",
          "transport_address" : "inet[127.0.0.1/127.0.0.1:9300]",
          "attributes" : {
          },
          "http_address" : "inet[127.0.0.1/127.0.0.1:9200]",
          "os" : {
            "cpu" : {
              "vendor" : "Intel",
              "model" : "Core(TM)2 Duo CPU     T9600  ** 2.80GHz",
              "mhz" : 2801,
              "total_cores" : 2,
              "total_sockets" : 1,
              "cores_per_socket" : 2,
              "cache_size" : "6kb",
              "cache_size_in_bytes" : 6144
            },
            "mem" : {
              "total" : "3.7gb",
              "total_in_bytes" : 4008771584
            },
            "swap" : {
              "total" : "3.8gb",
              "total_in_bytes" : 4093632512
            }
          },
          "process" : {
            "id" : 5009
          },
          "jvm" : {
            "pid" : 5009,
            "vm_name" : "OpenJDK 64-Bit Server VM",
            "vm_version" : "14.0-b16",
            "vm_vendor" : "Sun Microsystems Inc.",
            "start_time" : 1281991445051
          },
          "network" : {
            "primary_interface" : {
              "address" : "192.168.2.3",
              "name" : "wlan0",
              "mac_address" : "00:1E:65:38:82:FC"
            }
          },
          "thread_pool" : {
            "type" : "cached",
            "min_threads" : 0,
            "max_threads" : -1,
            "scheduler_threads" : 20
          },
          "transport" : {
            "bound_address" : "inet[/0:0:0:0:0:0:0:0:9300]",
            "publish_address" : "inet[127.0.0.1/127.0.0.1:9300]"
          }
        },
        "9a7ef95c-0714-476c-9ac0-f342581916e2" : {
          "name" : "Human Torch II",
          "transport_address" : "inet[/127.0.0.1:9301]",
          "attributes" : {
          },
          "http_address" : "inet[127.0.0.1/127.0.0.1:9201]",
          "os" : {
            "cpu" : {
              "vendor" : "Intel",
              "model" : "Core(TM)2 Duo CPU     T9600  ** 2.80GHz",
              "mhz" : 2801,
              "total_cores" : 2,
              "total_sockets" : 1,
              "cores_per_socket" : 2,
              "cache_size" : "6kb",
              "cache_size_in_bytes" : 6144
            },
            "mem" : {
              "total" : "3.7gb",
              "total_in_bytes" : 4008771584
            },
            "swap" : {
              "total" : "3.8gb",
              "total_in_bytes" : 4093632512
            }
          },
          "process" : {
            "id" : 5061
          },
          "jvm" : {
            "pid" : 5061,
            "vm_name" : "OpenJDK 64-Bit Server VM",
            "vm_version" : "14.0-b16",
            "vm_vendor" : "Sun Microsystems Inc.",
            "start_time" : 1281991449425
          },
          "network" : {
            "primary_interface" : {
              "address" : "192.168.2.3",
              "name" : "wlan0",
              "mac_address" : "00:1E:65:38:82:FC"
            }
          },
          "thread_pool" : {
            "type" : "cached",
            "min_threads" : 0,
            "max_threads" : -1,
            "scheduler_threads" : 20
          },
          "transport" : {
            "bound_address" : "inet[/0:0:0:0:0:0:0:0:9301]",
            "publish_address" : "inet[/127.0.0.1:9301]"
          }
        }
      }
    }

