.. _es-guide-reference-mapping-date-format:

===========
Date Format
===========

When defining a **date** type, or when defining **date_formats** in the **object** mapping, the value of it is the actual date format that will be used to parse the string representation of the date. There are built in formats supported, as well as complete custom one.


The parsing of dates uses `Joda <http://joda-time.sourceforge.net/>`_.  The default date parsing used if no format is specified is `ISODateTimeFormat.dateOptionalTimeParser() <http://joda-time.sourceforge.net/api-release/org/joda/time/format/ISODateTimeFormat.html#dateOptionalTimeParser()>`_.  

An extension to the format allow to define several formats using **||** separator. This allows to define less strict formats that can be used, for example, the **yyyy/MM/dd HH:mm:ss||yyyy/MM/dd** format will parse both **yyyy/MM/dd HH:mm:ss** and **yyyy/MM/dd**. The first format will also act as the one that converts back from milliseconds to a string representation.


Date Math
=========

The **date** type supports using date math expression when using it in a query/filter (mainly make sense in **range** query/filter).


The expression starts with an "anchor" date, which can be either **now** or a date string (in the applicable format) ending with **||**. It can then follow by a math expression, supporting **+**, **-** and **/** (rounding). The units supported are **M** (month), **w** (week), **h** (hour), **m** (minute), and **s** (second).


Here are some samples: **now+1h**, **now+1h+1m**, **now+1h/d**, **2012-01-01||+1M/d**.


Note, when doing **range** type searches, and the upper value is inclusive, the rounding will properly be rounded to the ceiling instead of flooring it.


Built In Formats
================

The following tables lists all the defaults ISO formats supported:


===================================  ==========================================================================================================================================================================================
 Name                                 Description                                                                                                                                                                              
===================================  ==========================================================================================================================================================================================
basic_date                           A basic formatter for a full date as four digit year, two digit month of year, and two digit day of month (yyyyMMdd).                                                                     
basic_date_time                      A basic formatter that combines a basic date and time, separated by a 'T' (yyyyMMdd'T'HHmmss.SSSZ).                                                                                       
basic_date_time_no_millis            A basic formatter that combines a basic date and time without millis, separated by a 'T' (yyyyMMdd'T'HHmmssZ).                                                                            
basic_ordinal_date                   A formatter for a full ordinal date, using a four digit year and three digit dayOfYear (yyyyDDD).                                                                                         
basic_ordinal_date_time              A formatter for a full ordinal date and time, using a four digit year and three digit dayOfYear (yyyyDDD'T'HHmmss.SSSZ).                                                                  
basic_ordinal_date_time_no_millis    A formatter for a full ordinal date and time without millis, using a four digit year and three digit dayOfYear (yyyyDDD'T'HHmmssZ).                                                       
basic_time                           A basic formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, three digit millis, and time zone offset (HHmmss.SSSZ).                              
basic_time_no_millis                 A basic formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, and time zone offset (HHmmssZ).                                                      
basic_t_time                         A basic formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, three digit millis, and time zone off set prefixed by 'T' ('T'HHmmss.SSSZ).          
basic_t_time_no_millis               A basic formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, and time zone offset prefixed by 'T' ('T'HHmmssZ).                                   
basic_week_date                      A basic formatter for a full date as four digit weekyear, two digit week of weekyear, and one digit day of week (xxxx'W'wwe).                                                             
basic_week_date_time                 A basic formatter that combines a basic weekyear date and time, separated by a 'T' (xxxx'W'wwe'T'HHmmss.SSSZ).                                                                            
basic_week_date_time_no_millis       A basic formatter that combines a basic weekyear date and time without millis, separated by a 'T' (xxxx'W'wwe'T'HHmmssZ).                                                                 
date                                 A formatter for a full date as four digit year, two digit month of year, and two digit day of month (yyyy-MM-dd).                                                                         
date_hour                            A formatter that combines a full date and two digit hour of day.                                                                                                                          
date_hour_minute                     A formatter that combines a full date, two digit hour of day, and two digit minute of hour.                                                                                               
date_hour_minute_second              A formatter that combines a full date, two digit hour of day, two digit minute of hour, and two digit second of minute.                                                                   
date_hour_minute_second_fraction     A formatter that combines a full date, two digit hour of day, two digit minute of hour, two digit second of minute, and three digit fraction of second (yyyy-MM-dd'T'HH:mm:ss.SSS).       
date_hour_minute_second_millis       A formatter that combines a full date, two digit hour of day, two digit minute of hour, two digit second of minute, and three digit fraction of second (yyyy-MM-dd'T'HH:mm:ss.SSS).       
date_optional_time                   a generic ISO datetime parser where the date is mandatory and the time is optional.                                                                                                       
date_time                            A formatter that combines a full date and time, separated by a 'T' (yyyy-MM-dd'T'HH:mm:ss.SSSZZ).                                                                                         
date_time_no_millis                  A formatter that combines a full date and time without millis, separated by a 'T' (yyyy-MM-dd'T'HH:mm:ssZZ).                                                                              
hour                                 A formatter for a two digit hour of day.                                                                                                                                                  
hour_minute                          A formatter for a two digit hour of day and two digit minute of hour.                                                                                                                     
hour_minute_second                   A formatter for a two digit hour of day, two digit minute of hour, and two digit second of minute.                                                                                        
hour_minute_second_fraction          A formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, and three digit fraction of second (HH:mm:ss.SSS).                                         
hour_minute_second_millis            A formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, and three digit fraction of second (HH:mm:ss.SSS).                                         
ordinal_date                         A formatter for a full ordinal date, using a four digit year and three digit dayOfYear (yyyy-DDD).                                                                                        
ordinal_date_time                    A formatter for a full ordinal date and time, using a four digit year and three digit dayOfYear (yyyy-DDD'T'HH:mm:ss.SSSZZ).                                                              
ordinal_date_time_no_millis          A formatter for a full ordinal date and time without millis, using a four digit year and three digit dayOfYear (yyyy-DDD'T'HH:mm:ssZZ).                                                   
time                                 A formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, three digit fraction of second, and time zone offset (HH:mm:ss.SSSZZ).                     
time_no_millis                       A formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, and time zone offset (HH:mm:ssZZ).                                                         
t_time                               A formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, three digit fraction of second, and time zone offset prefixed by 'T' ('T'HH:mm:ss.SSSZZ).  
t_time_no_millis                     A formatter for a two digit hour of day, two digit minute of hour, two digit second of minute, and time zone offset prefixed by 'T' ('T'HH:mm:ssZZ).                                      
week_date                            A formatter for a full date as four digit weekyear, two digit week of weekyear, and one digit day of week (xxxx-'W'ww-e).                                                                 
week_date_time                       A formatter that combines a full weekyear date and time, separated by a 'T' (xxxx-'W'ww-e'T'HH:mm:ss.SSSZZ).                                                                              
weekDateTimeNoMillis                 A formatter that combines a full weekyear date and time without millis, separated by a 'T' (xxxx-'W'ww-e'T'HH:mm:ssZZ).                                                                   
week_year                            A formatter for a four digit weekyear.                                                                                                                                                    
weekyearWeek                         A formatter for a four digit weekyear and two digit week of weekyear.                                                                                                                     
weekyearWeekDay                      A formatter for a four digit weekyear, two digit week of weekyear, and one digit day of week.                                                                                             
year                                 A formatter for a four digit year.                                                                                                                                                        
year_month                           A formatter for a four digit year and two digit month of year.                                                                                                                            
year_month_day                       A formatter for a four digit year, two digit month of year, and two digit day of month.                                                                                                   
===================================  ==========================================================================================================================================================================================

Custom Format
=============

Allows for a completely customizable date format explained `here <http://joda-time.sourceforge.net/api-release/org/joda/time/format/DateTimeFormat.html>`_.  _.  
