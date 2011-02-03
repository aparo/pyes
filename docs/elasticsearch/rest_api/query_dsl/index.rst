Query DSL
=========

ElasticSearch provides a full query dsl based on JSON to define queries. In general, there are basic queries such as **term** or **prefix**. There are also compound queries like the **bool** query. Queries can also have filters associated with them such as the **filtered** or **constant_score** queries, with specific filter queries. 


Note
    Filters are very handy since they perform an order of magnitude better then plain queries since no scoring is required and they are automatically cached.


Queries
-------

=====================================================================  =====================================================================================================================================================================================================================================================
 API                                                                    Description                                                                                                                                                                                                                                         
=====================================================================  =====================================================================================================================================================================================================================================================
:doc:`term <./term_query/index>`                                       Matches documents that have fields that contain a a term (*not analyzed*).                                                                                                                                                                           
:doc:`terms <./terms_query/index>`                                     Matches documents that have fields that match any of the listed terms (*not analyzed*).                                                                                                                                                              
:doc:`range <./range_query/index>`                                     Matches documents with fields that have terms within a certain range.                                                                                                                                                                                
:doc:`prefix <./prefix_query/index>`                                   Matches documents that have fields containing terms with a specified prefix.                                                                                                                                                                         
:doc:`wildcard <./wildcard_query/index>`                               Matches documents that have fields matching a wildcard expression.                                                                                                                                                                                   
:doc:`fuzzy <./fuzzy_query/index>`                                     A fuzzy based query that uses similarity based on Levenshtein (edit distance) algorithm.                                                                                                                                                             
:doc:`match_all <./match_all_query/index>`                             A query that matches all documents.                                                                                                                                                                                                                  
:doc:`query_string <./query_string_query/index>`                       A query that uses a query parser in order to parse a query string.                                                                                                                                                                                   
:doc:`field <./field_query/index>`                                     A query that executes a query string against a specific field.                                                                                                                                                                                       
:doc:`bool <./bool_query/index>`                                       A query that matches documents matching boolean combinations of other queries.                                                                                                                                                                       
:doc:`dis_max <./dis_max_query/index>`                                 A query that generates the union of documents produced by its subqueries, and that scores each document with the maximum score for that document as produced by any subquery, plus a tie breaking increment for any additional matching subqueries.  
:doc:`constant_score <./constant_score_query/index>`                   A query that wraps a filter and simply returns a constant score equal to the query boost for every document in the filter.                                                                                                                           
:doc:`filtered <./filtered_query/index>`                               A query that applies a filter to the results of another query.                                                                                                                                                                                       
:doc:`more_like_this <./more_like_this_query/index>`                   More like this query find documents that are "like" provided text by running it against one or more fields.                                                                                                                                          
:doc:`more_like_this_field <./more_like_this_field_query/index>`       More like this query find documents that are "like" provided text by running it against a field.                                                                                                                                                     
:doc:`fuzzy_like_this <./fuzzy_like_this_query/index>`                 Fuzzy like this query find documents that are "like" provided text by running it against one or more fields.                                                                                                                                         
:doc:`fuzzy_like_this_field <./fuzzy_like_this_field_query/index>`     Fuzzy like this query find documents that are "like" provided text by running it against a field.                                                                                                                                                    
:doc:`span_term <./span_term_query/index>`                             Matches spans containing a term.                                                                                                                                                                                                                     
:doc:`span_first <./span_first_query/index>`                           Matches spans near the beginning of a field.                                                                                                                                                                                                         
:doc:`span_near <./span_near_query/index>`                             Matches spans which are near one another.                                                                                                                                                                                                            
:doc:`span_not <./span_not_query/index>`                               Removes matches which overlap with another span query.                                                                                                                                                                                               
:doc:`span_or <./span_or_query/index>`                                 Matches the union of its span query clauses.                                                                                                                                                                                                         
:doc:`custom_score <./custom_score_query/index>`                       Wraps another query and provides custom scripted score computation.                                                                                                                                                                                  
:doc:`has_child <./has_child_query/index>`                             A query that runs a sub query against child docs, returning their matching parents.                                                                                                                                                                  
=====================================================================  =====================================================================================================================================================================================================================================================

Filters
-------

============================================================  =========================================================================================================================
 API                                                           Description                                                                                                             
============================================================  =========================================================================================================================
:doc:`script <./script_filter/index>`                         A filter defined by a custom script.                                                                                     
:doc:`term <./term_filter/index>`                             Filters documents that have fields that contain a term (*not analyzed*).                                                 
:doc:`terms <./terms_filter/index>`                           Filters documents that have fields that match any of the listed terms (*not analyzed*).                                  
:doc:`range <./range_filter/index>`                           Filters documents with fields that have terms within a certain range.                                                    
:doc:`numeric_range <./numeric_range_filter/index>`           Filters documents with numeric field between a specific range. Faster than `range` filter, though requires more memory.  
:doc:`prefix <./prefix_filter/index>`                         Filters documents that have fields containing terms with a specified prefix.                                             
:doc:`bool <./bool_filter/index>`                             A filter that matches documents matching boolean combinations of other queries.                                          
:doc:`query <./query_filter/index>`                           Wraps any query to be used as a filter.                                                                                  
:doc:`and <./and_filter/index>`                               A filter that matches documents using **AND** boolean operator on other queries.                                         
:doc:`or <./or_filter/index>`                                 A filter that matches documents using **OR** boolean operator on other queries.                                          
:doc:`not <./not_filter/index>`                               A filter that filters out matched documents using a query.                                                               
:doc:`geo_distance <./geo_distance_filter/index>`             Filters documents based on a distance from a geo point.                                                                  
:doc:`geo_bounding_box <./geo_bounding_box_filter/index>`     Filters documents that falls within a bounding box.                                                                      
:doc:`geo_polygon <./geo_polygon_filter/index>`               Filters documents that falls within a geo polygon.                                                                       
:doc:`match_all <./match_all_filter/index>`                   A filter that matches on all documents.                                                                                  
:doc:`exists <./exists_filter/index>`                         Filters documents where a field has a value in them.                                                                     
:doc:`missing <./missing_filter/index>`                       Filters documents where a field doesn't have a value in them.                                                            
:doc:`has_child <./has_child_filter/index>`                   A filter that runs a sub query against child docs, returning their matching parents.                                     
:doc:`top_children <./top_children_query/index>`              A query that runs a sub query against child docs returning matching parents, while retaining scoring.                    
============================================================  =========================================================================================================================

Filters and Caching
-------------------

Filters can be a great candidate for caching. Caching the result of a filter does not require a lot of memory, and will cause other queries executing against the same filter (same parameters) to be blazingly fast.


Some filters already produce a result that is easily cacheable, and the different between caching and not caching them is the act of placing the result in the cache or not. This filters, which include the `term`, `terms`, `prefix`, and `range` filters, are by default cached. These filters are recommended to use (compared to the equivalent query version) when the same filter (same parameters) will be used across multiple different queries (for example, a range filter with age higher than 10).


Other filters, usually already working with the field data loaded into memory, are not cached by default. Those filter are already very fast, and the process of caching them requires extra processing in order to allow the filter result to be used with different queries than the one executed. This filters, including the geo filters, `numeric_range`, and `script` are not cached by default.


The last type of filters are filters that work with other filters. The `and`, `not`, and `or` are not cached as they basically just manipulate the internal filters.

