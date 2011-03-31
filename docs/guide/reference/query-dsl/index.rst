=========
Query Dsl
=========

*elasticsearch* provides a full query dsl based on JSON to define queries. In general, there are basic queries such as :doc:`term <./term-query.html>`  or :doc:`prefix <./prefix-query.html>`.  There are also compound queries like the :doc:`bool <./bool-query.html>`  query. Queries can also have filters associated with them such as the :doc:`filtered <./filtered-query.html>`  or :doc:`constant_score <./constant-score-query.html>`  queries, with specific filter queries. 


Think of the Query DSL as an AST of queries. Certain queries can contain other queries (like the :doc:`bool <./bool-query.html>`  query), other can contain filters (like the :doc:`constant_score <./constnat-score-query.html)>`,  and some can contain both a query and a filter (like the :doc:`filtered <./filtered-query.html)>`.  Each of those can container *any* query of the list of queries or *any* filter from the list of filters, resulting in the ability to build quite complex (and interesting) queries.


Both queries and filters can be used in different APIs. For example, within a :doc:`search query <.//guide/reference/api/search/query.html>`,  or as a :doc:`facet filter <.//guide/reference/api/search/facets/>`.  This section explains the components (queries and filters) that can form the AST one can use.


Note
    Filters are very handy since they perform an order of magnitude better then plain queries since no scoring is required and they are automatically cached.


Filters and Caching
===================

Filters can be a great candidate for caching. Caching the result of a filter does not require a lot of memory, and will cause other queries executing against the same filter (same parameters) to be blazingly fast.


Some filters already produce a result that is easily cacheable, and the difference between caching and not caching them is the act of placing the result in the cache or not. These filters, which include the :doc:`term <./term-filter.html>`,  :doc:`terms <./terms-filter.html>`,  :doc:`prefix <./prefix-filter.html>`,  and :doc:`range <./range-filter.html>`  filters, are by default cached and are recommended to use (compared to the equivalent query version) when the same filter (same parameters) will be used across multiple different queries (for example, a range filter with age higher than 10).


Other filters, usually already working with the field data loaded into memory, are not cached by default. Those filter are already very fast, and the process of caching them requires extra processing in order to allow the filter result to be used with different queries than the one executed. This filters, including the geo filters, :doc:`numeric_range <./numeric-range-filter.html>`,  and :doc:`script <./script-filter.html>`  are not cached by default.


The last type of filters are filters that work with other filters. The :doc:`and <./and-filter.html>`,  :doc:`not <./not-filter.html>`,  and :doc:`or <./or-filter.html>`  are not cached as they basically just manipulate the internal filters.

