.. _es-guide-reference-query-dsl-index:
.. _es-guide-reference-query-dsl:

=========
Query Dsl
=========

*elasticsearch* provides a full Query DSL based on JSON to define queries. In general, there are basic queries such as :ref:`term <es-guide-reference-query-dsl-term-query>`  or :ref:`prefix <es-guide-reference-query-dsl-prefix-query>`.  There are also compound queries like the :ref:`bool <es-guide-reference-query-dsl-bool-query>`  query. Queries can also have filters associated with them such as the :ref:`filtered <es-guide-reference-query-dsl-filtered-query>`  or :ref:`constant_score <es-guide-reference-query-dsl-constant-score-query>`  queries, with specific filter queries. 


Think of the Query DSL as an AST of queries. Certain queries can contain other queries (like the :ref:`bool <es-guide-reference-query-dsl-bool-query>`  query), other can contain filters (like the :ref:`constant_score <es-guide-reference-query-dsl-constant-score-query>`,  and some can contain both a query and a filter (like the :ref:`filtered <es-guide-reference-query-dsl-filtered-query>`.  Each of those can contain *any* query of the list of queries or *any* filter from the list of filters, resulting in the ability to build quite complex (and interesting) queries.


Both queries and filters can be used in different APIs. For example, within a :ref:`search query <es-guide-reference-api-search-query>`,  or as a :ref:`facet filter <es-guide-reference-api-search-facets>`.  This section explains the components (queries and filters) that can form the AST one can use.


Note
    Filters are very handy since they perform an order of magnitude better then plain queries since no scoring is performed and they are automatically cached.


Filters and Caching
===================

Filters can be a great candidate for caching. Caching the result of a filter does not require a lot of memory, and will cause other queries executing against the same filter (same parameters) to be blazingly fast.


Some filters already produce a result that is easily cacheable, and the difference between caching and not caching them is the act of placing the result in the cache or not. These filters, which include the :ref:`term <es-guide-reference-query-dsl-term-filter>`,  :ref:`terms <es-guide-reference-query-dsl-terms-filter>`,  :ref:`prefix <es-guide-reference-query-dsl-prefix-filter>`,  and :ref:`range <es-guide-reference-query-dsl-range-filter>`  filters, are by default cached and are recommended to use (compared to the equivalent query version) when the same filter (same parameters) will be used across multiple different queries (for example, a range filter with age higher than 10).


Other filters, usually already working with the field data loaded into memory, are not cached by default. Those filters are already very fast, and the process of caching them requires extra processing in order to allow the filter result to be used with different queries than the one executed. These filters, including the geo, :ref:`numeric_range <es-guide-reference-query-dsl-numeric-range-filter>`,  and :ref:`script <es-guide-reference-query-dsl-script-filter>`  filters are not cached by default.


The last type of filters are those working with other filters. The :ref:`and <es-guide-reference-query-dsl-and-filter>`,  :ref:`not <es-guide-reference-query-dsl-not-filter>`  and :ref:`or <es-guide-reference-query-dsl-or-filter>`  filters are not cached as they basically just manipulate the internal filters.


All filters allow to set **_cache** element on them to explicitly control caching. They also allow to set **_cache_key** which will be used as the caching key for that filter. This can be handy when using very large filters (like a terms filter with many elements in it).


Query:

.. toctree::
    :maxdepth: 1

    bool-query
    boosting-query
    constant-score-query
    custom-boost-factor-query
    custom-score-query
    dis-max-query
    field-query
    filtered-query
    flt-field-query
    flt-query
    fuzzy-query
    has-child-query
    ids-query
    indices-query
    match-all-query
    mlt-field-query
    mlt-query
    multi-term-rewrite
    nested-query
    prefix-query
    query-string-query
    range-query
    span-first-query
    span-near-query
    span-not-query
    span-or-query
    span-term-query
    term-query
    terms-query
    text-query
    top-children-query
    wildcard-query

Filter:

.. toctree::
    :maxdepth: 1

    and-filter
    bool-filter
    custom-filters-score-query
    exists-filter
    geo-bounding-box-filter
    geo-distance-filter
    geo-distance-range-filter
    geo-polygon-filter
    has-child-filter
    ids-filter
    limit-filter
    match-all-filter
    missing-filter
    nested-filter
    not-filter
    numeric-range-filter
    or-filter
    prefix-filter
    query-filter
    range-filter
    script-filter
    term-filter
    terms-filter
    type-filter
