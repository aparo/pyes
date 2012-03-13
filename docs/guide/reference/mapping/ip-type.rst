.. _es-guide-reference-mapping-ip-type:

=======
Ip Type
=======

An **ip** mapping type allows to store _ipv4_ addresses in a numeric form allowing to easily sort, and range query it (using ip values).


The following table lists all the attributes that can be used with an ip type:


====================  ==============================================================================================================================================================================
 Attribute             Description                                                                                                                                                                  
====================  ==============================================================================================================================================================================
**index_name**        The name of the field that will be stored in the index. Defaults to the property/field name.                                                                                  
**store**             Set to **yes** the store actual field in the index, **no** to not store it. Defaults to **no** (note, the JSON document itself is stored, and it can be retrieved from it).   
**index**             Set to **no** if the value should not be indexed. In this case, **store** should be set to **yes**, since if its not indexed and not stored, there is nothing to do with it.  
**precision_step**    The precision step (number of terms generated for each number value). Defaults to **4**.                                                                                      
**boost**             The boost value. Defaults to **1.0**.                                                                                                                                         
**null_value**        When there is a (JSON) null value for the field, use the **null_value** as the field value. Defaults to not adding the field at all.                                          
**include_in_all**    Should the field be included in the **_all** field (if enabled). Defaults to **true** or to the parent **object** type setting.                                               
====================  ==============================================================================================================================================================================
