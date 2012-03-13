.. _es-guide-reference-modules-scripting:

=========
Scripting
=========

The scripting module allows to use scripts in order to evaluate custom expressions. For example, scripts can be used to return "script fields" as part of a search request, or can be used to evaluate a custom score for a query and so on.


The scripting module uses by default `mvel <http://mvel.codehaus.org/>`_  as the scripting language with some extensions. mvel is used since its extremely fast and very simple to use, and in most cases, simple expressions are needed (for example, mathematical equations).


Additional **lang** plugins are provided to allow to execute scripts in different languages. Currently supported plugins are **lang-javascript** for JavaScript, **lang-groovy** for Groovy, and **lang-python** for Python. All places where a `script` parameter can be used, a **lang** parameter (on the same level) can be provided to define the language of the script. The **lang** options are **mvel**, **js**, **groovy**, **python**, and **native**.


Default Scripting Language
==========================

The default scripting language (assuming no **lang** parameter is provided) is **mvel**. In order to change it set the **script.default_lang** to the appropriate language.


Preloaded Scripts
=================

Scripts can always be provided as part of the relevant API, but they can also be preloaded by placing them under `config/scripts` and then referencing them by the script name (instead of providing the full script). This helps reduce the amount of data passed between the client and the nodes.


The name of the script is derived from the hierarchy of directories it exists under, and the file name without the lang extension. For example, a script placed under `config/scripts/group1/group2/test.py` will be named `group1_group2_test`.


Native (Java) Scripts
=====================

Even though **mvel** is pretty fast, allow to register native Java based scripts for faster execution.


In order to allow for scripts, the **NativeScriptFactory** needs to be implemented that constructs the script that will be executed. There are two main types, one that extends **AbstractExecutableScript** and one that extends **AbstractSearchScript** (probably the one most users will extend, with additional helper classes in **AbstractLongSearchScript**, **AbstractDoubleSearchScript**, and **AbstractFloatSearchScript**).


Registering them can either be done by settings, for example: **script.native.my.type** set to **sample.MyNativeScriptFactory** will register a script named **my**. Another option is in a plugin, access **ScriptModule** and call **registerScript** on it.


Executing the script is done by specifying the **lang** as **native**, and the name of the script as the **script**.


Note, the scripts need to be in the classpath of elasticsearch. One simple way to do it is to create a directory under plugins (choose a descriptive name), and place the jar / classes files there, they will be automatically loaded.


Score
=====

In all scripts that can be used in facets, allow to access the current doc score using **doc.score**.


Document Fields
===============

Most scripting revolve around the use of specific document fields data. The **doc['field_name']** can be used to access specific field data within a document (the document in question is usually derived by the context the script is used). Document fields are very fast to access since they end up being loaded into memory (all the relevant field values/tokens are loaded to memory).


The following data can be extracted from a field:


====================================================  =====================================================================================================================================================================================================================================================================
 Expression                                            Description                                                                                                                                                                                                                                                         
====================================================  =====================================================================================================================================================================================================================================================================
**doc['field_name'].value**                           The native value of the field. For example, if its a short type, it will be short.                                                                                                                                                                                   
**doc['field_name'].values**                          The native array values of the field. For example, if its a short type, it will be short[]. Remember, a field can have several values within a single doc. Returns an empty array if the field has no values.                                                        
**doc['field_name'].stringValue**                     The string value of the field.                                                                                                                                                                                                                                       
**doc['field_name'].doubleValue**                     The converted double of the field. Replace `double` with `int`, `long`, `float`, `short`, `byte` for the respective values.                                                                                                                                          
**doc['field_name'].doubleValues**                    A converted double values array.                                                                                                                                                                                                                                     
**doc['field_name'].date**                             Applies only to date / long (timestamp) types, returns a `MutableDateTime <http://joda-time.sourceforge.net/api-release/org/joda/time/MutableDateTime.html>`_  `_  allowing to get date / time specific data. For example: **doc['field_name'].date.minuteOfHour**  
**doc['field_name'].dates**                           Return an array of date values for the field.                                                                                                                                                                                                                        
**doc['field_name'].empty**                           A boolean indicating if the field has no values within the doc.                                                                                                                                                                                                      
**doc['field_name'].multiValued**                     A boolean indicating that the field has several values within the corpus.                                                                                                                                                                                            
**doc['field_name'].lat**                             The latitude of a geo point type.                                                                                                                                                                                                                                    
**doc['field_name'].lon**                             The longitude of a geo point type.                                                                                                                                                                                                                                   
**doc['field_name'].lats**                            The latitudes of a geo point type.                                                                                                                                                                                                                                   
**doc['field_name'].lons**                            The longitudes of a geo point type.                                                                                                                                                                                                                                  
**doc['field_name'].distance(lat, lon)**              The distance (in miles) of this geo point field from the provided lat/lon.                                                                                                                                                                                           
**doc['field_name'].distanceInKm(lat, lon)**          The distance (in km) of this geo point field from the provided lat/lon.                                                                                                                                                                                              
**doc['field_name'].geohashDistance(geohash)**        The distance (in miles) of this geo point field from the provided geohash.                                                                                                                                                                                           
**doc['field_name'].geohashDistanceInKm(geohash)**    The distance (in km) of this geo point field from the provided geohash.                                                                                                                                                                                              
====================================================  =====================================================================================================================================================================================================================================================================

Stored Fields
=============

Stored fields can also be accessed when executed a script. Note, they are much slower to access compared with document fields, but are not loaded into memory. They can be simply accessed using **_fields['my_field_name'].value** or **_fields['my_field_name'].values**.


Source Field
============

The source field can also be accessed when executing a script. The source field is loaded per doc, parsed, and then provided to the script for evaluation. The **_source** forms the context under which the source field can be accessed, for example **_source.obj2.obj1.field3**.


mvel Built In Functions
=======================

There are several built in functions that can be used within scripts. They include:


===========================  =================================================================================================================================================
 Function                     Description                                                                                                                                     
===========================  =================================================================================================================================================
**time**                     The current time in milliseconds.                                                                                                                
**sin(a)**                   Returns the trigonometric sine of an angle.                                                                                                      
**cos(a)**                   Returns the trigonometric cosine of an angle.                                                                                                    
**tan(a)**                   Returns the trigonometric tangent of an angle.                                                                                                   
**asin(a)**                  Returns the arc sine of a value.                                                                                                                 
**acos(a)**                  Returns the arc cosine of a value.                                                                                                               
**atan(a)**                  Returns the arc tangent of a value.                                                                                                              
**toRadians(angdeg)**        Converts an angle measured in degrees to an approximately equivalent angle measured in radians                                                   
**toDegrees(angrad)**        Converts an angle measured in radians to an approximately equivalent angle measured in degrees.                                                  
**exp(a)**                   Returns Euler's number _e_ raised to the power of value.                                                                                         
**log(a)**                   Returns the natural logarithm (base _e_) of a value.                                                                                             
**log10(a)**                 Returns the base 10 logarithm of a value.                                                                                                        
**sqrt(a)**                  Returns the correctly rounded positive square root of a value.                                                                                   
**cbrt(a)**                  Returns the cube root of a double value.                                                                                                         
**IEEEremainder(f1, f2)**    Computes the remainder operation on two arguments as prescribed by the IEEE 754 standard.                                                        
**ceil(a)**                  Returns the smallest (closest to negative infinity) value that is greater than or equal to the argument and is equal to a mathematical integer.  
**floor(a)**                 Returns the largest (closest to positive infinity) value that is less than or equal to the argument and is equal to a mathematical integer.      
**rint(a)**                  Returns the value that is closest in value to the argument and is equal to a mathematical integer.                                               
**atan2(y, x)**              Returns the angle <i>theta</i> from the conversion of rectangular coordinates (_x_, _y_) to polar coordinates (r,_theta_).                       
**pow(a, b)**                Returns the value of the first argument raised to the power of the second argument.                                                              
**round(a)**                 Returns the closest _int_ to the argument.                                                                                                       
**random()**                 Returns a random _double_ value.                                                                                                                 
**abs(a)**                   Returns the absolute value of a value.                                                                                                           
**max(a, b)**                Returns the greater of two values.                                                                                                               
**min(a, b)**                Returns the smaller of two values.                                                                                                               
**ulp(d)**                   Returns the size of an ulp of the argument.                                                                                                      
**signum(d)**                Returns the signum function of the argument.                                                                                                     
**sinh(x)**                  Returns the hyperbolic sine of a value.                                                                                                          
**cosh(x)**                  Returns the hyperbolic cosine of a value.                                                                                                        
**tanh(x)**                  eturns the hyperbolic tangent of a value.                                                                                                        
**hypot(x, y)**              Returns sqrt(_x^2_ + _y^2_) without intermediate overflow or underflow.                                                                          
===========================  =================================================================================================================================================
