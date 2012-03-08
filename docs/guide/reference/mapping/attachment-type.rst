.. _es-guide-reference-mapping-attachment-type:

===============
Attachment Type
===============

The **attachment** type allows to index different `attachment" type field (encoded as **base64**), for example, microsoft office formats, open document formats, ePub, HTML, and so on (full list can be found "here <http://lucene.apache.org/tika/0.10/formats.html)>`_.  

The **attachment** type is provided as a plugin extension. The plugin is a simple zip file that can be downloaded and placed under **$ES_HOME/plugins** location. It will be automatically detected and the **attachment** type will be added.


Note, the **attachment** type is experimental.


Using the attachment type is simple, in your mapping JSON, simply set a certain JSON element as attachment, for example:


.. code-block:: js


    {
        "person" : {
            "properties" : {
                "my_attachment" : { "type" : "attachment" }
            }
        }
    }


In this case, the JSON to index can be:


.. code-block:: js


    {
        "my_attachment" : "... base64 encoded attachment ..."
    }


Or it is possible to use more elaborated JSON if content type or resource name need to be set explicitly:


.. code-block:: js


    {
        "my_attachment" : {
            "_content_type" : "application/pdf",
            "_name" : "resource/name/of/my.pdf",
            "content" : "... base64 encoded attachment ..."
        }
    }


The **attachment** type not only indexes the content of the doc, but also automatically adds meta data on the attachment as well (when available). The metadata supported are: **date**, **title**, **author**, and **keywords**. They can be queried using the "dot notation", for example: **my_attachment.author**.


Both the meta data and the actual content are simple core type mappers (string, date, ...), thus, they can be controlled in the mappings. For example:


.. code-block:: js


    {
        "person" : {
            "properties" : {
                "file" : { 
                    "type" : "attachment",
                    "fields" : {
                        "file" : {"index" : "no"},
                        "date" : {"store" : "yes"},
                        "author" : {"analyzer" : "myAnalyzer"}
                    }
                }
            }
        }
    }


In the above example, the actual content indexed is mapped under **fields** name **file**, and we decide not to index it, so it will only be available in the **_all** field. The other fields map to their respective metadata names, but there is no need to specify the **type** (like **string** or **date**) since it is already known.


The plugin uses `Apache Tika <http://lucene.apache.org/tika/>`_  to parse attachments, so many formats are supported, listed `here <http://lucene.apache.org/tika/0.10/formats.html>`_.  
