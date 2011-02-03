Root Object Type
================

The root object mapping is an :doc:`object type mapping <./../object_type/index>` that maps the root object (the type itself). On top of all the different mappings that can be set using the :doc:`object type mapping <./../object_type/index>`, it allows for additional, type level mapping definitions.


The root object mapping allows to index a JSON document that either starts with the actual mapping type, or only contains its fields. For example, the following **tweet** JSON can be indexed:


.. code-block:: js


    {
        "tweet" {
            "message" : "This is a tweet!"
        }
    }


But, also the following JSON can be indexed:


.. code-block:: js


    {
        "message" : "This is a tweet!"
    }


The above can be done since the API for the index operation already includes the type the JSON document belongs to.


Special Fields
--------------

Each document created has special fields that are either created or managed automatically, with specific mappings allowing to control their behavior. The fields are:


===========================================  ======================================================================================
 Field                                        Description                                                                          
===========================================  ======================================================================================
:doc:`_id <./../id_field/index>`             Allow to control the automatically created **_id** field.                             
:doc:`_type <./../type_field/index>`         Allow to control the automatically created **_type** field.                           
:doc:`_boost <./../boost_field/index>`       Allow to control the boosting of a document using an external value.                  
:doc:`_source <./../source_field/index>`     Allow to control the **_source** field storing the actual JSON indexed.               
:doc:`_all <./../all_field/index>`           Allows to automatically create an **_all** field that includes all the other fields.  
===========================================  ======================================================================================

Index / Search Analyzers
------------------------

The root object allows to define type mapping level analyzers for index and search that will be used with all different fields that do not explicitly set analyzers on their own. Here is an example:


.. code-block:: js


    {
        "tweet" : {
            "index_analyzer" : "standard",
            "search_analyzer" : "standard"
        }
    }


The above simply explicitly defines both the **index_analyzer** and **search_analyzer** that will be used. There is also an option to use the **analyzer** attribute to set both the **search_analyzer** and **index_analyzer**.


date_formats
------------

**date_formats** is the ability to set one or more date formats that will be used to detect **date** fields. For example:


.. code-block:: js


    {
        "tweet" : {
            "date_formats" : ["yyyy-MM-dd", "dd-MM-yyyy"],
            "properties" : {
                "message" : {"type" : "string"}
            }
        }
    }


In the above mapping, if a new JSON field of type string is detected, the date formats specified will be used in order to check if its a date. If it passes parsing, then the field will be declared with **date** type, and will use the matching format as its format attribute. The date format itself is explained :doc:`here <.//date_format/index>`. 

The default formats are: **dateOptionalTime** (ISO) and **yyyy/MM/dd HH:mm:ss||yyyy/MM/dd**.


dynamic_templates
-----------------

Dynamic templates allow to define mapping templates that will be applied when dynamic introduction of fields / objects happens.


For example, we might want to have all fields to be stored by default, or all `string` fields to be stored, or have `string` fields to always be indexed as `multi_field`, once analyzed and once not_analyzed. Here is a simple example:


.. code-block:: js


    {
        "person" : {
            "dynamic_templates" : [
                {
                    "template_1" : {
                        "match" : "multi*",
                        "mapping" : {
                            "type" : "multi_field",
                            "fields" : {
                                :doc:`{name}" : {"type <.//index>` pe <./ "{dynamic_tpye}", "index" : "analyzed", "store" : "yes"}/index>`, 
                                :doc:`org" : {"type <.//index>` pe <./ "{dynamic_type}", "index" : "not_analyzed", "store" : "yes"}/index>` 
                            }
                        }
                    }
                },
                {
                    "template_2" : {
                        "match" : "*",
                        "match_mapping_type" : "string",
                        "mapping" : {
                            "type" : "string",
                            "index" : "not_analyzed"
                        }
                    }
                }
            ]
        }
    }


The above mapping will create a **multi_field** mapping for all field names starting with multi, and will map all **string** types to be **not_analyzed**.


Dynamic templates are named to allow for simple merge behavior. A new mapping, just with a new template can be "put" and that template will be added, or if it has the same name, the template will be replaced.


The **match** allow to define matching on the field name. An **unmatch** option is also available to exclude fields if they do match on **match**. The **match_mapping_type** controls if this template will be applied only for dynamic fields of the specified type (as guessed by the json format).


Another option is to use **path_match**, which allows to match the dynamic template against the "full" dot notation name of the field (for example **obj1.*.value** or **obj1.obj2.***), with the respective **path_unmatch**.


The format of all the matching is simple format, allowing to use * as a matching element supporting simple patterns such as xxx*, *xxx, xxx*yyy (with arbitrary number of pattern types), as well as direct equality. The **match_pattern** can be set to **regex** to allow for regular expression based matching.


The **mapping** element provides the actual mapping definition. The **{name}** keyword can be used and will be replaced with the actual dynamic field name being introduced. The **{dynamic_type}** (or **{dynamicType}**) can be used and will be replaced with the mapping derived based on the field type (or the derived type, like **date**).


Complete generic settings can also be applied, for example, to have all mappings be stored, just set:


.. code-block:: js


    {
        "person" : {
            "dynamic_templates" : [
                {
                    "store_generic" : {
                        "match" : "*",
                        "mapping" : {
                            "store" : "yes"
                        }
                    }
                }
            ]
        }
    }

