.. _es-guide-reference-mapping-source-field:

============
Source Field
============

The **_source** field is an automatically generated field that stores the actual JSON that was used as the indexed document. It is not indexed (searchable), just stored. When executed "fetch" requests, like get or search, the **_source** field is returned by default.


Though very handy to have around, the source field does incur storage overhead within the index. For this reason, it can be disabled. For example:


.. code-block:: js


    {
        "tweet" : {
            "_source" : {"enabled" : false}
        }
    }


Compression
===========

The source field can be compressed (LZF) when stored in the index. This can greatly reduce the index size, as well as possibly improving performance (when decompression overhead is better than loading a bigger source from disk). The code takes special care to decompress the source only when needed, for example decompressing it directly into the REST stream of a result.


In order to enable compression, the **compress** option should be set to **true**. By default it is set to **false**. Note, this can be changed on an existing index, as a mix of compressed and uncompressed sources is supported.


Moreover, a **compress_threshold** can be set to control when the source will be compressed. It accepts a byte size value (for example **100b**, **10kb**). Note, **compress** should be set to **true**.


Includes / Excludes
===================

Allow to specify paths in the source that would be included / excluded when its stored, supporting ***** as wildcard annotation. For example:


.. code-block:: js


    {
        "my_type" : {
            "_source" : {
                "includes" : ["path1.*", "path2.*"],
                "excludes" : ["pat3.*"]
            }
        }
    }

