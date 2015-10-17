# -*- coding: utf-8 -*-

import six
from .exceptions import InvalidQuery, InvalidParameterQuery, QueryError, \
    ScriptFieldsError
from .sort import SortFactory
from .facets import FacetFactory
from .aggs import AggFactory
from .filters import ANDFilter, Filter
from .highlight import HighLighter
from .scriptfields import ScriptFields
from .utils import clean_string, ESRange, EqualityComparableUsingAttributeDictionary

class Suggest(EqualityComparableUsingAttributeDictionary):
    def __init__(self, fields=None):
        self.fields = fields or {}

    def add(self, text, name, field, type='term', size=None, params=None):
        """
        Set the suggester of given type.

        :param text: text
        :param name: name of suggest
        :param field: field to be used
        :param type: type of suggester to add, available types are: completion,
                     phrase, term
        :param size: number of phrases
        :param params: dict of additional parameters to pass to the suggester
        :return: None
        """
        func = None

        if type == 'completion':
            func = self.add_completion
        elif type == 'phrase':
            func = self.add_phrase
        elif type == 'term':
            func = self.add_term
        else:
            raise InvalidQuery('Invalid type')

        func(text=text, name=name, field=field, size=size, params=params)

    def add_completion(self, text, name, field, size=None, params=None):
        """
        Add completion-type suggestion:

        http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/search-suggesters-completion.html

        :param text: text for searching using autocompletion
        :param name: name for the suggester
        :param field: document's field to be autocompleted
        :param size: (optional) size of the autocomplete list
        :return:
        """
        data = {
            'field': field
        }

        if size:
            data['size'] = size

        if params:
            data.update(params)

        self.fields[name] = {
            'text': text,
            'completion': data,
        }


    def add_term(self, text, name, field, size=None, params=None):
        data = {"field": field}

        if size:
            data["size"] = size

        if params:
            data.update(params)

        self.fields[name] = {"text": text, "term": data}

    def add_phrase(self, text, name, field, size=None, params=None):
        tokens = text.split()
        gram = field + ".bigram"
        # if len(tokens) > 3:
        #     gram = field + ".trigram"

        data = {
            "analyzer": "standard_lower",
            "field": gram,
            "size": 4,
            "real_word_error_likelihood": 0.95,
            "confidence": 2.0,
            "gram_size": 2,
            "direct_generator": [{
                                     "field": field + ".tkl",
                                     "suggest_mode": "always",
                                     "min_word_len": 1
                                 }, {
                                     "field": field + ".reverse",
                                     "suggest_mode": "always",
                                     "min_word_len": 1,
                                     "pre_filter": "reverse",
                                     "post_filter": "reverse"
                                 }]
        }

        if size:
            data["size"] = size

        if params:
            data.update(params)

        self.fields[name] = {"text": text, "phrase": data}

    def is_valid(self):
        return len(self.fields) > 0

    def serialize(self):
        return self.fields

class FieldParameter(EqualityComparableUsingAttributeDictionary):

    def __init__(self, field, query, default_operator="OR", analyzer=None,
                 allow_leading_wildcard=True, lowercase_expanded_terms=True,
                 enable_position_increments=True, fuzzy_prefix_length=0,
                 fuzzy_min_sim=0.5, phrase_slop=0, boost=1.0):
        self.query = query
        self.field = field
        self.default_operator = default_operator
        self.analyzer = analyzer
        self.allow_leading_wildcard = allow_leading_wildcard
        self.lowercase_expanded_terms = lowercase_expanded_terms
        self.enable_position_increments = enable_position_increments
        self.fuzzy_prefix_length = fuzzy_prefix_length
        self.fuzzy_min_sim = fuzzy_min_sim
        self.phrase_slop = phrase_slop
        self.boost = boost

    def serialize(self):
        filters = {}

        if self.default_operator != "OR":
            filters["default_operator"] = self.default_operator
        if self.analyzer:
            filters["analyzer"] = self.analyzer
        if not self.allow_leading_wildcard:
            filters["allow_leading_wildcard"] = self.allow_leading_wildcard
        if not self.lowercase_expanded_terms:
            filters["lowercase_expanded_terms"] = self.lowercase_expanded_terms
        if not self.enable_position_increments:
            filters["enable_position_increments"] = self.enable_position_increments
        if self.fuzzy_prefix_length:
            filters["fuzzy_prefix_length"] = self.fuzzy_prefix_length
        if self.fuzzy_min_sim != 0.5:
            filters["fuzzy_min_sim"] = self.fuzzy_min_sim
        if self.phrase_slop:
            filters["phrase_slop"] = self.phrase_slop

        if self.boost != 1.0:
            filters["boost"] = self.boost
        if filters:
            filters["query"] = self.query
        else:
            filters = self.query
        return self.field, filters


class Search(EqualityComparableUsingAttributeDictionary):
    """A search to be performed.

    This contains a query, and has additional parameters which are used to
    control how the search works, what it should return, etc.

    The rescore parameter takes a Search object created from a RescoreQuery.

    Example:

    q = QueryStringQuery('elasticsearch')
    s = Search(q, fields=['title', 'author'], start=100, size=50)
    results = conn.search(s)
    """

    def __init__(self, query=None, filter=None, fields=None, start=None,
                 size=None, highlight=None, sort=None, explain=False, facet=None, agg=None, rescore=None,
                 window_size=None, version=None, track_scores=None, script_fields=None, index_boost=None,
                 min_score=None, stats=None, bulk_read=None, partial_fields=None, _source=None, timeout=None):
        """
        fields: if is [], the _source is not returned
        """
        if not index_boost: index_boost = {}
        self.query = query
        self.filter = filter
        self.fields = fields
        self.start = start
        self.size = size
        self._highlight = highlight
        self.sort = sort or SortFactory()
        self.explain = explain
        self.facet = facet or FacetFactory()
        self.agg = agg or AggFactory()
        self.rescore = rescore
        self.window_size = window_size
        self.version = version
        self.track_scores = track_scores
        self._script_fields = script_fields
        self.index_boost = index_boost
        self.min_score = min_score
        self.stats = stats
        self.bulk_read = bulk_read
        self.partial_fields = partial_fields
        self._source = _source
        self.timeout = timeout

    def get_facet_factory(self):
        """
        Returns the facet factory
        """
        return self.facet

    def get_agg_factory(self):
        """
        Returns the agg factory
        """
        return self.agg

    def serialize(self):
        """Serialize the search to a structure as passed for a search body."""
        res = {}
        if self.query:
            if isinstance(self.query, dict):
                res["query"] = self.query
            elif isinstance(self.query, Query):
                res["query"] = self.query.serialize()
            else:
                raise InvalidQuery("Invalid query")
        if self.filter:
            res['filter'] = self.filter.serialize()
        if self.facet.facets:
            res['facets'] = self.facet.serialize()
        if self.agg.aggs:
            res['aggs'] = self.agg.serialize()
        if self.rescore:
            res['rescore'] = self.rescore.serialize()
        if self.window_size:
            res['window_size'] = self.window_size
        if self.fields is not None: #Deal properly with self.fields = []
            res['fields'] = self.fields
        if self.size is not None:
            res['size'] = self.size
        if self.start is not None:
            res['from'] = self.start
        if self._highlight:
            res['highlight'] = self._highlight.serialize()
        if self.sort:
            if isinstance(self.sort, SortFactory):
                sort = self.sort.serialize()
                if sort:
                    res['sort'] = sort
            else:
                res['sort'] = self.sort
        if self.explain:
            res['explain'] = self.explain
        if self.version:
            res['version'] = self.version
        if self.track_scores:
            res['track_scores'] = self.track_scores
        if self._script_fields:
            if isinstance(self.script_fields, ScriptFields):
                res['script_fields'] = self.script_fields.serialize()
            elif isinstance(self.script_fields, dict):
                res['script_fields'] = self.script_fields
            else:
                raise ScriptFieldsError("Parameter script_fields should of type ScriptFields or dict")
        if self.index_boost:
            res['indices_boost'] = self.index_boost
        if self.min_score:
            res['min_score'] = self.min_score
        if self.stats:
            res['stats'] = self.stats
        if self.partial_fields:
            res['partial_fields'] = self.partial_fields
        if self._source:
            res['_source'] = self._source
        if self.timeout:
            res['timeout'] = self.timeout
        return res

    @property
    def highlight(self):
        if self._highlight is None:
            self._highlight = HighLighter("<b>", "</b>")
        return self._highlight

    @property
    def script_fields(self):
        if self._script_fields is None:
            self._script_fields = ScriptFields()
        return self._script_fields

    def add_highlight(self, field, fragment_size=None,
                      number_of_fragments=None, fragment_offset=None, type=None):
        """Add a highlight field.

        The Search object will be returned, so calls to this can be chained.

        """
        if self._highlight is None:
            self._highlight = HighLighter("<b>", "</b>")
        self._highlight.add_field(field, fragment_size, number_of_fragments, fragment_offset, type=type)
        return self

    def add_index_boost(self, index, boost):
        """Add a boost on an index.

        The Search object will be returned, so calls to this can be chained.

        """
        if boost is None:
            if index in self.index_boost:
                del(self.index_boost[index])
        else:
            self.index_boost[index] = boost
        return self

    def __repr__(self):
        return str(self.serialize())


class Query(EqualityComparableUsingAttributeDictionary):
    """Base class for all queries."""

    def __init__(self, *args, **kwargs):
        if len(args) > 0 or len(kwargs) > 0:
            raise RuntimeWarning("No all parameters are processed by derivated query object")

    def search(self, **kwargs):
        """Return this query wrapped in a Search object.

        Any keyword arguments supplied to this call will be passed to the
        Search object.
        """
        return Search(query=self, **kwargs)

    def serialize(self):
        """Serialize the query to a structure using the query DSL."""
        return {self._internal_name: self._serialize()}

    def _serialize(self):
        raise NotImplementedError

    @property
    def _internal_name(self):
        raise NotImplementedError


class BoolQuery(Query):
    """A boolean combination of other queries.

    BoolQuery maps to Lucene **BooleanQuery**. It is built using one or more
    boolean clauses, each clause with a typed occurrence.  The occurrence types
    are:

    ================  ========================================================
     Occur             Description
    ================  ========================================================
    **must**          The clause (query) must appear in matching documents.
    **should**        The clause (query) should appear in the matching
                      document. A boolean query with no **must** clauses, one
                      or more **should** clauses must match a document. The
                      minimum number of should clauses to match can be set
                      using **minimum_number_should_match** parameter.
    **must_not**      The clause (query) must not appear in the matching
                      documents. Note that it is not possible to search on
                      documents that only consists of a **must_not** clauses.
    ================  ========================================================

    The bool query also supports **disable_coord** parameter (defaults to
    **false**).
    """

    _internal_name = "bool"

    def __init__(self, must=None, must_not=None, should=None, boost=None,
                 minimum_number_should_match=1, disable_coord=None, **kwargs):
        super(BoolQuery, self).__init__(**kwargs)
        self._must = []
        self._must_not = []
        self._should = []
        self.boost = boost
        self.minimum_number_should_match = minimum_number_should_match
        self.disable_coord = disable_coord
        if must:
            self.add_must(must)
        if must_not:
            self.add_must_not(must_not)
        if should:
            self.add_should(should)

    def add_must(self, queries):
        """Add a query to the "must" clause of the query.

        The Query object will be returned, so calls to this can be chained.
        """
        if isinstance(queries, list):
            self._must.extend(queries)
        else:
            self._must.append(queries)
        return self

    def add_should(self, queries):
        """Add a query to the "should" clause of the query.

        The Query object will be returned, so calls to this can be chained.
        """
        if isinstance(queries, list):
            self._should.extend(queries)
        else:
            self._should.append(queries)
        return self

    def add_must_not(self, queries):
        """Add a query to the "must_not" clause of the query.

        The Query object will be returned, so calls to this can be chained.
        """
        if isinstance(queries, list):
            self._must_not.extend(queries)
        else:
            self._must_not.append(queries)
        return self

    def is_empty(self):
        if self._must:
            return False
        if self._must_not:
            return False
        if self._should:
            return False
        return True

    def _serialize(self):
        filters = {}
        if self._must:
            filters['must'] = [f.serialize() for f in self._must]
        if self._must_not:
            filters['must_not'] = [f.serialize() for f in self._must_not]
        if self._should:
            filters['should'] = [f.serialize() for f in self._should]
            filters['minimum_number_should_match'] = self.minimum_number_should_match
        if self.boost:
            filters['boost'] = self.boost
        if self.disable_coord is not None:
            filters['disable_coord'] = self.disable_coord
        if not filters:
            raise RuntimeError("A least a filter must be declared")
        return filters


class ConstantScoreQuery(Query):
    """Returns a constant score for all documents matching a filter.

    Multiple filters may be supplied by passing a sequence or iterator as the
    filter parameter.  If multiple filters are supplied, documents must match
    all of them to be matched by this query.
    """

    _internal_name = "constant_score"

    def __init__(self, filter=None, boost=1.0, **kwargs):
        super(ConstantScoreQuery, self).__init__(**kwargs)
        self.filters = []
        self.queries = []
        self.boost = boost
        if filter:
            self.add(filter)

    def add(self, filter_or_query):
        """Add a filter, or a list of filters, to the query.

        If a sequence of filters is supplied, they are all added, and will be
        combined with an ANDFilter.

        If a sequence of queries is supplied, they are all added, and will be
        combined with an BooleanQuery(must) .

        """
        if isinstance(filter_or_query, Filter):
            if self.queries:
                raise QueryError("A Query is required")
            self.filters.append(filter_or_query)
        elif isinstance(filter_or_query, Query):
            if self.filters:
                raise QueryError("A Filter is required")
            self.queries.append(filter_or_query)
        else:
            for item in filter_or_query:
                self.add(item)
        return self

    def is_empty(self):
        """Returns True if the query is empty.

        """
        if self.filters:
            return False
        if self.queries:
            return False
        return True

    def _serialize(self):
        data = {}
        if self.boost != 1.0:
            data["boost"] = self.boost

        if self.filters:
            filters = {}
            if len(self.filters) == 1:
                filters.update(self.filters[0].serialize())
            else:
                filters.update(ANDFilter(self.filters).serialize())
            if not filters:
                raise QueryError("A filter is required")
            data['filter'] = filters
        else:
            queries = {}
            if len(self.queries) == 1:
                queries.update(self.queries[0].serialize())
            else:
                queries.update(BoolQuery(must=self.queries).serialize())
            data['query'] = queries

        return data


class HasQuery(Query):

    def __init__(self, type, query, _scope=None, score_mode=None, **kwargs):
        super(HasQuery, self).__init__(**kwargs)
        self.type = type
        self._scope = _scope
        self.score_mode = score_mode
        self.query = query

    def _serialize(self):
        data = {'type': self.type, 'query': self.query.serialize()}
        if self._scope is not None:
            data['_scope'] = self._scope
        if self.score_mode is not None:
            data['score_mode'] = self.score_mode
        return data


class HasChildQuery(HasQuery):

    _internal_name = "has_child"

    def __init__(self, *args, **kwargs):
        super(HasChildQuery, self).__init__(*args, **kwargs)
        if self.score_mode and self.score_mode not in ["max", "sum", "avg", "none"]:
            raise InvalidParameterQuery("Invalid value '%s' for score_mode" % self.score_mode)


class HasParentQuery(HasQuery):

    _internal_name = "has_parent"

    def __init__(self, *args, **kwargs):
        super(HasParentQuery, self).__init__(*args, **kwargs)
        if self.score_mode and self.score_mode not in ["score", "none"]:
            raise InvalidParameterQuery("Invalid value '%s' for score_mode" % self.score_mode)


class TopChildrenQuery(ConstantScoreQuery):

    _internal_name = "top_children"

    def __init__(self, type, score="max", factor=5, incremental_factor=2, **kwargs):
        super(TopChildrenQuery, self).__init__(**kwargs)
        self.type = type
        self.score = score
        self.factor = factor
        self.incremental_factor = incremental_factor

    def _serialize(self):
        if self.score not in ["max", "min", "avg", "sum"]:
            raise InvalidParameterQuery("Invalid value '%s' for score" % self.score)

        queries = {}
        if self.boost != 1.0:
            queries["boost"] = self.boost
        for f in self.queries:
            queries.update(f.serialize())
        return {
            'type': self.type,
            'query': queries,
            'score': self.score,
            'factor': self.factor,
            'incremental_factor': self.incremental_factor,
        }


class NestedQuery(Query):
    """
    Nested query allows to query nested objects / docs (see nested mapping).
    The query is executed against the nested objects / docs as if they were
    indexed as separate docs (they are, internally) and resulting in the root
    parent doc (or parent nested mapping).

    The query path points to the nested object path, and the query (or filter)
    includes the query that will run on the nested docs matching the direct
    path, and joining with the root parent docs.

    The score_mode allows to set how inner children matching affects scoring of
    parent. It defaults to avg, but can be total, max and none.

    Multi level nesting is automatically supported, and detected, resulting in
    an inner nested query to automatically match the relevant nesting level
    (and not root) if it exists within another nested query.
    """

    _internal_name = "nested"

    def __init__(self, path, query, _scope=None, score_mode="avg", **kwargs):
        super(NestedQuery, self).__init__(**kwargs)
        self.path = path
        self.score_mode = score_mode
        self.query = query
        self._scope = _scope

    def _serialize(self):
        if self.score_mode and self.score_mode not in ['avg', "total", "max"]:
            raise InvalidParameterQuery("Invalid score_mode: %s" % self.score_mode)
        data = {
            'path': self.path,
            'score_mode': self.score_mode,
            'query': self.query.serialize()}
        if self._scope is not None:
            data['_scope'] = self._scope
        return data


class DisMaxQuery(Query):

    _internal_name = "dis_max"

    def __init__(self, query=None, tie_breaker=0.0, boost=1.0, queries=None, **kwargs):
        super(DisMaxQuery, self).__init__(**kwargs)
        self.queries = queries or []
        self.tie_breaker = tie_breaker
        self.boost = boost
        if query:
            self.add(query)

    def add(self, query):
        if isinstance(query, list):
            self.queries.extend(query)
        else:
            self.queries.append(query)
        return self

    def _serialize(self):
        filters = {}
        if self.tie_breaker != 0.0:
            filters["tie_breaker"] = self.tie_breaker
        if self.boost != 1.0:
            filters["boost"] = self.boost
        filters["queries"] = [q.serialize() for q in self.queries]
        if not filters["queries"]:
            raise InvalidQuery("A least a query is required")
        return filters

#Removed in ES 1.x
# class FieldQuery(Query):
#
#     _internal_name = "field"
#
#     def __init__(self, fieldparameters=None, default_operator="OR", analyzer=None,
#                  allow_leading_wildcard=True, lowercase_expanded_terms=True,
#                  enable_position_increments=True, fuzzy_prefix_length=0,
#                  fuzzy_min_sim=0.5, phrase_slop=0, boost=1.0, use_dis_max=True,
#                  tie_breaker=0, **kwargs):
#         super(FieldQuery, self).__init__(**kwargs)
#         self.field_parameters = []
#         self.default_operator = default_operator
#         self.analyzer = analyzer
#         self.allow_leading_wildcard = allow_leading_wildcard
#         self.lowercase_expanded_terms = lowercase_expanded_terms
#         self.enable_position_increments = enable_position_increments
#         self.fuzzy_prefix_length = fuzzy_prefix_length
#         self.fuzzy_min_sim = fuzzy_min_sim
#         self.phrase_slop = phrase_slop
#         self.boost = boost
#         self.use_dis_max = use_dis_max
#         self.tie_breaker = tie_breaker
#         if fieldparameters:
#             if isinstance(fieldparameters, list):
#                 self.field_parameters.extend(fieldparameters)
#             else:
#                 self.field_parameters.append(fieldparameters)
#
#     def add(self, field, query, **kwargs):
#         fp = FieldParameter(field, query, **kwargs)
#         self.field_parameters.append(fp)
#
#     def _serialize(self):
#         result = {}
#         for f in self.field_parameters:
#             val, filters = f.serialize()
#             result[val] = filters
#         return result


class FilteredQuery(Query):
    """
    FilteredQuery allows for results to be filtered using the various filter classes.

    Example:

    t = TermFilter('name', 'john')
    q = FilteredQuery(MatchAllQuery(), t)
    results = conn.search(q)
    """

    _internal_name = "filtered"

    def __init__(self, query, filter, **kwargs):
        super(FilteredQuery, self).__init__(**kwargs)
        self.query = query
        self.filter = filter

    def _serialize(self):
        return {
            'query': self.query.serialize(),
            'filter': self.filter.serialize(),
        }


class BoostingQuery(Query):
    """
    The boosting query can be used to effectively demote results that match a given query. Unlike the "NOT"
    clause in bool query, this still selects documents that contain undesirable terms, but reduces their overall score.

    Example:

    t = TermQuery('name', 'john')
    q = BoostingQuery(MatchAllQuery(), t, negative_boost=0.2)
    results = conn.search(q)
    reference :https://github.com/elastic/elasticsearch/blob/148265bd164cd5a614cd020fb480d5974f523d81/core/src/main/java/org/elasticsearch/index/query/BoostingQueryParser.java
    """

    _internal_name = "boosting"

    def __init__(self, positive, negative, negative_boost=0.0, boost=1.0, **kwargs):
        super(BoostingQuery, self).__init__(**kwargs)
        self.positive = positive
        self.negative = negative
        self.negative_boost = negative_boost
        self.boost = boost

    def _serialize(self):
        return {
            'positive': self.positive.serialize(),
            'negative': self.negative.serialize(),
            'negative_boost': self.negative_boost,
            'boost': self.boost
        }

class MoreLikeThisFieldQuery(Query):

    _internal_name = "more_like_this_field"

    def __init__(self, field, like_text, percent_terms_to_match=0.3,
                 min_term_freq=2, max_query_terms=25, stop_words=None,
                 min_doc_freq=5, max_doc_freq=None, min_word_len=0, max_word_len=0,
                 boost_terms=1, boost=1.0, **kwargs):
        super(MoreLikeThisFieldQuery, self).__init__(**kwargs)
        self.field = field
        self.like_text = like_text
        self.percent_terms_to_match = percent_terms_to_match
        self.min_term_freq = min_term_freq
        self.max_query_terms = max_query_terms
        self.stop_words = stop_words or []
        self.min_doc_freq = min_doc_freq
        self.max_doc_freq = max_doc_freq
        self.min_word_len = min_word_len
        self.max_word_len = max_word_len
        self.boost_terms = boost_terms
        self.boost = boost

    def _serialize(self):
        filters = {'like_text': self.like_text}
        if self.percent_terms_to_match != 0.3:
            filters["percent_terms_to_match"] = self.percent_terms_to_match
        if self.min_term_freq != 2:
            filters["min_term_freq"] = self.min_term_freq
        if self.max_query_terms != 25:
            filters["max_query_terms"] = self.max_query_terms
        if self.stop_words:
            filters["stop_words"] = self.stop_words
        if self.min_doc_freq != 5:
            filters["min_doc_freq"] = self.min_doc_freq
        if self.max_doc_freq:
            filters["max_doc_freq"] = self.max_doc_freq
        if self.min_word_len:
            filters["min_word_len"] = self.min_word_len
        if self.max_word_len:
            filters["max_word_len"] = self.max_word_len
        if self.boost_terms:
            filters["boost_terms"] = self.boost_terms
        if self.boost != 1.0:
            filters["boost"] = self.boost
        return {self.field: filters}


class FuzzyLikeThisQuery(Query):

    _internal_name = "fuzzy_like_this"

    def __init__(self, fields, like_text, ignore_tf=False, max_query_terms=25,
                 min_similarity=0.5, prefix_length=0, boost=1.0, **kwargs):
        super(FuzzyLikeThisQuery, self).__init__(**kwargs)
        self.fields = fields
        self.like_text = like_text
        self.ignore_tf = ignore_tf
        self.max_query_terms = max_query_terms
        self.min_similarity = min_similarity
        self.prefix_length = prefix_length
        self.boost = boost

    def _serialize(self):
        filters = {'fields': self.fields, 'like_text': self.like_text}
        if self.ignore_tf:
            filters["ignore_tf"] = self.ignore_tf
        if self.max_query_terms != 25:
            filters["max_query_terms"] = self.max_query_terms
        if self.min_similarity != 0.5:
            filters["min_similarity"] = self.min_similarity
        if self.prefix_length:
            filters["prefix_length"] = self.prefix_length
        if self.boost != 1.0:
            filters["boost"] = self.boost
        return filters


class FuzzyQuery(Query):
    """
    A fuzzy based query that uses similarity based on Levenshtein (edit distance) algorithm.

    Note
        Warning: this query is not very scalable with its default prefix
        length of 0 - in this case, every term will be enumerated and cause an
        edit score calculation. Here is a simple example:
    """

    _internal_name = "fuzzy"

    def __init__(self, field, value, boost=None, min_similarity=0.5,
                 prefix_length=0, **kwargs):
        super(FuzzyQuery, self).__init__(**kwargs)
        self.field = field
        self.value = value
        self.boost = boost
        self.min_similarity = min_similarity
        self.prefix_length = prefix_length

    def _serialize(self):
        data = {
            'value': self.value,
            'min_similarity': self.min_similarity,
            'prefix_length': self.prefix_length,
            }
        if self.boost:
            data['boost'] = self.boost
        return {self.field: data}


class FuzzyLikeThisFieldQuery(Query):

    _internal_name = "fuzzy_like_this_field"

    def __init__(self, field, like_text, ignore_tf=False, max_query_terms=25,
                 boost=1.0, min_similarity=0.5, **kwargs):
        super(FuzzyLikeThisFieldQuery, self).__init__(**kwargs)
        self.field = field
        self.like_text = like_text
        self.ignore_tf = ignore_tf
        self.max_query_terms = max_query_terms
        self.min_similarity = min_similarity
        self.boost = boost

    def _serialize(self):
        filters = {'like_text': self.like_text}
        if self.ignore_tf:
            filters["ignore_tf"] = self.ignore_tf
        if self.max_query_terms != 25:
            filters["max_query_terms"] = self.max_query_terms
        if self.boost != 1.0:
            filters["boost"] = self.boost
        if self.min_similarity != 0.5:
            filters["min_similarity"] = self.min_similarity
        return {self.field: filters}


class MatchAllQuery(Query):
    """
    Query used to match all

    Example:

    q = MatchAllQuery()
    results = conn.search(q)
    """

    _internal_name = "match_all"

    def __init__(self, boost=None, **kwargs):
        super(MatchAllQuery, self).__init__(**kwargs)
        self.boost = boost

    def _serialize(self):
        filters = {}
        if self.boost:
            if isinstance(self.boost, (float, int)):
                filters['boost'] = self.boost
            else:
                filters['boost'] = float(self.boost)
        return filters


class MoreLikeThisQuery(Query):

    _internal_name = "more_like_this"

    def __init__(self, fields, like_text, percent_terms_to_match=0.3,
                 min_term_freq=2, max_query_terms=25, stop_words=None,
                 min_doc_freq=5, max_doc_freq=None, min_word_len=0, max_word_len=0,
                 boost_terms=1, boost=1.0, **kwargs):
        super(MoreLikeThisQuery, self).__init__(**kwargs)
        self.fields = fields
        self.like_text = like_text
        self.stop_words = stop_words or []
        self.percent_terms_to_match = percent_terms_to_match
        self.min_term_freq = min_term_freq
        self.max_query_terms = max_query_terms
        self.min_doc_freq = min_doc_freq
        self.max_doc_freq = max_doc_freq
        self.min_word_len = min_word_len
        self.max_word_len = max_word_len
        self.boost_terms = boost_terms
        self.boost = boost

    def _serialize(self):
        filters = {'fields': self.fields, 'like_text': self.like_text}
        if self.percent_terms_to_match != 0.3:
            filters["percent_terms_to_match"] = self.percent_terms_to_match
        if self.min_term_freq != 2:
            filters["min_term_freq"] = self.min_term_freq
        if self.max_query_terms != 25:
            filters["max_query_terms"] = self.max_query_terms
        if self.stop_words:
            filters["stop_words"] = self.stop_words
        if self.min_doc_freq != 5:
            filters["min_doc_freq"] = self.min_doc_freq
        if self.max_doc_freq:
            filters["max_doc_freq"] = self.max_doc_freq
        if self.min_word_len:
            filters["min_word_len"] = self.min_word_len
        if self.max_word_len:
            filters["max_word_len"] = self.max_word_len
        if self.boost_terms:
            filters["boost_terms"] = self.boost_terms
        if self.boost != 1.0:
            filters["boost"] = self.boost
        return filters


class FilterQuery(Query):

    _internal_name = "query"

    def __init__(self, filters=None, **kwargs):
        super(FilterQuery, self).__init__(**kwargs)
        self._filters = []
        if filters is not None:
            self.add(filters)

    def add(self, filterquery):
        if isinstance(filterquery, list):
            self._filters.extend(filterquery)
        else:
            self._filters.append(filterquery)

    def _serialize(self):
        filters = [f.serialize() for f in self._filters]
        if not filters:
            raise RuntimeError("A least one filter must be declared")
        return {"filter": filters}


class PrefixQuery(Query):

    _internal_name = "prefix"

    def __init__(self, field=None, prefix=None, boost=None, **kwargs):
        super(PrefixQuery, self).__init__(**kwargs)
        self._values = {}
        if field is not None and prefix is not None:
            self.add(field, prefix, boost)

    def add(self, field, prefix, boost=None):
        match = {'prefix': prefix}
        if boost:
            if isinstance(boost, (float, int)):
                match['boost'] = boost
            else:
                match['boost'] = float(boost)
        self._values[field] = match

    def _serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/prefix pair must be added")
        return self._values


class TermQuery(Query):
    """Match documents that have fields that contain a term (not analyzed).

    A boost may be supplied.

    Example:

    q = TermQuery('name', 'john')
    results = conn.search(q)

    With boost:

    q = TermQuery('name', 'john', boost=0.75)
    results = conn.search(q)
    """

    _internal_name = "term"

    def __init__(self, field=None, value=None, boost=None, **kwargs):
        super(TermQuery, self).__init__(**kwargs)
        self._values = {}
        if field is not None and value is not None:
            self.add(field, value, boost=boost)

    def add(self, field, value, boost=None):
        match = {'value': value}
        if boost:
            if isinstance(boost, (float, int)):
                match['boost'] = boost
            else:
                match['boost'] = float(boost)
            self._values[field] = match
        else:
            self._values[field] = value

    def _serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return self._values


class TermsQuery(TermQuery):

    _internal_name = "terms"

    def __init__(self, *args, **kwargs):
        minimum_match = kwargs.pop('minimum_match', 1)

        super(TermsQuery, self).__init__(*args, **kwargs)

        if minimum_match is not None:
            self._values['minimum_match'] = int(minimum_match)

    def add(self, field, value, minimum_match=1, boost=None):
        if not isinstance(value, list):
            raise InvalidParameterQuery("value %r must be valid list" % value)
        self._values[field] = value
        if minimum_match:
            if isinstance(minimum_match, int):
                self._values['minimum_match'] = minimum_match
            else:
                self._values['minimum_match'] = int(minimum_match)


class TextQuery(Query):
    """
    A new family of text queries that accept text, analyzes it, and constructs a query out of it.

    Examples:

    q = TextQuery('book_title', 'elasticsearch')
    results = conn.search(q)

    q = TextQuery('book_title', 'elasticsearch python', operator='and')
    results = conn.search(q)
    """

    _internal_name = "text"
    _valid_types = ['boolean', "phrase", "phrase_prefix"]
    _valid_operators = ['or', "and"]

    def __init__(self, field, text, type="boolean", slop=0, fuzziness=None,
                 prefix_length=0, max_expansions=2147483647, operator="or",
                 analyzer=None, boost=1.0, minimum_should_match=None, cutoff_frequency=None, **kwargs):
        super(TextQuery, self).__init__(**kwargs)
        self.queries = {}
        self.add_query(field, text, type, slop, fuzziness,
                       prefix_length, max_expansions,
                       operator, analyzer, boost, minimum_should_match,
                       cutoff_frequency=cutoff_frequency)

    def add_query(self, field, text, type="boolean", slop=0, fuzziness=None,
                  prefix_length=0, max_expansions=2147483647,
                  operator="or", analyzer=None, boost=1.0, minimum_should_match=None,
                  cutoff_frequency=None):
        if type not in self._valid_types:
            raise QueryError("Invalid value '%s' for type: allowed values are %s" % (type, self._valid_types))
        if operator not in self._valid_operators:
            raise QueryError(
                "Invalid value '%s' for operator: allowed values are %s" % (operator, self._valid_operators))

        query = {'type': type, 'query': text}
        if slop:
            query["slop"] = slop
        if fuzziness is not None:
            query["fuzziness"] = fuzziness
        if prefix_length:
            query["prefix_length"] = prefix_length
        if max_expansions != 2147483647:
            query["max_expansions"] = max_expansions
        if operator:
            query["operator"] = operator
        if boost != 1.0:
            query["boost"] = boost
        if analyzer:
            query["analyzer"] = analyzer
        if cutoff_frequency is not None:
            query["cutoff_frequency"] = cutoff_frequency
        if minimum_should_match:
            query["minimum_should_match"] = minimum_should_match
        self.queries[field] = query

    def _serialize(self):
        return self.queries

class MatchQuery(TextQuery):
    """
    Replaces TextQuery
    """
    _internal_name = "match"

class MultiMatchQuery(Query):
    """
    A query that matches same value on several fields with various types of matching and per field
    boosting.

    Examples:
    q = MultiMatch(['subject', 'message'], 'this is a test')

    Fore more, take a look at:
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/1.4/query-dsl-multi-match-query.html
    """
    _internal_name = "multi_match"
    _valid_types = ["best_fields", "most_fields", "cross_fields", "phrase", "phrase_prefix"]
    _valid_operators = ['or', "and"]

    def __init__(self, fields, text, type="best_fields", slop=0, fuzziness=None,
                 prefix_length=0, max_expansions=2147483647, rewrite=None,
                 operator="or", analyzer=None, use_dis_max=True, minimum_should_match=None,
                 boost = None, tie_breaker=None, **kwargs):
        super(MultiMatchQuery, self).__init__(**kwargs)

        if type not in self._valid_types:
            raise QueryError("Invalid value '%s' for type: allowed values are %s" % (type, self._valid_types))
        if operator not in self._valid_operators:
            raise QueryError(
                "Invalid value '%s' for operator: allowed values are %s" % (operator, self._valid_operators))
        if not fields:
            raise QueryError("At least one field must be defined for multi_match")
        if not isinstance(fields, list):
          fields = [fields]

        query = {'type': type, 'query': text, 'fields': fields, 'use_dis_max': use_dis_max}
        if slop:
            query["slop"] = slop
        if fuzziness is not None:
            query["fuzziness"] = fuzziness
        if prefix_length:
            query["prefix_length"] = prefix_length
        if max_expansions != 2147483647:
            query["max_expansions"] = max_expansions
        if operator:
            query["operator"] = operator
        if analyzer:
            query["analyzer"] = analyzer
        if rewrite:
            query["rewrite"] = rewrite
        if minimum_should_match:
            query['minimum_should_match'] = minimum_should_match
        if boost:
            query['boost'] = boost
        if tie_breaker:
            # 0.0 is a default, so we do not need to test against None
            query['tie_breaker'] = tie_breaker
        self.query = query

    def _serialize(self):
        return self.query


class RegexTermQuery(TermQuery):

    _internal_name = "regexp"


class QueryStringQuery(Query):
    """
    Query to match values on all fields for a given string

    Example:

    q = QueryStringQuery('elasticsearch')
    results = conn.search(q)
    """

    _internal_name = "query_string"

    def __init__(self, query, default_field=None, search_fields=None,
                 default_operator="OR", analyzer=None, allow_leading_wildcard=True,
                 lowercase_expanded_terms=True, enable_position_increments=True,
                 fuzzy_prefix_length=0, fuzzy_min_sim=0.5, phrase_slop=0,
                 boost=1.0, analyze_wildcard=False, use_dis_max=True,
                 tie_breaker=0, clean_text=False, minimum_should_match=None,
                 **kwargs):
        super(QueryStringQuery, self).__init__(**kwargs)
        self.clean_text = clean_text
        self.search_fields = search_fields or []
        self.query = query
        self.default_field = default_field
        self.default_operator = default_operator
        self.analyzer = analyzer
        self.allow_leading_wildcard = allow_leading_wildcard
        self.lowercase_expanded_terms = lowercase_expanded_terms
        self.enable_position_increments = enable_position_increments
        self.fuzzy_prefix_length = fuzzy_prefix_length
        self.fuzzy_min_sim = fuzzy_min_sim
        self.phrase_slop = phrase_slop
        self.boost = boost
        self.analyze_wildcard = analyze_wildcard
        self.use_dis_max = use_dis_max
        self.tie_breaker = tie_breaker
        self.minimum_should_match = minimum_should_match

    def _serialize(self):
        filters = {}
        if self.default_field:
            filters["default_field"] = self.default_field
            if not isinstance(self.default_field, six.string_types) and isinstance(self.default_field, list):
                if not self.use_dis_max:
                    filters["use_dis_max"] = self.use_dis_max
                if self.tie_breaker:
                    filters["tie_breaker"] = self.tie_breaker

        if self.default_operator != "OR":
            filters["default_operator"] = self.default_operator
        if self.analyzer:
            filters["analyzer"] = self.analyzer
        if not self.allow_leading_wildcard:
            filters["allow_leading_wildcard"] = self.allow_leading_wildcard
        if not self.lowercase_expanded_terms:
            filters["lowercase_expanded_terms"] = self.lowercase_expanded_terms
        if not self.enable_position_increments:
            filters["enable_position_increments"] = self.enable_position_increments
        if self.fuzzy_prefix_length:
            filters["fuzzy_prefix_length"] = self.fuzzy_prefix_length
        if self.fuzzy_min_sim != 0.5:
            filters["fuzzy_min_sim"] = self.fuzzy_min_sim
        if self.phrase_slop:
            filters["phrase_slop"] = self.phrase_slop
        if self.search_fields:
            if isinstance(self.search_fields, six.string_types):
                filters["fields"] = [self.search_fields]
            else:
                filters["fields"] = self.search_fields

            if len(filters["fields"]) > 1:
                if not self.use_dis_max:
                    filters["use_dis_max"] = self.use_dis_max
                if self.tie_breaker:
                    filters["tie_breaker"] = self.tie_breaker
        if self.boost != 1.0:
            filters["boost"] = self.boost
        if self.analyze_wildcard:
            filters["analyze_wildcard"] = self.analyze_wildcard
        if self.clean_text:
            query = clean_string(self.query)
            if not query:
                raise InvalidQuery("The query is empty")
            filters["query"] = query
        else:
            if not self.query.strip():
                raise InvalidQuery("The query is empty")
            filters["query"] = self.query
        if self.minimum_should_match:
          filters['minimum_should_match']=self.minimum_should_match
        return filters

class SimpleQueryStringQuery(Query):
    """
    A query that uses the SimpleQueryParser to parse its context. Unlike the regular query_string query,
    the simple_query_string query will never throw an exception, and discards invalid parts of the query.

    Example:

    q = SimpleQueryStringQuery('elasticsearch')
    results = conn.search(q)
    """

    _internal_name = "simple_query_string"

    def __init__(self, query, default_field=None, search_fields=None,
                 default_operator="OR", analyzer=None, allow_leading_wildcard=True,
                 lowercase_expanded_terms=True, enable_position_increments=True,
                 fuzzy_prefix_length=0, fuzzy_min_sim=0.5, phrase_slop=0,
                 boost=1.0, analyze_wildcard=False, use_dis_max=True,
                 tie_breaker=0, clean_text=False, minimum_should_match=None,
                 **kwargs):
        super(SimpleQueryStringQuery, self).__init__(**kwargs)
        self.clean_text = clean_text
        self.search_fields = search_fields or []
        self.query = query
        self.default_field = default_field
        self.default_operator = default_operator
        self.analyzer = analyzer
        self.allow_leading_wildcard = allow_leading_wildcard
        self.lowercase_expanded_terms = lowercase_expanded_terms
        self.enable_position_increments = enable_position_increments
        self.fuzzy_prefix_length = fuzzy_prefix_length
        self.fuzzy_min_sim = fuzzy_min_sim
        self.phrase_slop = phrase_slop
        self.boost = boost
        self.analyze_wildcard = analyze_wildcard
        self.use_dis_max = use_dis_max
        self.tie_breaker = tie_breaker
        self.minimum_should_match = minimum_should_match

    def _serialize(self):
        filters = {}
        if self.default_field:
            filters["default_field"] = self.default_field
            if not isinstance(self.default_field, six.string_types) and isinstance(self.default_field, list):
                if not self.use_dis_max:
                    filters["use_dis_max"] = self.use_dis_max
                if self.tie_breaker:
                    filters["tie_breaker"] = self.tie_breaker

        if self.default_operator != "OR":
            filters["default_operator"] = self.default_operator
        if self.analyzer:
            filters["analyzer"] = self.analyzer
        if not self.allow_leading_wildcard:
            filters["allow_leading_wildcard"] = self.allow_leading_wildcard
        if not self.lowercase_expanded_terms:
            filters["lowercase_expanded_terms"] = self.lowercase_expanded_terms
        if not self.enable_position_increments:
            filters["enable_position_increments"] = self.enable_position_increments
        if self.fuzzy_prefix_length:
            filters["fuzzy_prefix_length"] = self.fuzzy_prefix_length
        if self.fuzzy_min_sim != 0.5:
            filters["fuzzy_min_sim"] = self.fuzzy_min_sim
        if self.phrase_slop:
            filters["phrase_slop"] = self.phrase_slop
        if self.search_fields:
            if isinstance(self.search_fields, six.string_types):
                filters["fields"] = [self.search_fields]
            else:
                filters["fields"] = self.search_fields

            if len(filters["fields"]) > 1:
                if not self.use_dis_max:
                    filters["use_dis_max"] = self.use_dis_max
                if self.tie_breaker:
                    filters["tie_breaker"] = self.tie_breaker
        if self.boost != 1.0:
            filters["boost"] = self.boost
        if self.analyze_wildcard:
            filters["analyze_wildcard"] = self.analyze_wildcard
        if self.clean_text:
            query = clean_string(self.query)
            if not query:
                raise InvalidQuery("The query is empty")
            filters["query"] = query
        else:
            if not self.query.strip():
                raise InvalidQuery("The query is empty")
            filters["query"] = self.query
        if self.minimum_should_match:
          filters['minimum_should_match']=self.minimum_should_match
        return filters

class RangeQuery(Query):

    _internal_name = "range"

    def __init__(self, qrange=None, **kwargs):
        super(RangeQuery, self).__init__(**kwargs)
        self.ranges = []
        if qrange:
            self.add(qrange)

    def add(self, qrange):
        if isinstance(qrange, list):
            self.ranges.extend(qrange)
        elif isinstance(qrange, ESRange):
            self.ranges.append(qrange)

    def _serialize(self):
        if not self.ranges:
            raise RuntimeError("A least a range must be declared")
        return dict([r.serialize() for r in self.ranges])


class SpanFirstQuery(TermQuery):

    _internal_name = "span_first"

    def __init__(self, field=None, value=None, end=3, **kwargs):
        super(SpanFirstQuery, self).__init__(**kwargs)
        self._values = {}
        self.end = end
        if field is not None and value is not None:
            self.add(field, value)

    def _serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return {"match": {"span_first": self._values}, "end": self.end}


class SpanMultiQuery(Query):
    """
    This query allows you to wrap multi term queries (fuzzy, prefix, wildcard, range).

    The query element is either of type WildcardQuery, FuzzyQuery, PrefixQuery or RangeQuery.
    A boost can also be associated with the element query
    """

    _internal_name = "span_multi"

    def __init__(self, query, **kwargs):
        super(SpanMultiQuery, self).__init__(**kwargs)
        self.query = query

    def _validate(self):
        if not isinstance(self.query, (WildcardQuery, FuzzyQuery, PrefixQuery, RangeQuery)):
            raise RuntimeError("Invalid query:%r" % self.query)

    def _serialize(self):
        self._validate()
        return {'match': self.query.serialize()}


class SpanNearQuery(Query):
    """
    Matches spans which are near one another. One can specify _slop_,
    the maximum number of intervening unmatched positions, as well as
    whether matches are required to be in-order.

    The clauses element is a list of one or more other span type queries and
    the slop controls the maximum number of intervening unmatched positions
    permitted.
    """

    _internal_name = "span_near"

    def __init__(self, clauses=None, slop=1, in_order=None,
                 collect_payloads=None, **kwargs):
        super(SpanNearQuery, self).__init__(**kwargs)
        self.clauses = clauses or []
        self.slop = slop
        self.in_order = in_order
        self.collect_payloads = collect_payloads

    def _validate(self):
        for clause in self.clauses:
            if not is_a_spanquery(clause):
                raise RuntimeError("Invalid clause:%r" % clause)

    def _serialize(self):
        if not self.clauses or len(self.clauses) == 0:
            raise RuntimeError("A least a Span*Query must be added to clauses")
        data = {"slop": self.slop}
        if self.in_order is not None:
            data["in_order"] = self.in_order
        if self.collect_payloads is not None:
            data["collect_payloads"] = self.collect_payloads
        data['clauses'] = [clause.serialize() for clause in self.clauses]
        return data


class SpanNotQuery(Query):
    """
    Removes matches which overlap with another span query.

    The include and exclude clauses can be any span type query. The include
    clause is the span query whose matches are filtered, and the exclude
    clause is the span query whose matches must not overlap those returned.
    """

    _internal_name = "span_not"

    def __init__(self, include, exclude, **kwargs):
        super(SpanNotQuery, self).__init__(**kwargs)
        self.include = include
        self.exclude = exclude

    def _validate(self):
        if not is_a_spanquery(self.include):
            raise RuntimeError("Invalid clause:%r" % self.include)
        if not is_a_spanquery(self.exclude):
            raise RuntimeError("Invalid clause:%r" % self.exclude)

    def _serialize(self):
        self._validate()
        return {'include': self.include.serialize(),
                'exclude': self.exclude.serialize()}


def is_a_spanquery(obj):
    """
    Returns if the object is a span query
    """
    return isinstance(obj, (SpanTermQuery, SpanFirstQuery, SpanOrQuery, SpanMultiQuery))


class SpanOrQuery(Query):
    """
    Matches the union of its span clauses.

    The clauses element is a list of one or more other span type queries.
    """

    _internal_name = "span_or"

    def __init__(self, clauses=None, **kwargs):
        super(SpanOrQuery, self).__init__(**kwargs)
        self.clauses = clauses or []

    def _validate(self):
        for clause in self.clauses:
            if not is_a_spanquery(clause):
                raise RuntimeError("Invalid clause:%r" % clause)

    def _serialize(self):
        if not self.clauses or len(self.clauses) == 0:
            raise RuntimeError("A least a Span*Query must be added to clauses")
        clauses = [clause.serialize() for clause in self.clauses]
        return {"clauses": clauses}


class SpanTermQuery(TermQuery):

    _internal_name = "span_term"


class WildcardQuery(TermQuery):

    _internal_name = "wildcard"


class CustomScoreQuery(Query):

    _internal_name = "custom_score"

    def __init__(self, query=None, script=None, params=None, lang=None, **kwargs):
        super(CustomScoreQuery, self).__init__(**kwargs)
        self.query = query
        self.script = script
        self.lang = lang
        self.params = params or {}

    def add_param(self, name, value):
        self.params[name] = value

    def _serialize(self):
        if not self.query:
            raise RuntimeError("A least a query must be declared")
        if not self.script:
            raise RuntimeError("A script must be provided")
        data = {}
        data['query'] = self.query.serialize()
        data['script'] = self.script
        if self.params:
            data['params'] = self.params
        if self.lang:
            data['lang'] = self.lang
        return data


class IdsQuery(Query):

    _internal_name = "ids"

    def __init__(self, values, type=None, **kwargs):
        super(IdsQuery, self).__init__(**kwargs)
        self.type = type
        self.values = values

    def _serialize(self):
        data = {}
        if self.type is not None:
            data['type'] = self.type
        if isinstance(self.values, list):
            data['values'] = self.values
        else:
            data['values'] = [self.values]
        return data


class PercolatorQuery(Query):
    """A percolator query is used to determine which registered
    PercolatorDoc's match the document supplied.
    """

    def __init__(self, doc, query=None, **kwargs):
        """Constructor

        doc - the doc to match against, dict
        query - an additional query that can be used to filter the percolated
        queries used to match against.
        """
        super(PercolatorQuery, self).__init__(**kwargs)
        self.doc = doc
        self.query = query

    def serialize(self):
        """Serialize the query to a structure using the query DSL."""
        data = {'doc': self.doc}
        if isinstance(self.query, Query):
            data['query'] = self.query.serialize()
        return data

    def search(self, **kwargs):
        """Disable this as it is not allowed in percolator queries."""
        raise NotImplementedError()

class RescoreQuery(Query):
    """
    A rescore query is used to rescore top results from another query.
    """

    _internal_name = "rescore_query"

    def __init__(self, query, window_size=None, query_weight=None, rescore_query_weight=None, **kwargs):
        """
        Constructor
        """
        super(RescoreQuery, self).__init__(**kwargs)
        self.query = query
        self.window_size = window_size
        self.query_weight = query_weight
        self.rescore_query_weight = rescore_query_weight

    def serialize(self):
        """Serialize the query to a structure using the query DSL."""

        data = {self._internal_name: self.query.serialize()}
        if self.query_weight is not None:
            data['query_weight'] = self.query_weight
        if self.rescore_query_weight is not None:
            data['rescore_query_weight'] = self.rescore_query_weight

        return data


# class CustomFiltersScoreQuery(Query):
#
#     _internal_name = "custom_filters_score"
#
#     class ScoreMode(object):
#         FIRST = "first"
#         MIN = "min"
#         MAX = "max"
#         TOTAL = "total"
#         AVG = "avg"
#         MULTIPLY = "multiply"
#
#     class Filter(EqualityComparableUsingAttributeDictionary):
#
#         def __init__(self, filter_, boost=None, script=None):
#             if (boost is None) == (script is None):
#                 raise ValueError("Exactly one of boost and script must be specified")
#             self.filter_ = filter_
#             self.boost = boost
#             self.script = script
#
#         def serialize(self):
#             data = {'filter': self.filter_.serialize()}
#             if self.boost is not None:
#                 data['boost'] = self.boost
#             if self.script is not None:
#                 data['script'] = self.script
#             return data
#
#     def __init__(self, query, filters, score_mode=None, params=None, lang=None,
#                  **kwargs):
#         super(CustomFiltersScoreQuery, self).__init__(**kwargs)
#         self.query = query
#         self.filters = filters
#         self.score_mode = score_mode
#         self.params = params
#         self.lang = lang
#
#     def _serialize(self):
#         data = {'query': self.query.serialize(),
#                 'filters': [filter_.serialize() for filter_ in self.filters]}
#         if self.score_mode is not None:
#             data['score_mode'] = self.score_mode
#         if self.params is not None:
#             data['params'] = self.params
#         if self.lang is not None:
#             data['lang'] = self.lang
#         return data
#
#
# class CustomBoostFactorQuery(Query):
#     _internal_name = "custom_boost_factor"
#
#     def __init__(self, query, boost_factor, **kwargs):
#         super(CustomBoostFactorQuery, self).__init__(**kwargs)
#         self.boost_factor = boost_factor
#         self.query = query
#
#     def _serialize(self):
#         data = {'query': self.query.serialize()}
#
#         if isinstance(self.boost_factor, (float, int)):
#             data['boost_factor'] = self.boost_factor
#         else:
#             data['boost_factor'] = float(self.boost_factor)
#
#         return data


class FunctionScoreQuery(Query):
    """The functoin_score query exists since 0.90.4.
    It replaces CustomScoreQuery and some other.
    """

    class FunctionScoreFunction(EqualityComparableUsingAttributeDictionary):

        def serialize(self):
            """Serialize the function to a structure using the query DSL."""
            return {self._internal_name: self._serialize()}

    class DecayFunction(FunctionScoreFunction):

        def __init__(self, decay_function, field, origin=None, scale=None, decay=None, offset=None, filter=None):

            decay_functions = ["gauss", "exp", "linear"]
            if decay_function not in decay_functions:
                raise RuntimeError("The decay_function  %s is not allowed" % decay_function)

            self._internal_name = decay_function
            self.decay_function = decay_function
            self.field = field
            self.origin = origin
            self.scale = scale
            self.decay = decay
            self.filter = filter
            self.offset = offset

        def _serialize(self):
            field_data = {}
            if self.origin is not None:
                field_data['origin'] = self.origin
            if self.scale is not None:
                field_data['scale'] = self.scale
            if self.decay:
                field_data['decay'] = self.decay
            if self.offset:
                field_data['offset'] = self.offset

            return {self.field: field_data }

    class BoostFunction(FunctionScoreFunction):
        """Boost by a factor"""
        _internal_name = 'boost_factor'

        def __init__(self, boost_factor, filter=None):
            self.boost_factor = boost_factor
            self.filter = filter

        def serialize(self):
            data = {self._internal_name: self.boost_factor}
            if self.filter:
                data['filter'] = self.filter.serialize()
            return data

    class RandomFunction(FunctionScoreFunction):
        """Is a random boost based on a seed value"""
        _internal_name = 'random_score'

        def __init__(self, seed, filter=None):
            self.seed = seed
            self.filter = filter

        def _serialize(self):
            data = {'seed': self.seed}
            if self.filter:
                data['filter'] = self.filter.serialize()
            return data


    class ScriptScoreFunction(FunctionScoreFunction):
        """Scripting function with params and a script.
        Also possible to switch the script language"""
        _internal_name = "script_score"

        def __init__(self, script=None, params=None, lang=None, filter=None):

            self.filter = filter
            self.params = params
            self.lang = lang
            self.script = script

        def _serialize(self):
            data = {}
            if self.filter:
                data['filter'] = self.filter.serialize()
            if self.params is not None:
                data['params'] = self.params
            if self.script is not None:
                data['script'] = self.script
            if self.lang is not None:
                data['lang'] = self.lang
            return data

    class ScoreModes(object):
        """Some helper object to show the possibility of
        score_mode"""
        MULTIPLY = "multiply"
        SUM = "sum"
        AVG = "avg"
        FIRST = "first"
        MAX = "max"
        MIN = "min"

    class BoostModes(object):
        """Some helper object to show the possibility of
        boost_mode"""
        MULTIPLY = "multiply"
        REPLACE = "replace"
        SUM = "sum"
        AVG = "avg"
        MAX = "max"
        MIN = "min"

    class FieldValueFactor(FunctionScoreFunction):
        """ Boost by field value """
        _internal_name = "field_value_factor"

        def __init__(self, field, factor=None, modifier=None):
            self.field = field
            self.factor = factor
            self.modifier = modifier

        def _serialize(self):
            data = {
                'field': self.field
            }
            if self.factor:
                data['factor'] = self.factor
            if self.modifier:
                data['modifier'] = self.modifier
            return data

    _internal_name = "function_score"

    def __init__(
            self, functions=None, query=None, filter=None, max_boost=None, boost=None,
            score_mode=None, boost_mode=None, params=None):

        if not functions:
            functions = list()

        if max_boost:
            self.max_boost = int(max_boost)

        self.score_mode = score_mode
        self.boost_mode = boost_mode
        self.params = params
        self.functions = functions
        self.filter = filter
        self.query = query

    def _serialize(self):

        data = {}
        if self.params:
            data['params'] = dict(self.params)
        if self.functions:
            data['functions'] = []
            for function in self.functions:
                data['functions'].append(function.serialize())

        if self.score_mode:
            data['score_mode'] = self.score_mode

        if self.boost_mode:
            data['boost_mode'] = self.boost_mode

        if self.query:
            data['query'] = self.query.serialize()

        if self.filter:
            data['filter'] = self.filter.serialize()

        return data
