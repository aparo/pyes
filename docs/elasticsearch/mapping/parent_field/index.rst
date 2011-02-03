Parent Field
============

The parent field mapping is defined on a child mapping, and points to the parent type this child relates to. For example, in case of a **blog** type and a **blog_tag** type child document, the mapping for **blog_tag** should be:


.. code-block:: js


    {
        "blog_tag" : {
            "_parent" : {
                "type" : "blog"
            }
        }
    }


The mapping is automatically stored and indexed (meaning it can be searched on using the **_parent** field notation).

