=====================
Admin Indices Analyze
=====================

Performs the analysis process on a text and return the tokens breakdown of the text. Here is an example:


.. code-block:: js

    curl -XGET 'localhost:9200/test/_analyze?text=this+is+a+test'


The above will run an analysis on the "this is a test" text, using the default index analyzer associated with the **test** index. An **analyzer** can also be provided to use a different analyzer:


.. code-block:: js

    curl -XGET 'localhost:9200/test/_analyze?analyzer=whitespace' -d 'this is a test'


Also, the text can be provided as part of the request body, and not as a parameter.


Format
------

By default, the format the tokens are returned in are in json and its called **detailed**. The **text** format value provides the analyzed data in a text stream that is a bit more readable.



