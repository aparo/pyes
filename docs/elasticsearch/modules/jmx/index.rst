JMX Module
==========

The JMX module exposes node information through `JMX <http://java.sun.com/javase/technologies/core/mntr-mgmt/javamanagement/>`. JMX can be used by either `jconsole <http://en.wikipedia.org/wiki/JConsole>` or `VisualVM <http://en.wikipedia.org/wiki/VisualVM>`. 

Exposed JMX data include both node level information, as well as instantiated index and shard on specific node. This is a work in progress with each version exposing more information.


jmx.domain
----------

The domain under which the JMX will register under can be set using **jmx.domain** setting. It defaults to **{elasticsearch}**.


jmx.create_connector
--------------------

An RMI connector can be started to accept JMX requests. This can be enabled by setting **jmx.create_connector** to **true**. An RMI connector does come with its own overhead, make sure you really need it.


When an RMI connector is created, the **jmx.port** setting provides a port range setting for the ports the rmi connector can open on. By default, it is set to **9400-9500**.

