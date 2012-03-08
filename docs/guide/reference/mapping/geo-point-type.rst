.. _es-guide-reference-mapping-geo-point-type:

==============
Geo Point Type
==============

Mapper type called **geo_point** to support geo based points. The declaration looks as follows:


.. code-block:: js


    {
        "pin" : {
            "properties" : {
                "location" : {
                    "type" : "geo_point"
                }
            }
        }
    }


Indexed Fields
==============

The **geo_point** mapping will index a single field with the format of **lat,lon**. The **lat_lon** option can be set to also index the **.lat** and **.lon** as numeric fields, and **geohash** can be set to **true** to also index **.geohash** value.


A good practice is to enable indexing **lat_lon** as well, since both the geo distance and bounding box filters can either be executed using in memory checks, or using the indexed lat lon values, and it really depends on the data set which one performs better. Note though, that indexed lat lon only make sense when there is a single geo point value for the field, and not multi values.


Input Structure
===============

The above mapping defines a **geo_point**, which accepts different formats. The following formats are supported:

Lat Lon as Properties
---------------------

.. code-block:: js


    {
        "pin" : {
            "location" : {
                "lat" : 41.12,
                "lon" : -71.34
            }
        }
    }


Lat Lon as String
-----------------

Format in **lat,lon**.


.. code-block:: js


    {
        "pin" : {
            "location" : "41.12,-71.34"
        }
    }


Geohash
-------

.. code-block:: js


    {
        "pin" : {
            "location" : "drm3btev3e86"
        }
    }


Lat Lon as Array
----------------

Format in **[lon, lat]**, note, the order of lon/lat here in order to conform with `GeoJSON <http://geojson.org/>`_.  

.. code-block:: js


    {
        "pin" : {
            "location" : [-71.34, 41.12]
        }
    }



Mapping Options
===============

=======================  ===========================================================================================
 Option                   Description                                                                               
=======================  ===========================================================================================
**lat_lon**              Set to **true** to also index the **.lat** and **.lon** as fields. Defaults to **false**.  
**geohash**              Set to **true** to also index the **.geohash** as a field. Defaults to **false**.          
**geohash_precision**    Sets the geohash precision, defaults to 12.                                                
=======================  ===========================================================================================

Usage in Scripts
================

When using **doc[geo_field_name]** (in the above mapping, **doc['location']**), the **doc[...].value** returns a **GeoPoint**, which then allows access to **lat** and **lon** (for example, **doc[...].value.lat**). For performance, it is better to access the **lat** and **lon** directly using **doc[...].lat** and **doc[...].lon**.


