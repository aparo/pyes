.. _es-guide-reference-java-api-client:

======
Client
======

Obtaining an elasticsearch **Client** is simple. The most common way to get a client is by 1) creating an embedded **Node** that acts as a node within a cluster and 2) requesting a **Client** from your embedded **Node**. Another manner is by creating a **TransportClient** that connects to a cluster.


Node Client
===========

Instantiating a node based client is the simplest way to get a **Client** that can execute operations against elasticsearch.


.. code-block:: java


    import static org.elasticsearch.node.NodeBuilder.*;
    
    // on startup
    
    Node node = nodeBuilder().node();
    Client client = node.client();
    
    // on shutdown
    
    node.close();


When you start a **Node**, it joins an elasticsearch cluster. You can have different clusters by simple setting the **cluster.name** setting, or explicitly using the **clusterName** method on the builder. The benefit of using the **Client** is the fact that operations are automatically routed to the node(s) the operations need to be executed on, without performing a "double hop". For example, the index operation will automatically be executed on the shard that it will end up existing at.


When you start a **Node**, the most important decision is whether it should hold data or not. In other words, should indices and shards be allocated to it. Many times we would like to have the clients just be clients, without shards being allocated to them. This is simple to configure by setting either **node.data** setting to **false** or **node.client** to **true** (the **NodeBuilder** respective helper methods on it):


.. code-block:: java


    import static org.elasticsearch.node.NodeBuilder.*;
    
    // on startup
    
    Node node = nodeBuilder().client(true).node();
    Client client = node.client();
    
    // on shutdown
    
    node.close();


Another common usage is to start the **Node** and use the **Client** in unit/integration tests. In such a case, we would like to start a "local" **Node** (with a "local" discovery and transport). Again, this is just a matter of a simple setting when starting the **Node**. Note, "local" here means local on the JVM (well, actually class loader) level, meaning that two *local* servers started within the same JVM will discover themselves and form a cluster.


.. code-block:: java


    import static org.elasticsearch.node.NodeBuilder.*;
    
    // on startup
    
    Node node = nodeBuilder().local(true).node();
    Client client = node.client();
    
    // on shutdown
    
    node.close();



Transport Client
================

The **TransportClient** connects remotely to an elasticsearch cluster using the transport module. It does not join the cluster, but simply gets one or more initial transport addresses and communicates with them in round robin fashion on each action (though most actions will probably be "two hop" operations).


.. code-block:: java


    // on startup    
        
    Client client = new TransportClient()
            .addTransportAddress(new InetSocketTransportAddress("host1", 9300))
            .addTransportAddress(new InetSocketTransportAddress("host2", 9300));
    
    // on shutdown
    
    client.close();


Note that you have to set the cluster name if you use one different to :ref:`elasticsearch <es-guide-reference-java-api>`  ch <es-guide-reference-java-api>`  

.. code-block:: java


    Settings settings = ImmutableSettings.settingsBuilder()
    		.put("cluster.name", "myClusterName").build();
    Client client =	new TransportClient(settings);
    //Add transport addresses and do something with the client...


The client allows to sniff the rest of the cluster, and add those into its list of machines to use. In this case, note that the ip addresses used will be the ones that the other nodes were started with (the "publish" address). In order to enable it, set the **client.transport.sniff** to **true**:


.. code-block:: java


    Settings settings = ImmutableSettings.settingsBuilder()
    		.put("client.transport.sniff", true).build();
    TransportClient client = new TransportClient(settings);

