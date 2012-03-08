.. _es-guide-reference-mapping-object-type:

===========
Object Type
===========

JSON documents are hierarchal in nature, allowing to define inner "object"s within the actual JSON. ElasticSearch completely understand the nature of objects and allows to map them easily, automatically support their dynamic nature (one object can have different fields each time), and provides query support for their inner field. Lets take the following JSON as an example:


.. code-block:: js


    {
        "tweet" : {
            "person" : {
                "name" : {
                    "first_name" : "Shay",
                    "last_name" : "Banon"
                },
                "sid" : "12345"
            },
            "message" : "This is a tweet!"
        }
    }

 
The above shows an example where a tweet includes the actual **person** details. A **person** is an object, with an **sid**, and a **name** object which has **first_name** and **last_name**. Its important to note that **tweet** is also an object, though a special :ref:`root object type <es-guide-reference-mapping-root-object-type>`  which allows for additional mapping definitions.


The following is an example of explicit mapping for the above JSON:


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "person" : {
                    "type" : "object",
                    "properties" : {
                        "name" : {
                            "properties" : {
                                "first_name" : {"type" : "string"},
                                "last_name" : {"type" : "string"}
                            }
                        },
                        "sid" : {"type" : "string", "index" : "not_analyzed"}
                    }
                }
                "message" : {"type" : "string"}
            }
        }
    }


In order to mark a mapping of type **object**, set the **type** to object. This is an optional step, since if there are **properties** defined for it, it will automatically be identified as an **object** mapping.


properties
==========

An object mapping can optionally define one or more properties using the **properties** tag. Properties list the properties this field will have. Each property can be either another **object**, or one of the :ref:`core_types <es-guide-reference-mapping-core-types>`.  

dynamic
=======

One of the more important features of ElasticSearch is its ability to be schema-less. This means that, in our example above, the **person** object can later on be indexed with a new property, for example, **age**, and it will automatically be added to the mapping definitions. Same goes for the **tweet** root object.


This feature is by default turned on, and its the **dynamic** nature of each object mapped. Each object mapped is automatically dynamic, though it can be explicitly turned off:


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "person" : {
                    "type" : "object",
                    "properties" : {
                        "name" : {
                            "dynamic" : false,
                            "properties" : {
                                "first_name" : {"type" : "string"},
                                "last_name" : {"type" : "string"}
                            }
                        },
                        "sid" : {"type" : "string", "index" : "not_analyzed"}
                    }
                }
                "message" : {"type" : "string"}
            }
        }
    }


In the above example, the **name** object mapped is not dynamic, meaning that if, in the future, we will try and index a JSON with a **middle_name** within the **name** object, it will get discarded and not added.


There is no performance overhead of an **object** being dynamic, the ability to turn it off is provided as a safe mechanism so "malformed" objects won't, by mistake, index data that we do not wish to be indexed.


The dynamic nature also works with inner objects, meaning that if a new **object** is provided within a mapped dynamic object, it will be automatically added to the index and mapped as well.


When processing dynamic new fields, their type is automatically derived. For example, if it is a **number**, it will automatically be treated as number :ref:`core_type <es-guide-reference-mapping-core-types>`.  Dynamic fields default to their default attributes, for example, they are not stored and they are always indexed.


Date fields are special since they are represented as a **string**. Date fields are detected if they can be parsed as a date when they are first introduced into the system. The set of date formats that are tested against can be configured using the **date_formats** and explained later.


Note, once a field has been added, *its type can not change*. For example, if we added age and its value is a number, then it can't be treated as a string.


The **dynamic** parameter can also be set to **strict**, meaning that not only new fields will not be introduced into the mapping, parsing (indexing) docs with such new fields will fail.


enabled
=======

The **enabled** flag allows to disable parsing and adding a named object completely. This is handy when a portion of the JSON document passed should not be indexed. For example:


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "person" : {
                    "type" : "object",
                    "properties" : {
                        "name" : {
                            "type" : "object",
                            "enabled" : false
                        },
                        "sid" : {"type" : "string", "index" : "not_analyzed"}
                    }
                }
                "message" : {"type" : "string"}
            }
        }
    }


In the above, **name** and its content will not be indexed at all.


path
====

In the :ref:`core_types <es-guide-reference-mapping-core-types>`  section, a field can have a **index_name** associated with it in order to control the name of the field that will be stored within the index. When that field exists within an object(s) that are not the root object, the name of the field of the index can either include the full "path" to the field with its **index_name**, or just the **index_name**. For example (under mapping of _type_ **person**, removed the tweet type for clarity):


.. code-block:: js


    {
        "person" : {
            "properties" : {
                "name1" : {
                    "type" : "object",
                    "path" : "just_name",
                    "properties" : {
                        "first1" : {"type" : "string"},
                        "last1" : {"type" : "string", "index_name" : "i_last_1"}
                    }
                },
                "name2" : {
                    "type" : "object",
                    "path" : "full",
                    "properties" : {
                        "first2" : {"type" : "string"},
                        "last2" : {"type" : "string", "index_name" : "i_last_2"}
                    }
                }
            }
        }
    }


In the above example, the **name1** and **name2** objects within the **person** object have different combination of **path** and **index_name**. The document fields that will be stored in the index as a result of that are:


======================  =======================
 JSON Name               Document Field Name   
======================  =======================
**name1**/**first1**    **first1**             
**name1**/**last1**     **i_last_1**           
**name2**/**first2**    **name2.first2**       
**name2**/**last2**     **name2.i_last_2**     
======================  =======================

Note, when querying or using a field name in any of the APIs provided (search, query, selective loading, ...), there is an automatic detection from logical full path and into the **index_name** and vice versa. For example, even though **name1**/**last1** defines that it is stored with **just_name** and a different **index_name**, it can either be referred to using **name1.last1** (logical name), or its actual indexed name of **i_last_1**.


More over, where applicable, for example, in queries, the full path including the type can be used such as **person.name.last1**, in this case, both the actual indexed name will be resolved to match against the index, and an automatic query filter will be added to only match **person** types.


include_in_all
==============

**include_in_all** can be set on the **object** type level. When set, it propagates down to all the inner mapping defined within the **object** that do no explicitly set it.


