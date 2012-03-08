.. _es-guide-reference-query-dsl-multi-term-rewrite:

==================
Multi Term Rewrite
==================

Multi term queries, like :ref:`wildcard <es-guide-reference-query-dsl-wildcard-query>`  and :ref:`prefix <es-guide-reference-query-dsl-prefix-query>`  are called multi term queries and end up going through a process of rewrite. This also happens on the :ref:`query_string <es-guide-reference-query-dsl-query-string-query>`.  All of those queries allow to control how they will get rewritten using the **rewrite** parameter:


* When not set, or set to **constant_score_default**, defaults to automatically choosing either **constant_score_boolean** or **constant_score_filter** based on query characteristics.
* **scoring_boolean**: A rewrite method that first translates each term into a should clause in a boolean query, and keeps the scores as computed by the query. Note that typically such scores are meaningless to the user, and require non-trivial CPU to compute, so it's almost always better to use **constant_score_default**. This rewrite method will hit too many clauses failure if it exceeds the boolean query limit (defaults to **1024**).
* **constant_score_boolean**: Similar to **scoring_boolean** except scores are not computed. Instead, each matching document receives a constant score equal to the query's boost. This rewrite method will hit too many clauses failure if it exceeds the boolean query limit (defaults to **1024**).
* **constant_score_filter**: A rewrite method that first creates a private Filter by visiting each term in sequence and marking all docs for that term. Matching documents are assigned a constant score equal to the query's boost.
* **top_terms_N**: A rewrite method that first translates each term into should clause in boolean query, and keeps the scores as computed by the query. This rewrite method only uses the top scoring terms so it will not overflow boolean max clause count. The **N** controls the size of the top scoring terms to use.
* **top_terms_boost_N**: A rewrite method that first translates each term into should clause in boolean query, but the scores are only computed as the boost. This rewrite method only uses the top scoring terms so it will not overflow the boolean max clause count. The **N** controls the size of the top scoring terms to use.