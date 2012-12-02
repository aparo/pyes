.. _es-guide-appendix-glossary:

========
Glossary
========

.. _glossary-analysis:

analysis
    Analysis is the process of converting full :ref:`text <glossary-text>` to :ref:`terms <glossary-term>`.
    Depending on which analyzer is used, these phrases: "**FOO BAR**",
    "**Foo-Bar**", "**foo,bar**" will probably all result in the terms "**foo**"
    and "**bar**".  These terms are what is actually stored in the index.

    A full text query (not a :ref:`term <glossary-term>` query) for "**FoO:bAR**" will
    also be analyzed to the terms "**foo**","**bar**" and will thus match
    the terms stored in the index.

    It is this process of analysis (both at index time and at search time)
    that allows elasticsearch to perform full text queries.

    Also see :ref:`text <glossary-text>` and :ref:`term <glossary-term>`.

.. _glossary-cluster:

cluster
    A cluster consists of one or more :ref:`nodes <glossary-node>` which share the same
    cluster name. Each cluster has a single master node which is
    chosen automatically by the cluster and which can be replaced if
    the current master node fails.

.. _glossary-document:

document
    A document is a JSON document which is stored in elasticsearch. It is
    like a row in a table in a relational database. Each document is
    stored in an :ref:`index <glossary-index>` and has a :ref:`type <glossary-type>`
    and an :ref:`id <glossary-id>`.

    A document is a JSON object (also known in other languages
    as a hash / hashmap / associative array) which contains zero or more
    :ref:`fields <glossary-field>`, or key-value pairs.

    The original JSON document that is indexed will be stored in the
    **_source** :ref:`field <glossary-field>`, which is returned by default
    when getting or searching for a document.

.. _glossary-id:

id
    The ID of a :ref:`document <glossary-document>` identifies a document. The
    **index/type/id** of a document must be unique. If no ID is provided,
    then it will be auto-generated. (also see :ref:`routing <glossary-routing>`)

.. _glossary-field:

field
    A :ref:`document <glossary-document>` contains a list of fields,  or key-value pairs.
    The value can be a simple (scalar) value (eg a string, integer, date),
    or a nested structure like an array or an object. A field is similar
    to a column in a table in a relational database.

    The :ref:`mapping <glossary-mapping>` for each field has a field 'type'
    (not to be confused with document :ref:`type <glossary-type>`) which indicates the
    type of data that can be stored in that field, eg
    **integer**, **string**, **object**.
    The mapping also allows you to define (amongst other things) how the
    value for a field should be analyzed.

.. _glossary-index:

index
    An index is like a 'database' in a relational database. It has a
    :ref:`mapping <glossary-mapping>` which defines multiple
    :ref:`types <glossary-type>`.

    An index is a logical namespace which maps to one or more
    primary :ref:`shards <glossary-shard>` and can have zero or more
    replica :ref:`shards <glossary-shard>`.


.. _glossary-mapping:

mapping
    A mapping is like a 'schema definition' in a relational database.
    Each :ref:`index <glossary-index>` has a mapping, which defines each
    :ref:`type <glossary-type>` within the index, plus a number of
    index-wide settings.

    A mapping can either be defined explicitly, or it will be generated
    automatically when a document is indexed.

.. _glossary-node:

node
    A node is a running instance of elasticsearch which belongs to a
    :ref:`cluster <glossary-cluster>`. Multiple nodes can be started on a single
    server for testing purposes, but usually you should have one node
    per server.

    At startup, a node will use unicast (or multicast, if specified)
    to discover an existing cluster with the same cluster name and will
    try to join that cluster.

.. _glossary-primary-shard:

primary shard
    Each document is stored in a single primary :ref:`shard <glossary-shard>`. When you
    index a document, it is indexed first on the primary shard, then
    on all :ref:`replicas <glossary-replica-shard>` of the primary shard.

    By default, an :ref:`index <glossary-index>` has 5 primary shards.  You can specify fewer
    or more primary shards to scale the number of :ref:`documents <glossary-document>`
    that your index can handle.

    You cannot change the number of primary shards in an index, once the
    index is created.

    See also :ref:`routing <glossary-routing>`


.. _glossary-replica-shard:

replica shard
    Each primary :ref:`shard <glossary-shard>` can have zero or more replicas.
    A replica is a copy of the primary shard, and has two purposes:

    # increase failover: a replica shard can be promoted
    to a primary shard if the primary fails

    # increase performance: get and search requests can be handled by
    primary or replica shards.

    By default, each primary shard has one replica, but the number
    of replicas can be changed dynamically on an existing index.
    A replica shard will never be started on the same node as its primary
    shard.

.. _glossary-routing:

routing
    When you index a document, it is stored on a single
    primary :ref:`shard <glossary-shard>`. That shard is chosen by hashing
    the **routing** value.  By default, the **routing** value is derived
    from the ID of the document or, if the document has a specified
    parent document, from the ID of the parent document (to ensure
    that child and parent documents are stored on the same shard).

    This value can be overridden by specifying a **routing** value at index
    time, or a :ref:`routing field <es-guide-reference-mapping-routing-field>` in the :ref:`mapping <glossary-mapping>`.

.. _glossary-shard:

shard
    A shard is a single Lucene instance. It is a low-level "worker" unit
    which is managed automatically by elasticsearch.  An index
    is a logical namespace which points to :ref:`primary <glossary-primary-shard>`
    and :ref:`replica <glossary-replica-shard>` shards.

    Other than defining the number of primary and replica shards that
    an index should have, you never need to refer to shards directly.
    Instead, your code should deal only with an index.

    Elasticsearch distributes shards amongst all :ref:`nodes <glossary-node>` in
    the :ref:`cluster <glossary-cluster>`, and can be move shards automatically from
    one node to another in the case of node failure, or the addition
    of new nodes.

.. _glossary-source-field:

source field
    By default, the JSON document that you index will be stored in the
    **_source** field and will be returned by all get and search requests.
    This allows you access to the original object directly from search
    results, rather than requiring a second step to retrieve the object
    from an ID.


    Note: the exact JSON string that you indexed will be returned to you,
    even if it contains invalid JSON.  The contents of this field do not
    indicate anything about how the data in the object has been indexed.

.. _glossary-term:

term
    A term is an exact value that is indexed in elasticsearch. The terms
    **foo**, **Foo**, **FOO** are NOT equivalent. Terms (ie exact values) can
    be searched for using 'term' queries.

    See also :ref:`text <glossary-text>` and :ref:`analysis <glossary-analysis>`.

.. _glossary-text:

text
    Text (or full text) is ordinary unstructured text, such as this
    paragraph. By default, text will by :ref:`analyzed <glossary-analysis>`  into
    :ref:`terms <glossary-term>`, which is what is actually stored in the index.

    Text :ref:`fields <glossary-field>` need to be analyzed at index time in order to
    be searchable as full text, and keywords in full text queries must
    be analyzed at search time to produce (and search for) the same
    terms that were generated at index time.

    See also :ref:`term <glossary-term>` and :ref:`analysis <glossary-analysis>`.

.. _glossary-type:

type
    A type is like a 'table' in a relational database. Each type has
    a list of :ref:`fields <glossary-field>` that can be specified for
    :ref:`documents <glossary-document>` of that type. The
    :ref:`mapping <glossary-mapping>` defines how each field in the document
    is analyzed.
