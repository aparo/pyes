#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

import logging

try:
    # For Python >= 2.6
    import json
except ImportError:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson as json

from pyes.es import ESJsonEncoder
from pyes.utils import clean_string
from pyes.facets import FacetFactory
from pyes.scriptfields import ScriptFields
from pyes.models import DotDict
from pyes.exceptions import InvalidQuery, InvalidParameterQuery, QueryError, ScriptFieldsError, InvalidParameter
log = logging.getLogger('pyes')

QUERY_PARAMETERS = {
                    "BoolQuery":{
                                 "must":{"type":list},
                                 "must_not":{"type":list},
                                 "should":{"type":list},
                                 "minimum_number_should_match":{"type":int, "default":1},
                                 "boost":{"type":float, "default":1.0},
                                 "disable_coord":{"type":bool, "default":False}, #check
                                 },
                    "ConstantScoreQuery":{
                                 "filter":{"type":list},
                                 "boost":{"type":float, "default":1.0},
                                 },
                    "CustomScoreQuery":{
                                 "query":{"type":dict},
                                 "script":{"type":basestring},
                                 "lang":{"type":basestring},
                                 "params":{"type":dict},
                                 },
                    "DisMaxQuery":{
                                 "tie_breaker":{"type":float, "default":0.0},
                                 "boost":{"type":float, "default":1.0},
                                 "queries":{"type":list},
                                 },
                    "FieldQuery":{
                                      "default_operator":{"type":basestring, "default":"OR", "values":["OR", "AND"]},
                                      "analyzer":{"type":basestring},
                                      "allow_leading_wildcard":{"type":bool, "default":True},
                                      "lowercase_expanded_terms":{"type":bool, "default":True},
                                      "enable_position_increments":{"type":bool, "default":True},
                                      "fuzzy_prefix_length":{"type":int, "default":0},
                                      "fuzzy_min_sim":{"type":float, "default":0.5},
                                      "phrase_slop":{"type":int, "default":0},
                                      "boost":{"type":float, "default":1.0},
                                      "use_dis_max":{"type":bool, "default":True},
                                      "tie_breaker":{"type":int, "default":0},
                                  },
                    "FilterQuery":{
                                    "filters":{"type":list},
                                },
                    "FilteredQuery":{
                                      "query":{"type":dict},
                                      "filter":{"type":dict},
                                     },
                    "FuzzyLikeThisFieldQuery":{
                                      "field":{"type":basestring},
                                      "like_text":{"type":basestring},
                                      "ignore_tf":{"type":bool, "default":False},
                                      "max_query_terms":{"type":int, "default":25},
                                      "boost":{"type":float, "default":1.0},
                                      "min_similarity":{"type":float, "default":0.5},
                                     },
                    "FuzzyLikeThisQuery":{
                                      "fields":{"type":list},
                                      "like_text":{"type":basestring},
                                      "ignore_tf":{"type":bool, "default":False},
                                      "prefix_length":{"type":int, "default":0},
                                      "boost":{"type":float, "default":1.0},
                                      "min_similarity":{"type":float, "default":0.5},
                                     },
                    "FuzzyQuery":{
                                  "field":{"type":basestring},
                                  "value":{"type":basestring},
                                  "boost":{"type":float, "default":1.0},
                                  "min_similarity":{"type":float, "default":0.5},
                                  "prefix_length":{"type":int, "default":0},
                                  },
                    "HasChildQuery":{
                                      "type":{"type":basestring},
                                      "query":{"type":dict},
                                      "_scope":{"type":basestring},
                                     },
                    "IdsQuery":{
                                      "type":{"type":basestring},
                                      "values":{"type":list},
                                      },
                    "MatchAllQuery":{
                                     "boost":{"type":float, "default":1.0},
                                     },
                    "MoreLikeThisQuery":{
                                      "like_text":{"type":basestring},
                                      "percent_terms_to_match":{"type":float, "default":0.3},
                                      "min_term_freq":{"type":int, "default":2},
                                      "max_query_terms":{"type":int, "default":25},
                                      "stop_words":{"type":list},
                                      "min_doc_freq":{"type":int, "default":5},
                                      "max_doc_freq":{"type":int},
                                      "min_word_len":{"type":int, "default":0},
                                      "max_word_len":{"type":int, "default":0},
                                      "boost_terms":{"type":int, "default":1},
                                      "boost":{"type":float, "default":1.0}
                                     },
                    "MoreLikeThisFieldField":{"field":{"type":float, "default":1.0}},
                    "MoreLikeThisFieldQueryField":{
                                      "like_text":{"type":basestring},
                                      "percent_terms_to_match":{"type":float, "default":0.3},
                                      "min_term_freq":{"type":int, "default":2},
                                      "max_query_terms":{"type":int, "default":25},
                                      "stop_words":{"type":list},
                                      "min_doc_freq":{"type":int, "default":5},
                                      "max_doc_freq":{"type":int},
                                      "min_word_len":{"type":int, "default":0},
                                      "max_word_len":{"type":int, "default":0},
                                      "boost_terms":{"type":int, "default":1},
                                      "boost":{"type":float, "default":1.0}
                                     },
                    "NestedQuery":{
                                   "path":{"type":basestring},
                                   "query":{"type":dict},
                                   "score_mode":{"type":basestring, "default":'avg', "values":["avg", "total", "max"]}},
                    "PercolatorQuery":{"doc":{"type":dict},
                                       "query":{"type":dict},
                                       },
                    "SpanNearQuery":{
                                      "clauses":{"type":list},
                                      "slop":{"type":int, "default":0},
                                      "in_order":{"type":bool, "default":True},
                                      "collect_payloads":{"type":bool, "default":True},
                                     },
                    "SpanOrQuery":{
                                      "clauses":{"type":list},
                                     },
                    "SpanNotQuery":{
                                      "include":{"type":list},
                                      "exclude":{"type":list},
                                     },
                    "StringQuery":{
                                      "query":{"type":basestring},
                                      "default_field":{"type":basestring},
                                      "search_fields":{"type":list},
                                      "default_operator":{"type":basestring, "default":"OR", "values":["OR", "AND"]},
                                      "analyzer":{"type":basestring},
                                      "allow_leading_wildcard":{"type":bool, "default":True},
                                      "lowercase_expanded_terms":{"type":bool, "default":True},
                                      "enable_position_increments":{"type":bool, "default":True},
                                      "fuzzy_prefix_length":{"type":int, "default":0},
                                      "fuzzy_min_sim":{"type":float, "default":0.5},
                                      "phrase_slop":{"type":int, "default":0},
                                      "boost":{"type":float, "default":1.0},
                                      "analyze_wildcard":{"type":bool, "default":False},
                                      "use_dis_max":{"type":bool, "default":True},
                                      "tie_breaker":{"type":int, "default":0},
                                  },
                    "TopChildrenQuery":{ #derived from ConstantScoreQuery
                                 "type":{"type":basestring},
                                 "filter":{"type":list},
                                 "boost":{"type":float, "default":1.0},
                                 "score":{"type":basestring, "default":'max', "values":["avg", "total", "max"]},
                              "factor":{"type":int, "default":5},
                              "incremental_factor":{"type":int, "default":2},
                                 },
                    #extra models
                    "FieldParameter":{
                                      "query":{},
                                      "default_operator":{"type":basestring, "default":"OR", "values":["OR", "AND"]},
                                      "analyzer":{},
                                      "allow_leading_wildcard":{"type":bool, "default":True},
                                      "lowercase_expanded_terms":{"type":bool, "default":True},
                                      "enable_position_increments":{"type":bool, "default":True},
                                      "fuzzy_prefix_length":{"type":int, "default":0},
                                      "fuzzy_min_sim":{"type":float, "default":0.5},
                                      "phrase_slop":{"type":int, "default":0},
                                      "boost":{"type":float, "default":1.0}}
                  }

class BaseQueryModel(DotDict):
    def __setattr__(self, key, value):
        if not self.__dict__.has_key('_' + self.__class__.__name__ + '__initialised'):
            return dict.__setattr__(self, key, value)
        elif self.__dict__.has_key(key):
            dict.__setattr__(self, key, value)
        else:
            #case value is None
            if value is None:
                try:
                    del self[value]
                except KeyError:
                    #key not present
                    pass
                return
            parameters = QUERY_PARAMETERS.get(self.__class__.__name__, {})
            if parameters:
                if key not in parameters:
                    raise InvalidParameter("Invalid parameter: % s" % key)
                parameter = parameters[key]
                #check type
                _type = parameter.get("type", None)
                if _type:
                    if not isinstance(value, _type):
                        raise InvalidParameter("Invalid parameter value '%s' for '%s' valid types are % s" % (value, key, _type))

                #check default and remove 
                if 'default' in parameter:
                    if value == parameter['default']:
                        try:
                            del self[key]
                        except KeyError:
                            #key not present
                            pass
                        return

                #check values 
                if 'values' in parameter and value not in parameter['values']:
                    raise InvalidParameter('Invalid value " % s" for parameter %s: valid values are:%s' % (value, key, parameter['values']))
                key, value = self._validate_field(key, value)
                if key:
                    self.__setitem__(key, value)
            else:
                self.__setitem__(key, value)

    def _validate_field(self, key, value):
        """
        If key is None, remove from fields
        """
        return key, value

    def serialize(self):
        """Serialize the query to a structure using the query DSL.

        """
        return {self.query_name:self}

class FieldParameter(BaseQueryModel):

    def __init__(self, field,
                 query,
                 default_operator="OR",
                    analyzer=None,
                    allow_leading_wildcard=True,
                    lowercase_expanded_terms=True,
                    enable_position_increments=True,
                    fuzzy_prefix_length=0,
                    fuzzy_min_sim=0.5,
                    phrase_slop=0,
                    boost=1.0):
        self.field = field
        self._valid_fields = {"query":[],
                            "default_operator":[],
                            "analyzer":[],
                            "allow_leading_wildcard":[],
                            "lowercase_expanded_terms":[],
                            "enable_position_increments":[],
                            "fuzzy_prefix_length":[],
                            "fuzzy_min_sim":[],
                            "phrase_slop":[],
                            "boost":[],
                            }
        self.__initialised = True

        self.query = query
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
        return {self.field:self}

class HighLighter(DotDict):
    """
    This object manage the highlighting
    """
    def __init__(self, pre_tags=None, post_tags=None, ** kwargs):
        """
        fields: if is [], the _source is not returned
        """
        self._valid_fields = {
                              "pre_tags":[],
                              "post_tags":[],
                              "fields":[],
                              "fragment_size":[],
                              "number_of_fragments":[],
                              "fragment_offset":[],
                            }
        self.__initialised = True
        if "fields" not in kwargs:
            kwargs["fields"] = {"_all" : {}}
        if pre_tags:
            kwargs["pre_tags"] = pre_tags
        if post_tags:
            kwargs["post_tags"] = post_tags

        self.update(kwargs)

    def __setattr__(self, key, value):
        if not self.__dict__.has_key('_HighLighter__initialised'):
            return dict.__setattr__(self, key, value)
        elif self.__dict__.has_key(key):
            dict.__setattr__(self, key, value)
        else:
            if key not in self._valid_fields:
                raise InvalidParameter("Invalid parameter:%s" % key)
            if self._valid_fields[key] and value not in self._valid_fields[key]:
                raise InvalidParameter('Invalid value "%s" for parameter %s' % (value, key))
            self.__setitem__(key, value)

    def add_field(self, name, fragment_size=150, number_of_fragments=3, fragment_offset=None):
        """
        Add a field to Highlinghter
        """
        data = DotDict()
        if fragment_size:
            data.fragment_size = fragment_size
        if number_of_fragments is not None:
            data.number_of_fragments = number_of_fragments
        if fragment_offset is not None:
            data.fragment_offset = fragment_offset
        self.fields[name] = data


class Search(DotDict):
    """A search to be performed.

    This contains a query, and has additional parameters which are used to
    control how the search works, what it should return, etc.

    """
    def __init__(self, query=None, **kwargs):
        """
        fields: if is [], the _source is not returned
        """
        self._valid_fields = {
                              "query":[],
                              "filter":[],
                              "fields":[],
                              "from":[],
                              "size":[],
                              "highlight":[],
                              "sort":[],
                              "explain":[],
                              "facet":[],
                              "version":[],
                              "track_scores":[],
                              "script_fields":[],
                              "index_boost":[],
                              "min_score":[],
                            }
        self.__initialised = True
        if query is not None:
            kwargs['query'] = query.serialize()
        self.update(kwargs)

    def __setattr__(self, key, value):
        if not self.__dict__.has_key('_Search__initialised'):
            return dict.__setattr__(self, key, value)
        elif self.__dict__.has_key(key):
            dict.__setattr__(self, key, value)
        else:
            if key == "start":
                key = "from"
            if key not in self._valid_fields:
                raise InvalidParameter("Invalid parameter:%s" % key)
            if self._valid_fields[key] and value not in self._valid_fields[key]:
                raise InvalidParameter('Invalid value "%s" for parameter %s' % (value, key))

            self.__setitem__(key, value)

    def get_facet_factory(self):
        """
        Returns the facet factory
        """
        if self.facet is None:
            self.facet = FacetFactory()
        return self.facet

#    def serialize(self):
#        """Serialize the search to a structure as passed for a search body.
#
#        """
#        res = {"query": self.query.serialize()}
#        if self.filter:
#            res['filter'] = self.filter.serialize()
#        if self.fields is not None:
#            res['fields'] = self.fields
#        if self.size is not None:
#            res['size'] = self.size
#        if self.start is not None:
#            res['from'] = self.start
##        if self.highlight:
##            res['highlight'] = self.highlight.serialize()
#        if self.sort:
#            res['sort'] = self.sort
#        if self.explain:
#            res['explain'] = self.explain
#        if self.version:
#            res['version'] = self.version
#        if self.track_scores:
#            res['track_scores'] = self.track_scores
##        if self.script_fields:
##            if isinstance(self.script_fields, ScriptFields):
##                res['script_fields'] = self.script_fields.serialize()
##            else:
##                raise ScriptFieldsError("Parameter script_fields should of type ScriptFields")
#        if self.index_boost:
#            res['indices_boost'] = self.index_boost
#        if self.min_score:
#            res['min_score'] = self.min_score
#        if self.facet.facets:
#            res.update(self.facet.q)
#        return res

    def add_highlight(self, field, fragment_size=None,
                      number_of_fragments=None, fragment_offset=None):
        """Add a highlight field.

        The Search object will be returned, so calls to this can be chained.

        """
        if self.highlight is None:
            self.highlight = HighLighter("<b>", "</b>")
        self.highlight.add_field(field, fragment_size, number_of_fragments, fragment_offset)
        return self

    def add_index_boost(self, index, boost):
        """Add a boost on an index.

        The Search object will be returned, so calls to this can be chained.

        """
        if boost is None:
            if self.index_boost.has_key(index):
                del(self.index_boost[index])
        else:
            self.index_boost[index] = boost
        return self

    def to_json(self):
        """Convert the search to JSON.

        The output of this is suitable for using as the request body for
        search.

        """
        return json.dumps(self, cls=ESJsonEncoder)


class Query(BaseQueryModel):
    """Base class for all queries.

    """

    def search(self, **kwargs):
        """Return this query wrapped in a Search object.

        Any keyword arguments supplied to this call will be passed to the
        Search object.

        """
        return Search(query=self.serialize(), **kwargs)

    def to_json(self):
        """Convert the query to JSON suitable for searching with.

        The output of this is suitable for using as the request body for
        search.

        """
        return json.dumps(dict(query=self.serialize()), cls=ESJsonEncoder)

    def to_query_json(self):
        """Convert the query to JSON using the query DSL.

        The output of this is suitable for using as the request body for count,
        delete_by_query and reindex.

        """
        return json.dumps(self.serialize(), cls=ESJsonEncoder)


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
    query_name = "bool"

    def __init__(self, must=None, must_not=None, should=None,
                 boost=None, minimum_number_should_match=1,
                 disable_coord=None):
        super(BoolQuery, self).__init__()

        self.__initialised = True

        self.boost = boost
        self.minimum_number_should_match = minimum_number_should_match
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
        if self.must is None:
            self.must = []
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            if isinstance(query, Query):
                self.must.append({query.query_name:query})
            else:
                self.must.append(query)
        return self

    def add_should(self, queries):
        """Add a query to the "should" clause of the query.

        The Query object will be returned, so calls to this can be chained.

        """
        if self.should is None:
            self.should = []
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            if isinstance(query, Query):
                self.should.append({query.query_name:query})
            else:
                self.should.append(query)
        return self

    def add_must_not(self, queries):
        """Add a query to the "must_not" clause of the query.

        The Query object will be returned, so calls to this can be chained.

        """
        if self.must_not is None:
            self.must_not = []
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            if isinstance(query, Query):
                self.must_not.append({query.query_name:query})
            else:
                self.must_not.append(query)
        return self

    def is_empty(self):
        if self.must:
            return False
        if self.must_not:
            return False
        if self.should:
            return False
        return True

class ConstantScoreQuery(Query):
    """Returns a constant score for all documents matching a filter.

    Multiple filters may be supplied by passing a sequence or iterator as the
    filter parameter.  If multiple filters are supplied, documents must match
    all of them to be matched by this query.

    """
    query_name = "constant_score"

    def __init__(self, filter, boost=1.0):
        super(ConstantScoreQuery, self).__init__()
        self.__initialised = True
        self.filter = []
        self.boost = boost
        self.add(filter)

    def add(self, filter):
        """Add a filter, or a list of filters, to the query.

        If a sequence of filters is supplied, they are all added, and will be
        combined with an ANDFilter.

        """
        from pyes.filters import Filter
        if isinstance(filter, Filter):
            self.filter.append(filter.serialize())
        else:
            for f in filter:
                self.filter.append(f.serialize())
        return self

    def is_empty(self):
        """Returns True if the query is empty.

        """
        if self.filters:
            return False
        return True

#    def serialize(self):
#        data = {}
#
#        if self.boost != 1.0:
#            data["boost"] = self.boost
#        filters = {}
#        if len(self.filters) == 1:
#            filters.update(self.filters[0].serialize())
#        else:
#            from pyes import ANDFilter
#            filters.update(ANDFilter(self.filters).serialize())
#        if not filters:
#            raise QueryError("A filter is required")
#        data['filter'] = filters
#        return {self.query_name:data}

class HasChildQuery(Query):
    query_name = "has_child"

    def __init__(self, type, query, _scope=None):
        self.__initialised = True
        super(HasChildQuery, self).__init__()
        self.type = type
        self.query = query
        self._scope = _scope

    def _validate_field(self, key, value):
        """
        If key is None, remove from fields
        """
        if key == "query":
            if isinstance(value, Query):
                return key, value.serialize()
        return key, value


class TopChildrenQuery(ConstantScoreQuery):
    query_name = "top_children"

    def __init__(self, type, score="max", factor=5, incremental_factor=2,
                 **kwargs):
        self.__initialised = True
        super(TopChildrenQuery, self).__init__(**kwargs)
        self.type = type
        self.score = score
        self.factor = factor
        self.incremental_factor = incremental_factor


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
    query_name = "nested"

    def __init__(self, path, query, score_mode="avg"):
        self.__initialized = True
        super(NestedQuery, self).__init__()
        self.path = path
        self.score_mode = score_mode
        self.query = query

class DisMaxQuery(Query):
    query_name = "dis_max"

    def __init__(self, queries, tie_breaker=0.0, boost=1.0):
        self._validate_fields = {"query":[],
                                 "tie_breaker":[],
                                 "boost":[],
                                 "queries":[],
                                 }
        self.__initialised = True
        super(DisMaxQuery, self).__init__()
        self.queries = []
        self.tie_breaker = tie_breaker
        self.boost = boost
        if queries:
            self.add(queries)

    def add(self, query):
        if not isinstance(query, list):
            query = [query]
        for q in query:
            if isinstance(q, Query):
                self.queries.append(q.serialize())
            else:
                self.queries.append(q)
        return self

class FieldQuery(Query):
    query_name = "field"

    def __init__(self, fieldparameters, default_operator="OR",
                analyzer=None,
                allow_leading_wildcard=True,
                lowercase_expanded_terms=True,
                enable_position_increments=True,
                fuzzy_prefix_length=0,
                fuzzy_min_sim=0.5,
                phrase_slop=0,
                boost=1.0,
                use_dis_max=True,
                tie_breaker=0):
        super(FieldQuery, self).__init__()
        self.__initialised = True

        self.default_operator = default_operator
        self.analyzer = analyzer
        self.allow_leading_wildcard = allow_leading_wildcard
        self.lowercase_expanded_terms = lowercase_expanded_terms
        self.enable_position_increments = enable_position_increments
        self.fuzzy_prefix_length = fuzzy_prefix_length
        self.fuzzy_min_sim = fuzzy_min_sim
        self.phrase_slop = phrase_slop
        self.boost = boost
        self.use_dis_max = use_dis_max
        self.tie_breaker = tie_breaker
        if fieldparameters:
            if isinstance(fieldparameters, list):
                for fp in fieldparameters:
                    self[fp.field] = fp
            else:
                self[fieldparameters.field] = fieldparameters

    def add(self, field, query, **kwargs):
        fp = FieldParameter(field, query, **kwargs)
        self[fp.field] = fp

class FilteredQuery(Query):
    query_name = "filtered"

    def __init__(self, query, filter):
        super(FilteredQuery, self).__init__()
        self.__initialised = True
        self.query = query
        self.filter = filter

    def _validate_field(self, key, value):
        if key in ['query', 'filter']:
            return key, value.serialize()
        return key, value

class MoreLikeThisFieldQueryField(BaseQueryModel):
    def __init__(self, name,
                    like_text,
                     percent_terms_to_match=0.3,
                    min_term_freq=2,
                    max_query_terms=25,
                    stop_words=None,
                    min_doc_freq=5,
                    max_doc_freq=None,
                    min_word_len=0,
                    max_word_len=0,
                    boost_terms=1,
                    boost=1.0):
        self.name = name
        self.__initialised = True
        super(MoreLikeThisFieldQueryField, self).__init__()

class MoreLikeThisFieldQuery(Query):
    query_name = "more_like_this_field"

    def __init__(self, field):
        self.__initialised = True
        super(MoreLikeThisFieldQuery, self).__init__()
        self[field.name] = field

class FuzzyLikeThisQuery(Query):
    query_name = "fuzzy_like_this"

    def __init__(self, fields, like_text,
                     ignore_tf=False, max_query_terms=25,
                     min_similarity=0.5, prefix_length=0,
                     boost=1.0):
        super(FuzzyLikeThisQuery, self).__init__()
        self.__initialised = True
        self.fields = fields
        self.like_text = like_text
        self.ignore_tf = ignore_tf
        self.max_query_terms = max_query_terms
        self.min_similarity = min_similarity
        self.prefix_length = prefix_length
        self.boost = boost

class FuzzyQuery(Query):
    """
    A fuzzy based query that uses similarity based on Levenshtein (edit distance) algorithm.

    Note
        Warning: this query is not very scalable with its default prefix length of 0 - in this case, every term will be enumerated and cause an edit score calculation. Here is a simple example:

    """
    query_name = "fuzzy"

    def __init__(self, field, value, boost=None,
            min_similarity=0.5, prefix_length=0):
        self.__initialised = True
        super(FuzzyQuery, self).__init__()
        self.field = field
        self.value = value
        self.boost = boost
        self.min_similarity = min_similarity
        self.prefix_length = prefix_length


class FuzzyLikeThisFieldQuery(Query):
    query_name = "fuzzy_like_this_field"

    def __init__(self, field, like_text,
                     ignore_tf=False, max_query_terms=25,
                     boost=None, min_similarity=0.5):
        self.__initialised = True
        super(FuzzyLikeThisFieldQuery, self).__init__()
        self.field = field
        self.like_text = like_text
        self.ignore_tf = ignore_tf
        self.max_query_terms = max_query_terms
        self.min_similarity = min_similarity
        self.boost = boost

class MatchAllQuery(Query):
    query_name = "match_all"
    def __init__(self, boost=1.0):
        super(MatchAllQuery, self).__init__()
        self.__initialised = True
        self.boost = boost

class MoreLikeThisQuery(Query):
    query_name = "more_like_this"

    def __init__(self, fields, like_text,
                     percent_terms_to_match=0.3,
                    min_term_freq=2,
                    max_query_terms=25,
                    stop_words=None,
                    min_doc_freq=5,
                    max_doc_freq=None,
                    min_word_len=0,
                    max_word_len=0,
                    boost_terms=1,
                    boost=None):
        super(MatchAllQuery, self).__init__()
        self.__initialised = True
        super(MoreLikeThisQuery, self).__init__()
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

class FilterQuery(Query):
    query_name = "query"

    def __init__(self, filters):
        self.__initialised = True
        super(FilterQuery, self).__init__()

        self.filters = []
        self.add(filters)

    def add(self, filterquery):
        if isinstance(filterquery, list):
            for f in filterquery:
                self.filters.append(f.serialize())
        else:
            self.filters.append(filterquery.serialize())


class PrefixQuery(Query):
    query_name = "prefix"
    def __init__(self, field, prefix, boost=None):
        super(PrefixQuery, self).__init__()
        self.__initialised = True

        if field is not None and prefix is not None:
            self.add(field, prefix, boost)

    def add(self, field, prefix, boost=None):
        match = DotDict({'prefix':prefix})
        if boost:
            if isinstance(boost, (float, int)):
                match['boost'] = boost
            else:
                match['boost'] = float(boost)
        self[field] = match

class TermQuery(Query):
    """Match documents that have fields that contain a term (not analyzed).

    A boost may be supplied.

    """
    query_name = "term"

    def __init__(self, field=None, value=None, boost=None, **kwargs):
        super(TermQuery, self).__init__(**kwargs)
        self.__initialised = True
        if field is not None and value is not None:
            self.add(field, value, boost)

    def add(self, field, value, boost=None):
        match = DotDict({'value':value})
        if boost:
            if isinstance(boost, (float, int)):
                match['boost'] = boost
            else:
                match['boost'] = float(boost)
            self[field] = match
            return

        self[field] = value


class TermsQuery(TermQuery):
    query_name = "terms"

    def __init__(self, *args, **kwargs):
        self.__initialised = True
        super(TermsQuery, self).__init__(*args, **kwargs)

    def add(self, field, value, minimum_match=1):
        if not isinstance(value, list):
            raise InvalidParameterQuery("value %r must be valid list" % value)
        self[field] = value
        if minimum_match:
            if isinstance(minimum_match, int):
                self['minimum_match'] = minimum_match
            else:
                self['minimum_match'] = int(minimum_match)

class TextQuery(Query):
    """
    A new family of text queries that accept text, analyzes it, and constructs a query out of it.
    """
    query_name = "text"
    _valid_types = ['boolean', "phrase", "phrase_prefix"]
    _valid_operators = ['or', "and"]

    def __init__(self, field, text, type="boolean", slop=0, fuzziness=None,
                 prefix_length=0, max_expansions=2147483647,
                 operator="or", analyzer=None, **kwargs):
        self.__initialised = True
        super(TextQuery, self).__init__(**kwargs)
        self.add_query(field, text, type, slop, fuzziness,
                 prefix_length, max_expansions,
                 operator, analyzer)

    def add_query(self, field, text, type="boolean", slop=0, fuzziness=None,
                 prefix_length=0, max_expansions=2147483647,
                 operator="or", analyzer=None):

        if type not in self._valid_types:
            raise QueryError("Invalid value '%s' for type: allowed values are %s" % (type, self._valid_types))
        if operator not in self._valid_operators:
            raise QueryError("Invalid value '%s' for operator: allowed values are %s" % (operator, self._valid_operators))

        query = DotDict({'type':type, 'query':text})
        if slop != 0:
            query.slop = slop
        if fuzziness is not None:
            query.fuzziness = fuzziness
        if slop != 0:
            query.prefix_length = prefix_length
        if max_expansions != 2147483647:
            query.max_expansions = max_expansions

        self[field] = query

class RegexTermQuery(TermQuery):
    query_name = "regex_term"

    def __init__(self, *args, **kwargs):
        super(RegexTermQuery, self).__init__(*args, **kwargs)

class StringQuery(Query):
    query_name = "query_string"

    def __init__(self, query, default_field=None,
                 search_fields=None,
                default_operator="OR",
                analyzer=None,
                allow_leading_wildcard=True,
                lowercase_expanded_terms=True,
                enable_position_increments=True,
                fuzzy_prefix_length=0,
                fuzzy_min_sim=0.5,
                phrase_slop=0,
                boost=1.0,
                analyze_wildcard=False,
                use_dis_max=True,
                tie_breaker=0):
        self.__initialised = True
        super(StringQuery, self).__init__()
        self.search_fields = search_fields
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


#    def serialize(self):
#        filters = {}
#        if self.default_field:
#            filters["default_field"] = self.default_field
#            if not isinstance(self.default_field, (str, unicode)) and isinstance(self.default_field, list):
#                if not self.use_dis_max:
#                    filters["use_dis_max"] = self.use_dis_max
#                if self.tie_breaker != 0:
#                    filters["tie_breaker"] = self.tie_breaker
#
#        if self.default_operator != "OR":
#            filters["default_operator"] = self.default_operator
#        if self.analyzer:
#            filters["analyzer"] = self.analyzer
#        if not self.allow_leading_wildcard:
#            filters["allow_leading_wildcard"] = self.allow_leading_wildcard
#        if not self.lowercase_expanded_terms:
#            filters["lowercase_expanded_terms"] = self.lowercase_expanded_terms
#        if not self.enable_position_increments:
#            filters["enable_position_increments"] = self.enable_position_increments
#        if self.fuzzy_prefix_length:
#            filters["fuzzy_prefix_length"] = self.fuzzy_prefix_length
#        if self.fuzzy_min_sim != 0.5:
#            filters["fuzzy_min_sim"] = self.fuzzy_min_sim
#        if self.phrase_slop:
#            filters["phrase_slop"] = self.phrase_slop
#        if self.search_fields:
#            if isinstance(self.search_fields, (str, unicode)):
#                filters["fields"] = [self.search_fields]
#            else:
#                filters["fields"] = self.search_fields
#
#            if len(filters["fields"]) > 1:
#                if not self.use_dis_max:
#                    filters["use_dis_max"] = self.use_dis_max
#                if self.tie_breaker != 0:
#                    filters["tie_breaker"] = self.tie_breaker
#        if self.boost != 1.0:
#            filters["boost"] = self.boost
#        if self.analyze_wildcard:
#            filters["analyze_wildcard"] = self.analyze_wildcard
#        if self.clean_text:
#            query = clean_string(self.query)
#            if not query:
#                raise InvalidQuery("The query is empty")
#            filters["query"] = query
#        else:
#            if not self.query.strip():
#                raise InvalidQuery("The query is empty")
#            filters["query"] = self.query
#        return {self.query_name:filters}

class ESRange(BaseQueryModel):
    def __init__(self, field, **kwargs):
        """
        type can be "gt", "gte", "lt", "lte"
        
        """

        self.field = field
        self.__initialised = True
        self.update(kwargs)

    def serealize(self):
        return {self.field:self}

class ESRangeOp(ESRange):
    def __init__(self, field, op, value, boost=None):
        from_value = to_value = include_lower = include_upper = None
        if op == "gt":
            from_value = value
            include_lower = False
        elif op == "gte":
            from_value = value
            include_lower = True
        if op == "lt":
            to_value = value
            include_upper = False
        elif op == "lte":
            to_value = value
            include_upper = True
        super(ESRangeOp, self).__init__(field, from_value, to_value,
                include_lower, include_upper, boost)

class RangeQuery(Query):

    def __init__(self, _range):
        self.__initialised = True
        super(RangeQuery, self).__init__()

        self.range = []
        self.add(_range)

    def add(self, qrange):
        if isinstance(qrange, list):
            for _range in qrange:
                self.range.append(_range.serealize())
        elif isinstance(qrange, ESRange):
            self.range.append(qrange.serealize())

#    def serialize(self):
#        if not self.ranges:
#            raise RuntimeError("A least a range must be declared")
#        filters = dict([r.serialize() for r in self.ranges])
#        return {"range":filters}

class SpanFirstQuery(Query):
    query_name = "span_first"

    def __init__(self, field, value, end=3, **kwargs):
        super(SpanFirstQuery, self).__init__(**kwargs)
        #TODO: fix
        self.end = end
        self.add(field, value)

    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return {self.query_name:{"match":{"span_first":self._values},
                                     "end":self.end}}

class SpanNearQuery(Query):
    """
    Matches spans which are near one another. One can specify _slop_,
    the maximum number of intervening unmatched positions, as well as
    whether matches are required to be in-order.

    The clauses element is a list of one or more other span type queries and
    the slop controls the maximum number of intervening unmatched positions
    permitted.
    """
    query_name = "span_near"

    def __init__(self, clauses, slop=None,
                 in_order=None,
                 collect_payloads=None):
        super(SpanNearQuery, self).__init__()
        self.__initialised = True
        self.clauses = clauses
        self.slop = slop
        self.in_order = in_order
        self.collect_payloads = collect_payloads

    def _validate(self):
        for clause in self.clauses:
            if not is_a_spanquery(clause):
                raise RuntimeError("Invalid clause:%r" % clause)

class SpanNotQuery(Query):
    """
    Removes matches which overlap with another span query.

    The include and exclude clauses can be any span type query. The include
    clause is the span query whose matches are filtered, and the exclude
    clause is the span query whose matches must not overlap those returned.
    """
    query_name = "span_not"

    def __init__(self, include, exclude):
        super(SpanNotQuery, self).__init__()
        self.__initialised = True
        self.include = include
        self.exclude = exclude

    def _validate(self):
        if not is_a_spanquery(self.include):
            raise RuntimeError("Invalid clause:%r" % self.include)
        if not is_a_spanquery(self.exclude):
            raise RuntimeError("Invalid clause:%r" % self.exclude)

def is_a_spanquery(obj):
    """
    Returns if the object is a span query
    """
    return isinstance(obj, (SpanTermQuery, SpanFirstQuery, SpanOrQuery))

class SpanOrQuery(Query):
    """
    Matches the union of its span clauses.

    The clauses element is a list of one or more other span type queries.
    """
    query_name = "span_or"

    def __init__(self, clauses):
        super(SpanOrQuery, self).__init__()
        self.__initialised = True
        self.clauses = clauses

    def _validate(self):
        for clause in self.clauses:
            if not is_a_spanquery(clause):
                raise RuntimeError("Invalid clause:%r" % clause)

class SpanTermQuery(TermQuery):
    query_name = "span_term"

    def __init__(self, *args, **kwargs):
        self.__initialised = True
        super(SpanTermQuery, self).__init__(*args, **kwargs)

class WildcardQuery(TermQuery):
    query_name = "wildcard"

    def __init__(self, *args, **kwargs):
        self.__initialised = True
        super(WildcardQuery, self).__init__(*args, **kwargs)

class CustomScoreQuery(Query):
    query_name = "custom_score"

    def __init__(self, query, script, params=None, lang=None):
        super(CustomScoreQuery, self).__init__()
        self.__initialised = True
        self.query = query
        self.script = script
        self.lang = lang
        self.params = params

    def add_param(self, name, value):
        """
        Add a parameter
        """
        if self.params is None:
            self.params = {}
        self.params[name] = value

    def _validate_field(self, key, value):
        """
        If key is None, remove from fields
        """
        if key == "query":
            if isinstance(value, Query):
                return key, value.serialize()
        return key, value
class IdsQuery(Query):
    query_name = "ids"
    def __init__(self, type, values):
        super(IdsQuery, self).__init__()
        self.__initialised = True
        self.type = type
        if isinstance(values, basestring):
            values = [values]
        self.values = values


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
        self.__initialised = True
        self.doc = doc
        self.query = query

