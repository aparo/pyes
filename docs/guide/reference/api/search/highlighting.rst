.. _es-guide-reference-api-search-highlighting:

============
Highlighting
============

Allow to highlight search results on one or more fields. The implementation uses the either lucene **fast-vector-highlighter** or **highlighter**. The search request body:


.. code-block:: js


    {
        "query" : {...},
        "highlight" : {
            "fields" : {
                "content" : {}
            }
        }
    }


In the above case, the **content** field will be highlighted for each search hit (there will be another element in each search hit, called **highlight**, which includes the highlighted fields and the highlighted fragments).


In order to perform highlighting, the actual content of the field is required. If the field in question is stored (has **store** set to **yes** in the mapping), it will be used, otherwise, the actual **_source** will be loaded and the relevant field will be extracted from it.


If no **term_vector** information is provided (by setting it to **with_positions_offsets** in the mapping), then the plain highlighter will be used. If it is provided, then the fast vector highlighter will be used. When term vectors are available, highlighting will be performed faster at the cost of bigger index size.


Here is an example of setting the **content** field to allow for highlighting using the fast vector highlighter on it (this will cause the index to be bigger):


.. code-block:: js


    {
        "type_name" : {
            "content" : {"term_vector" : "with_positions_offsets"}
        }
    }



Highlighting Tags
=================

By default, the highlighting will wrap highlighted text in **<em>** and **</em>**. This can be controlled by setting **pre_tags** and **post_tags**, for example:


.. code-block:: js


    {
        "query" : {...},
        "highlight" : {
            "pre_tags" : ["<tag1>", "<tag2>"],
            "post_tags" : ["</tag1>", "</tag2>"],
            "fields" : {
                "_all" : {}
            }
        }
    }


There can be a single tag or more, and the "importance" is ordered. There are also built in "tag" schemas, with currently a single schema called **styled** with **pre_tags** of:


.. code-block:: js

    <em class="hlt1">, <em class="hlt2">, <em class="hlt3">,
    <em class="hlt4">, <em class="hlt5">, <em class="hlt6">,
    <em class="hlt7">, <em class="hlt8">, <em class="hlt9">,
    <em class="hlt10">


And post tag of **</em>**. If you think of more nice to have built in tag schemas, just send an email to the mailing list or open an issue. Here is an example of switching tag schemas:


.. code-block:: js


    {
        "query" : {...},
        "highlight" : {
            "tags_schema" : "styled",
            "fields" : {
                "content" : {}
            }
        }
    }


An **encoder** parameter can be used to define how highlighted text will be encoded. It can be either **default** (no encoding) or **html** (will escape html, if you use html highlighting tags).


Highlighted Fragments
=====================

Each field highlighted can control the size of the highlighted fragment in characters (defaults to **100**), and the maximum number of fragments to return (defaults to **5**). For example:


.. code-block:: js


    {
        "query" : {...},
        "highlight" : {
            "fields" : {
                "content" : {"fragment_size" : 150, "number_of_fragments" : 3}
            }
        }
    }


On top of this it is possible to specify that highlighted fragments are order by score:


.. code-block:: js


    {
        "query" : {...},
        "highlight" : {
            "order" : "score",
            "fields" : {
                "content" : {"fragment_size" : 150, "number_of_fragments" : 3}
            }
        }
    }


Note the score of text fragment in this case is calculated by Lucene highlighting framework. For implementation details you can check **ScoreOrderFragmentsBuilder.java** class.


If the **number_of_fragments** value is set to 0 then no fragments are produced, instead the whole content of the field is returned, and of course it is highlighted. This can be very handy if short texts (like document title or address) need to be highlighted but no fragmentation is required. Note that **fragment_size** is ignored in this case.


.. code-block:: js


    {
        "query" : {...},
        "highlight" : {
            "fields" : {
                "_all" : {},
                "bio.title" : {"number_of_fragments" : 0}
            }
        }
    }


When using **fast-vector-highlighter** one can use **fragment_offset** parameter to conrol the margin to start highlighting from. 


Global Settings
===============

Highlighting settings can be set on a global level and then overridden at the field level.


.. code-block:: js


    {
        "query" : {...},
        "highlight" : {
            "number_of_fragments" : 3,
            "fragment_size" : 150,
            "tag_schema" : "styled",
            "fields" : {
                "_all" : { "pre_tags" : ["<em>"], "post_tags" : ["</em>"] },
                "bio.title" : { "number_of_fragments" : 0 },
                "bio.author" : { "number_of_fragments" : 0 },
                "bio.content" : { "number_of_fragments" : 5, "order" : "score" }
            }
        }
    }


Require Field Match
===================

**require_field_match** can be set to **true** which will cause a field to be highlighted only if a query matched that field. false means that terms are highlighted on all requested fields regardless if the query matches specifically on them.


Boundary Characters
===================

When highlighting a field that is mapped with term vectors, **boundary_chars** can be configured to define what constitutes a boundary for highlighting. Its a single string with each boundary character defined in it. It defaults to **.,!? \t\n**.


The **boundary_max_size** allows to control how far to look for boundary characters, and defaults to **20**.
