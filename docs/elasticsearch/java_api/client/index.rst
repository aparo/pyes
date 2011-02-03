Client
======

Obtaining an elasticsearch **Client** is simple. The most common way to get a client is by starting an embedded **Node** which acts as a node within the cluster. Another manner is by using a **TransportClient** which connects to the cluster without being part of it.


Node Client
-----------

A Node based client is the simplest form to get a **Client** to start executing operations against elasticsearch.


.. code-block:: java


    import static org.elasticsearch.node.NodeBuilder.*;
    
    // on startup
    
    Node node = nodeBuilder().node();
    Client client = node.client();
    
    // on shutdown
    
    node.close();


When starting a **Node**, it joins the elasticsearch cluster (you can have different clusters by simple setting the **cluster.name** setting, or explicitly using the **clusterName** method on the builder). The benefit of using the **Client** is the fact that operations are automatically routed to the node(s) the operations need to be executed on, without performing a "double hop". For example, the index operation will automatically be executed on the shard that it will end up existing at.


When starting a **Node**, one of the common settings to consider is if it should hold data or not. In other words, should indices and shards be allocated to it. Many times we would like to have the clients just be clients, without shards being allocated to them. This is simple to configure by setting either **node.data** setting to **false** or **node.client** to **true** (the **NodeBuilder** respective helper methods on it):


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
----------------

The **TransportClient** connects remotely to an elasticsearch cluster using the transport module. It does not join the cluster, but simply gets one or more initial transport addresses and round robins between them on an action based operation (though most actions will probably be "two hop" operations).


.. code-block:: java


        
    // on startup    
        
    Client client = new TransportClient()
            .addTransportAddress(new InetSocketTransportAddress("host1", 9300))
            .addTransportAddress(new InetSocketTransportAddress("host2", 9300));
    
    // on shutdown
    
    client.close();


The client allows to sniff the rest of the cluster, and add those into its list of machines to use. In this case, note that the ip addresses used will be the ones that the other nodes were started with (the "publish" address). In order to enable it, set the **client.transport.sniff** to **true**:


.. code-block:: java


    TransportClient client = new TransportClient(settingsBuilder().put("client.transport.sniff", true));

