.. _es-guide-reference-modules-plugins:

=======
Plugins
=======

Plugins
=======

Plugins are a way to enhance the basic elasticsearch functionality in a custom manner. They range from adding custom mapping types, custom analyzers (in a more built in fashion), native scripts, custom discovery and more.


Installing plugins
------------------

Installing plugins can either be done manually by placing them under the **plugins** directory, or using the **plugin** script. Several plugins can be found under the `elasticsearch <https://github.com/elasticsearch>`_  organization in GitHub, starting with **elasticsearch-**.


Plugins can also be automatically downloaded and installed from gitub using: **user_name/repo_name** structure, or, for explicit versions, using **user_name/repo_name/version_number**. When no version number is specified, first a version based on the elasticsearch version is tried, and if it does not work, then master is used.


Site Plugins
------------

Plugins can have "sites" in them, any plugin that exists under the **plugins** directory with a **_site** directory, its content will be statically served when hitting **/_plugin/[plugin_name]/** url. Those can be added even after the process has started.


Installed plugins that do not contain any java related content, will automatically be detected as site plugins, and their content will be moved under **_site**.


The ability to install plugins from github allows to easily install site plugins hosted there, for example, running:


.. code-block:: js

    bin/plugin -install Aconex/elasticsearch-head
    bin/plugin -install lukas-vlcek/bigdesk


Will install both of those site plugins, with **elasticsearch-head** available under **http://localhost:9200/_plugin/head/** and **bigdesk** available under **http://localhost:9200/_plugin/bigdesk/**.


Mandatory Plugins
-----------------

If you rely on some plugins, you can define mandatory plugins using the **plugin.mandatory** attribute, for example, here is a sample config:


.. code-block:: js

    plugin.mandatory: mapper-attachments,lang-groovy


For safety reasons, if a mandatory plugin is not installed, the node will not start.


Known Plugins
=============

Analysis Plugins
----------------

* `Smart Chinese Analysis Plugin <https://github.com/elasticsearch/elasticsearch-analysis-smartcn>`_  `_  (by elasticsearch team)
* `ICU Analysis plugin <https://github.com/elasticsearch/elasticsearch-analysis-icu>`_  `_  (by elasticsearch team)
* `Stempel (Polish) Analysis plugin <https://github.com/elasticsearch/elasticsearch-analysis-stempel>`_  `_  (by elasticsearch team)
* `IK Analysis Plugin <https://github.com/medcl/elasticsearch-analysis-ik>`_  `_  (by Medcl)
* `Mmseg Analysis Plugin <https://github.com/medcl/elasticsearch-analysis-mmseg>`_  `_  (by Medcl)
* `Hunspell Analysis Plugin <https://github.com/jprante/elasticsearch-analysis-hunspell>`_  `_  (by Jörg Prante)
* `Japanese Analysis plugin <https://github.com/suguru/elasticsearch-analysis-japanese>`_  `_  (by suguru).

River Plugins
-------------

* `CouchDB River Plugin <https://github.com/elasticsearch/elasticsearch-river-couchdb>`_  `_  (by elasticsearch team)
* `Wikipedia River Plugin <https://github.com/elasticsearch/elasticsearch-river-wikipedia>`_  `_  (by elasticsearch team)
* `Twitter River Plugin <https://github.com/elasticsearch/elasticsearch-river-twitter>`_  `_  (by elasticsearch team)
* `RabbitMQ River Plugin <https://github.com/elasticsearch/elasticsearch-river-rabbitmq>`_  `_  (by elasticsearch team)
* `RSS River Plugin <http://dadoonet.github.com/rssriver/>`_  `_  (by David Pilato)
* `MongoDB River Plugin <https://github.com/richardwilly98/elasticsearch-river-mongodb/>`_  `_  (by Richard Louapre)

Transport Plugins
-----------------

* `Servlet transport <https://github.com/elasticsearch/elasticsearch-transport-wares>`_  `_  (by elasticsearch team)
* `Memcached transport plugin <https://github.com/elasticsearch/elasticsearch-transport-memcached>`_  `_  (by elasticsearch team)
* `Thrift Transport <https://github.com/elasticsearch/elasticsearch-transport-thrift>`_  `_  (by elasticsearch team)
* `ZeroMQ transport layer plugin <https://github.com/tlrx/transport-zeromq>`_  `_  (by Tanguy Leroux)
* `Jetty HTTP transport plugin <https://github.com/sonian/elasticsearch-jetty>`_  `_  (by Sonian Inc.)

Scripting Plugins
-----------------

* `Python language Plugin <https://github.com/elasticsearch/elasticsearch-lang-python>`_  `_  (by elasticsearch team)
* `JavaScript language Plugin <https://github.com/elasticsearch/elasticsearch-lang-javascript>`_  `_  (by elasticsearch team)
* `Groovy lang Plugin <https://github.com/elasticsearch/elasticsearch-lang-groovy>`_  `_  (by elasticsearch team)

Site Plugins
------------

* `BigDesk Plugin <https://github.com/lukas-vlcek/bigdesk>`_  `_  (by Lukáš Vlček)
* `Elasticsearch Head Plugin <https://github.com/Aconex/elasticsearch-head>`_  `_  (by Ben Birch)

Misc Plugins
------------

* `Mapper Attachments Type plugin <https://github.com/elasticsearch/elasticsearch-mapper-attachments>`_  `_  (by elasticsearch team)
* `Hadoop Plugin <https://github.com/elasticsearch/elasticsearch-hadoop>`_  `_  (by elasticsearch team)
* `AWS Cloud Plugin <https://github.com/elasticsearch/elasticsearch-cloud-aws>`_  `_  (by elasticsearch team)
* `ElasticSearch Mock Solr Plugin <https://github.com/mattweber/elasticsearch-mocksolrplugin>`_  `_  (by Matt Weber)
* `Suggester Plugin <https://github.com/spinscale/elasticsearch-suggest-plugin>`_  `_  (by Alexander Reelsen)
* `ElasticSearch PartialUpdate Plugin <https://github.com/medcl/elasticsearch-partialupdate>`_  `_  (by Medcl)

