.. _es-guide-reference-mapping-core-types:

==========
Core Types
==========

Each JSON field can be mapped to a specific core type. JSON itself already provides us with some typing, with its support for **string**, **integer**/**long**, **float**/**double**, **boolean**, and **null**.


The following sample tweet JSON document will be used to explain the core types:


.. code-block:: js


    {
        "tweet" {
            "user" : "kimchy"
            "message" : "This is a tweet!",
            "postDate" : "2009-11-15T14:12:12",
            "priority" : 4,
            "rank" : 12.3
        }
    }


Explicit mapping for the above JSON tweet can be:


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "user" : {"type" : "string", "index" : "not_analyzed"},
                "message" : {"type" : "string", "null_value" : "na"},
                "postDate" : {"type" : "date"},
                "priority" : {"type" : "integer"},
                "rank" : {"type" : "float"}
            }
        }
    }



String
======

The text based string type is the most basic type, and contains one or more characters. An example mapping can be:


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "message" : {
                    "type" : "string",
                    "store" : "yes",
                    "index" : "analyzed",
                    "null_value" : "na"
                }
            }
        }
    }


The above mapping defines a **string** **message** property/field within the **tweet** type. The field is stored in the index (so it can later be retrieved using selective loading when searching), and it gets analyzed (broken down into searchable terms). If the message has a **null** value, then then value that will be stored is **na**.


The following table lists all the attributes that can be used with the **string** type:


==================================  ===========================================================================================================================================================================================================================================================================================================================================================================================
 Attribute                           Description                                                                                                                                                                                                                                                                                                                                                                               
==================================  ===========================================================================================================================================================================================================================================================================================================================================================================================
**index_name**                      The name of the field that will be stored in the index. Defaults to the property/field name.                                                                                                                                                                                                                                                                                               
**store**                           Set to **yes** the store actual field in the index, **no** to not store it. Defaults to **no** (note, the JSON document itself is stored, and it can be retrieved from it).                                                                                                                                                                                                                
**index**                           Set to **analyzed** for the field to be indexed and searchable after being broken down into token using an analyzer. **not_analyzed** means that its still searchable, but does not go through any analysis process or broken down into tokens. **no** means that it won't be searchable at all (as an individual field; it may still be included in **_all**). Defaults to **analyzed**.  
**term_vector**                     Possible values are **no**, **yes**, **with_offsets**, **with_positions**, **with_positions_offsets**. Defaults to **no**.                                                                                                                                                                                                                                                                 
**boost**                           The boost value. Defaults to **1.0**.                                                                                                                                                                                                                                                                                                                                                      
**null_value**                      When there is a (JSON) null value for the field, use the **null_value** as the field value. Defaults to not adding the field at all.                                                                                                                                                                                                                                                       
**omit_norms**                      Boolean value if norms should be omitted or not. Defaults to **false**.                                                                                                                                                                                                                                                                                                                    
**omit_term_freq_and_positions**    Boolean value if term freq and positions should be omitted. Defaults to **false**.                                                                                                                                                                                                                                                                                                         
**analyzer**                        The analyzer used to analyze the text contents when **analyzed** during indexing and when searching using a query string. Defaults to the globally configured analyzer.                                                                                                                                                                                                                    
**index_analyzer**                  The analyzer used to analyze the text contents when **analyzed** during indexing.                                                                                                                                                                                                                                                                                                          
**search_analyzer**                 The analyzer used to analyze the field when part of a query string.                                                                                                                                                                                                                                                                                                                        
**include_in_all**                  Should the field be included in the **_all** field (if enabled). Defaults to **true** or to the parent **object** type setting.                                                                                                                                                                                                                                                            
==================================  ===========================================================================================================================================================================================================================================================================================================================================================================================

The **string** type also support custom indexing parameters associated with the indexed value. For example:


.. code-block:: js


    {
        "message" : {
            "_value":  "boosted value",
            "_boost":  2.0
        }
    }


The mapping is required to disambiguate the meaning of the document. Otherwise, the structure would interpret "message" as a value of type "object". The key **_value** (or **value**) in the inner document specifies the real string content that should eventually be indexed. The **_boost** (or **boost**) key specifies the per field document boost (here 2.0).


Number
======

A number based type supporting **float**, **double**, **byte**, **short**, **integer**, and **long**. It uses specific constructs within Lucene is order to support numeric values. An example mapping can be:


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "rank" : {
                    "type" : "float",
                    "null_value" : 1.0
                }
            }
        }
    }


The following table lists all the attributes that can be used with a numbered type:


====================  ==============================================================================================================================================================================
 Attribute             Description                                                                                                                                                                  
====================  ==============================================================================================================================================================================
**type**              The type of the number. Can be **float**, **double**, **integer**, **long**, **short**, **byte**. Required.                                                                   
**index_name**        The name of the field that will be stored in the index. Defaults to the property/field name.                                                                                  
**store**             Set to **yes** the store actual field in the index, **no** to not store it. Defaults to **no** (note, the JSON document itself is stored, and it can be retrieved from it).   
**index**             Set to **no** if the value should not be indexed. In this case, **store** should be set to **yes**, since if its not indexed and not stored, there is nothing to do with it.  
**precision_step**    The precision step (number of terms generated for each number value). Defaults to **4**.                                                                                      
**boost**             The boost value. Defaults to **1.0**.                                                                                                                                         
**null_value**        When there is a (JSON) null value for the field, use the **null_value** as the field value. Defaults to not adding the field at all.                                          
**include_in_all**    Should the field be included in the **_all** field (if enabled). Defaults to **true** or to the parent **object** type setting.                                               
====================  ==============================================================================================================================================================================

Date
====

The date type is a special type which maps to JSON string type. It follows a specific format that can be explicitly set. All dates are **UTC**. as. Internally, a date maps to a number type **long**, with the added parsing stage from string to long and from long to string. An example mapping:


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "postDate" : {
                    "type" : "date",
                    "format" : "YYYY-MM-dd"
                }
            }
        }
    }


The date type will also accept a long number representing UTC milliseconds since the epoch, regardless of the format it can handle.


The following table lists all the attributes that can be used with a date type:


====================  ==============================================================================================================================================================================
 Attribute             Description                                                                                                                                                                  
====================  ==============================================================================================================================================================================
**index_name**        The name of the field that will be stored in the index. Defaults to the property/field name.                                                                                  
**format**            The :ref:`date format <es-guide-reference-mapping-date-format>`.  rence-mapping-date-format>`.  Defaults to **dateOptionalTime**.                                             
**store**             Set to **yes** the store actual field in the index, **no** to not store it. Defaults to **no** (note, the JSON document itself is stored, and it can be retrieved from it).   
**index**             Set to **no** if the value should not be indexed. In this case, **store** should be set to **yes**, since if its not indexed and not stored, there is nothing to do with it.  
**precision_step**    The precision step (number of terms generated for each number value). Defaults to **4**.                                                                                      
**boost**             The boost value. Defaults to **1.0**.                                                                                                                                         
**null_value**        When there is a (JSON) null value for the field, use the **null_value** as the field value. Defaults to not adding the field at all.                                          
**include_in_all**    Should the field be included in the **_all** field (if enabled). Defaults to **true** or to the parent **object** type setting.                                               
====================  ==============================================================================================================================================================================

Boolean
=======

The boolean type Maps to the JSON boolean type. It ends up storing within the index either **T** or **F**, with automatic translation to **true** and **false** respectively.


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "hes_my_special_tweet" : {
                    "type" : "boolean",
                }
            }
        }
    }


The boolean type also supports passing the value as a number (in this case **0** is **false**, all other values are **true**).


The following table lists all the attributes that can be used with the boolean type:


====================  ==============================================================================================================================================================================
 Attribute             Description                                                                                                                                                                  
====================  ==============================================================================================================================================================================
**index_name**        The name of the field that will be stored in the index. Defaults to the property/field name.                                                                                  
**store**             Set to **yes** the store actual field in the index, **no** to not store it. Defaults to **no** (note, the JSON document itself is stored, and it can be retrieved from it).   
**index**             Set to **no** if the value should not be indexed. In this case, **store** should be set to **yes**, since if its not indexed and not stored, there is nothing to do with it.  
**boost**             The boost value. Defaults to **1.0**.                                                                                                                                         
**null_value**        When there is a (JSON) null value for the field, use the **null_value** as the field value. Defaults to not adding the field at all.                                          
**include_in_all**    Should the field be included in the **_all** field (if enabled). Defaults to **true** or to the parent **object** type setting.                                               
====================  ==============================================================================================================================================================================

Binary
======

The binary type is a base64 representation of binary data that can be stored in the index. The field is always stored and not indexed at all.


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "image" : {
                    "type" : "binary",
                }
            }
        }
    }


The following table lists all the attributes that can be used with the binary type:


================  ==============================================================================================
 Attribute         Description                                                                                  
================  ==============================================================================================
**index_name**    The name of the field that will be stored in the index. Defaults to the property/field name.  
================  ==============================================================================================
