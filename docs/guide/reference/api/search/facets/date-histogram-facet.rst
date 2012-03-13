.. _es-guide-reference-api-search-facets-date-histogram-facet:

====================
Date Histogram Facet
====================

A specific histogram facet that can work with **date** field types enhancing it over the regular :ref:`histogram facet <es-guide-reference-api-search-facets-histogram-facet>`.  Here is a quick example:


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

The **interval** allows to set the interval at which buckets will be created for each hit. It allows for the constant values of **year**, **month**, **week**, **day**, **hour**, **minute**.


The specific constant values also support setting rounding by appending : to it, and then the rounding value. For example: day:ceiling. The values are:


* **floor**: (the default), rounds to the lowest whole unit of this field.
* **ceiling**: Rounds to the highest whole unit of this field.
* **half_floor**: Round to the nearest whole unit of this field. If the given millisecond value is closer to the floor or is exactly halfway, this function behaves like floor. If the millisecond value is closer to the ceiling, this function behaves like ceiling.
* **half_ceiling**: Round to the nearest whole unit of this field. If the given millisecond value is closer to the floor, this function behaves like floor. If the millisecond value is closer to the ceiling or is exactly halfway, this function behaves like ceiling.
* **half_even**: Round to the nearest whole unit of this field. If the given millisecond value is closer to the floor, this function behaves like floor. If the millisecond value is closer to the ceiling, this function behaves like ceiling. If the millisecond value is exactly halfway between the floor and ceiling, the ceiling is chosen over the floor only if it makes this field's value even.

It also support time setting like **1.5h** (up to **w** for weeks).


Time Zone
=========

By default, times are stored as UTC milliseconds since the epoch. Thus, all computation and "bucketing" / "rounding" is done on UTC. It is possible to provide a time zone (both pre rounding, and post rounding) value, which will cause all computations to take the relevant zone into account. The time returned for each bucket/entry is milliseconds since the epoch of the provided time zone.


The parameters are **pre_zone** (pre rounding based on interval) and **post_zone** (post rounding based on interval). The **time_zone** parameter simply sets the **pre_zone** parameter. By default, those are set to **UTC**.


The zone value accepts either a numeric value for the hours offset, for example: **`time_zone" : -2**. It also accepts a format of hours and minutes, like **"time_zone" : "-02:30"**. Another option is to provide a time zone accepted as one of the values listed "here <http://joda-time.sourceforge.net/timezones.html>`_.  

Lets take an example. For **2012-04-01T04:15:30Z**, with a **pre_zone** of **-08:00**. For **day** interval, the actual time by applying the time zone and rounding falls under **2012-03-31**, so the returned value will be (in millis) of **2012-03-31T00:00:00Z** (UTC). For **hour** interval, applying the time zone results in **2012-03-31T20:15:30**, rounding it results in **2012-03-31T20:00:00**, but, we want to return it in UTC (**post_zone** is not set), so we convert it back to UTC: **2012-04-01T04:00:00Z**. Note, we are consistent in the results, returning the rounded value in UTC.


**post_zone** simply takes the result, and adds the relevant offset.


Sometimes, we want to apply the same conversion to UTC we did above for **hour** also for **day** (and up) intervals. We can set **pre_zone_adjust_large_interval** to **true**, which will apply the same conversion done for **hour** interval in the example, to **day** and above intervals (it can be set regardless of the interval, but only kick in when using **day** and higher intervals).


Factor
======

The date histogram works on numeric values (since time is stored in milliseconds since the epoch in UTC). But, sometimes, systems will store a different resolution (like seconds since UTC) in a numeric field. The **factor** parameter can be used to change the value in the field to milliseconds to actual do the relevant rounding, and then be applied again to get to the original unit. For example, when storing in a numeric field seconds resolution, the **factor** can be set to **1000**.


Pre / Post Offset
=================

Specific offsets can be provided for pre rounding and post rounding. The **pre_offset** for pre rounding, and **post_offset** for post rounding. The format is the date time format (**1h**, **1d**, ...).


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

