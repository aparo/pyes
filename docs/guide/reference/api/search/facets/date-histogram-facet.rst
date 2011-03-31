====================
Date Histogram Facet
====================

A specific histogram facet that can work with **date** field types enhancing it over the regular :doc:`histogram facet <./histogram-facet.html>`.  Here is a quick example:


.. code-block:: js


    {
        "query" : {
            "match_all" : {}
        },
        "facets" : {
            "histo1" : {
                "date_histogram" : {
                    "field" : "field_name",
                    "interval" : "day"
                }
            }
        }
    }


Interval
========

The **interval** allows to set the interval at which buckets will be created for each hit. It allows for the constant values of **year**, **month**, **day**, **hour**, **minute**.


The specific constant values also support setting rounding by appending : to it, and then the rounding value. For example: day:ceiling. The values are:


* **floor**: (the default), rounds to the lowest whole unit of this field.
* **ceiling**: Rounds to the highest whole unit of this field.
* **half_floor**: Round to the nearest whole unit of this field. If the given millisecond value is closer to the floor or is exactly halfway, this function behaves like floor. If the millisecond value is closer to the ceiling, this function behaves like ceiling.
* **half_ceiling**: Round to the nearest whole unit of this field. If the given millisecond value is closer to the floor, this function behaves like floor. If the millisecond value is closer to the ceiling or is exactly halfway, this function behaves like ceiling.
* **half_even**: Round to the nearest whole unit of this field. If the given millisecond value is closer to the floor, this function behaves like floor. If the millisecond value is closer to the ceiling, this function behaves like ceiling. If the millisecond value is exactly halfway between the floor and ceiling, the ceiling is chosen over the floor only if it makes this field's value even.

It also support time setting like **1.5h** (up to **w** for weeks).


Time Zone
=========

By default, times are stored as UTC milliseconds since the epoch. Thus, all computation and "bucketing" / "rounding" is done on UTC. It is possible to provide a **zone** value, which will cause all computations to take the relevant zone into account. The time returned for each bucket/entry is milliseconds since the epoch of the provided time zone.


The zone value accepts either a numeric value for the hours offset, for example: **`zone" : -2**. It also accepts a format of hours and minutes, like **"zone" : "-02:30"**. Another option is to provide a time zone accepted as one of the values listed "here <http://joda-time.sourceforge.net/timezones.html>`_.  

Value Field
===========

The date_histogram facet allows to use a different key (of type date) which controls the bucketing, with a different value field which will then return the total and mean for that field values of the hits within the relevant bucket. For example:


.. code-block:: js


    {
        "query" : {
            "match_all" : {}
        },
        "facets" : {
            "histo1" : {
                "histogram" : {
                    "key_field" : "timestamp",
                    "value_field" : "price",
                    "interval" : "day"
                }
            }
        }
    }


Script Value Field
==================

A script can be used to compute the value that will then be used to compute the total and mean for a bucket. For example:


.. code-block:: js


    {
        "query" : {
            "match_all" : {}
        },
        "facets" : {
            "histo1" : {
                "histogram" : {
                    "key_field" : "timestamp",
                    "value_script" : "doc['price'].value * 2",
                    "interval" : "day"
                }
            }
        }
    }

