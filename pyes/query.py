#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

import logging

try:
    import json
except ImportError:
    # For Python <= 2.5
    import simplejson as json

from es import ESJsonEncoder
from utils import clean_string, ESRange
from facets import FacetFactory
from highlight import HighLighter
from pyes.exceptions import InvalidQuery, InvalidParameterQuery, QueryError
log = logging.getLogger('pyes')

class FieldParameter:

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


#--- Query
class Query(object):
    def __init__(self,
                 fields=None,
                 start=None,
                 size=None,
                 highlight=None,
                 sort=None,
                 explain=False,
                 facet=None,
                 index_boost={}):
        """
        fields: if is [], the _soruce is not returned
        """
        self.fields = fields
        self.start = start
        self.size = size
        self.highlight = highlight
        self.sort = sort
        self.explain = explain
        self.facet = facet or FacetFactory()
        self.index_boost = index_boost

    def get_facet_factory(self):
        """
        Returns the facet factory
        """
        return self.facet

    @property
    def q(self):
        res = {"query":self.serialize()}
        if self.fields is not None:
            res['fields'] = self.fields
        if self.size is not None:
            res['size'] = self.size
        if self.start is not None:
            res['from'] = self.start
        if self.highlight:
            res['highlight'] = self.highlight.serialize()
        if self.sort:
            res['sort'] = self.sort
        if self.explain:
            res['explain'] = self.explain
        if self.index_boost:
            res['indices_boost'] = self.index_boost
        if self.facet.facets:
            res.update(self.facet.q)
        return res

    def add_highlight(self, field, fragment_size=None, number_of_fragments=None):
        """
        Add an highlight field
        """
        if self.highlight is None:
            self.highlight = HighLighter("<b>", "</b>")
        self.highlight.add_field(field, fragment_size, number_of_fragments)

    def add_index_boost(self, index, boost):
        """
        Add a boost on an index
        """
        if boost is None:
            if self.index_boost.has_key(index):
                del(self.index_boost[index])
        else:
            self.index_boost[index] = boost

    def count(self):
        # FIXME - document this or remove it - I don't think it does anything
        # sensible.
        return self.serialize()

    def __repr__(self):
        return str(self.q)

    def to_json(self, inner=False):
        """
        Inner return only the inner query. Useful for delete_by_query and reindex.
        """
        q = self.q
        if inner:
            q = q['query']
        return json.dumps(q, cls=ESJsonEncoder)



class BoolQuery(Query):
    """
    A query that matches documents matching boolean combinations of other 
    queries. The bool query maps to Lucene **BooleanQuery**. It is built 
    using one or more boolean clauses, each clause with a typed occurrence. 
    The occurrence types are:
    
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

    def __init__(self, must=None, must_not=None, should=None,
                 boost=None, minimum_number_should_match=1,
                 disable_coord=None,
                 **kwargs):
        super(BoolQuery, self).__init__(**kwargs)

        self._must = []
        self._must_not = []
        self._should = []
        self.boost = boost
        self.minimum_number_should_match = minimum_number_should_match
        self.disable_coord = None

        if must:
            self.add_must(must)

        if must_not:
            self.add_must_not(must_not)

        if should:
            self.add_should(should)

    def add_must(self, queries):
        if isinstance(queries, list):
            self._must.extend(queries)
        else:
            self._must.append(queries)

    def add_must_not(self, queries):
        if isinstance(queries, list):
            self._must_not.extend(queries)
        else:
            self._must_not.append(queries)

    def add_should(self, queries):
        if isinstance(queries, list):
            self._should.extend(queries)
        else:
            self._should.append(queries)

    def is_empty(self):
        if self._must:
            return False
        if self._must_not:
            return False
        if self._should:
            return False
        return True


    def serialize(self):
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
        return {"bool":filters}



class ConstantScoreQuery(Query):
    _internal_name = "constant_score"

    def __init__(self, filter=None, boost=1.0, **kwargs):
        super(ConstantScoreQuery, self).__init__(**kwargs)
        self.filters = []
        self.boost = boost
        if filter:
            self.add(filter)

    def add(self, filter):
        if isinstance(filter, list):
            self.filters.extend(filter)
        else:

            self.filters.append(filter)

    def is_empty(self):
        """Returns if the query is empty"""
        if self.filters:
            return False
        return True

    def serialize(self):
        data = {}

        if self.boost != 1.0:
            data["boost"] = self.boost
        filters = {}
        if len(self.filters) == 1:
            filters.update(self.filters[0].serialize())
        else:
            from pyes import ANDFilter
            filters.update(ANDFilter(self.filters).serialize())
        if not filters:
            raise QueryError("A filter is required")
        data['filter'] = filters
        return {self._internal_name:data}

class HasChildQuery(ConstantScoreQuery):
    _internal_name = "has_child"

    def __init__(self, type, **kwargs):
        super(HasChildQuery, self).__init__(**kwargs)
        self.type = type

    def serialize(self):
        filters = {}

        if self.boost != 1.0:
            filters["boost"] = self.boost

        for f in self.filters:
            filters.update(f.serialize())

        return {self._internal_name:{
                                     'type':self.type,
                                     'query':filters}}

class TopChildrenQuery(ConstantScoreQuery):
    _internal_name = "top_children"

    def __init__(self, type, score="max", factor=5, incremental_factor=2,
                 **kwargs):
        super(TopChildrenQuery, self).__init__(**kwargs)
        self.type = type
        self.score = score
        self.factor = factor
        self.incremental_factor = incremental_factor

    def serialize(self):
        filters = {}

        if self.boost != 1.0:
            filters["boost"] = self.boost

        for f in self.filters:
            filters.update(f.serialize())

        if self.score not in ["max", "min", "avg"]:
            raise InvalidParameterQuery("Invalid value '%s' for score" % self.score)

        return {self._internal_name:{
                                     'type':self.type,
                                     'query':filters,
                                     'score':self.score,
                                     'factor':self.factor,
                                     "incremental_factor":self.incremental_factor}}

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

    def serialize(self):
        filters = {}

        if self.tie_breaker != 0.0:
            filters["tie_breaker"] = self.tie_breaker

        if self.boost != 1.0:
            filters["boost"] = self.boost

        filters["queries"] = [q.serialize() for q in self.queries]
        if not filters["queries"]:
            raise InvalidQuery("A least a query is required")
        return {self._internal_name:filters}

class FieldQuery(Query):
    _internal_name = "field"

    def __init__(self, fieldparameters=None, default_operator="OR",
                analyzer=None,
                allow_leading_wildcard=True,
                lowercase_expanded_terms=True,
                enable_position_increments=True,
                fuzzy_prefix_length=0,
                fuzzy_min_sim=0.5,
                phrase_slop=0,
                boost=1.0,
                use_dis_max=True,
                tie_breaker=0, **kwargs):
        super(FieldQuery, self).__init__(**kwargs)
        self.field_parameters = []
        self.default_operator = default_operator
        self.analyzer = analyzer
        self.allow_leading_wildcard = allow_leading_wildcard
        self.lowercase_expanded_terms = lowercase_expanded_terms
        self.enable_position_increments = enable_position_increments
        self.fuzzy_prefix_length = enable_position_increments
        self.fuzzy_min_sim = fuzzy_min_sim
        self.phrase_slop = phrase_slop
        self.boost = boost
        self.use_dis_max = use_dis_max
        self.tie_breaker = tie_breaker
        if fieldparameters:
            if isinstance(fieldparameters, list):
                self.field_parameters.extend(fieldparameters)
            else:
                self.field_parameters.append(fieldparameters)

    def add(self, field, query, **kwargs):
        fp = FieldParameter(field, query, **kwargs)
        self.field_parameters.append(fp)

    def serialize(self):
        result = {}
        for f in self.field_parameters:
            val, filters = f.serialize()
            result[val] = filters

        return {self._internal_name:result}

class FilteredQuery(Query):
    _internal_name = "filtered"

    def __init__(self, query, filter, **kwargs):
        super(FilteredQuery, self).__init__(**kwargs)
        self.query = query
        self.filter = filter

    def serialize(self):
        filters = {
                   'query':self.query.serialize(),
                   'filter':self.filter.serialize(),
                   }

        return {self._internal_name:filters}

class MoreLikeThisFieldQuery(Query):
    _internal_name = "more_like_this_field"

    def __init__(self, field, like_text,
                     percent_terms_to_match=0.3,
                    min_term_freq=2,
                    max_query_terms=25,
                    stop_words=None,
                    min_doc_freq=5,
                    max_doc_freq=None,
                    min_word_len=0,
                    max_word_len=0,
                    boost_terms=1,
                    boost=1.0,
                 **kwargs):
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

    def serialize(self):
        filters = {'like_text':self.like_text}

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
        return {self._internal_name:{self.field:filters}}


class FuzzyLikeThisQuery(Query):
    _internal_name = "fuzzy_like_this"

    def __init__(self, fields, like_text,
                     ignore_tf=False, max_query_terms=25,
                     boost=1.0, **kwargs):
        super(FuzzyLikeThisQuery, self).__init__(**kwargs)
        self.fields = fields
        self.like_text = like_text
        self.ignore_tf = ignore_tf
        self.max_query_terms = max_query_terms
        self.boost = boost

    def serialize(self):
        filters = {'fields':self.fields,
                   'like_text':self.like_text}

        if self.ignore_tf:
            filters["ignore_tf"] = self.ignore_tf
        if self.max_query_terms != 25:
            filters["max_query_terms"] = self.max_query_terms
        if self.boost != 1.0:
            filters["boost"] = self.boost
        return {self._internal_name:filters}

class FuzzyQuery(Query):
    """
    A fuzzy based query that uses similarity based on Levenshtein (edit distance) algorithm.

    Note
        Warning: this query is not very scalable with its default prefix length of 0 - in this case, every term will be enumerated and cause an edit score calculation. Here is a simple example:

    """
    _internal_name = "fuzzy"

    def __init__(self, field, value, boost=None,
            min_similarity=0.5, prefix_length=0,
            **kwargs):
        super(FuzzyQuery, self).__init__(**kwargs)
        self.field = field
        self.value = value
        self.boost = boost
        self.min_similarity = min_similarity
        self.prefix_length = prefix_length

    def serialize(self):
        data = {
                'field':self.field,
                'value':self.value,
                'min_similarity':self.min_similarity,
                'prefix_length':self.prefix_length,
                }
        if self.boost:
            data['boost'] = self.boost
        return {self._internal_name:data}

class FuzzyLikeThisFieldQuery(Query):
    _internal_name = "fuzzy_like_this_field"

    def __init__(self, field, like_text,
                     ignore_tf=False, max_query_terms=25,
                     boost=1.0, **kwargs):
        super(FuzzyLikeThisFieldQuery, self).__init__(**kwargs)
        self.field = field
        self.like_text = like_text
        self.ignore_tf = ignore_tf
        self.max_query_terms = max_query_terms
        self.boost = boost

    def serialize(self):
        filters = {'like_text':self.like_text}

        if self.ignore_tf:
            filters["ignore_tf"] = self.ignore_tf
        if self.max_query_terms != 25:
            filters["max_query_terms"] = self.max_query_terms
        if self.boost != 1.0:
            filters["boost"] = self.boost
        return {self._internal_name:{self.field:filters}}

class MatchAllQuery(Query):
    _internal_name = "match_all"
    def __init__(self, boost=None, **kwargs):
        super(MatchAllQuery, self).__init__(**kwargs)
        self.boost = boost

    def serialize(self):
        filters = {}
        if self.boost:
            if isinstance(self.boost, (float, int)):
                filters['boost'] = self.boost
            else:
                filters['boost'] = float(self.boost)
        return {self._internal_name:filters}

class MoreLikeThisQuery(Query):
    _internal_name = "more_like_this"

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
                    boost=1.0, **kwargs):
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

    def serialize(self):
        filters = {'fields':self.fields,
                   'like_text':self.like_text}

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
        return {self._internal_name:filters}

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

    def serialize(self):
        filters = [f.serialize() for f in self._filters]
        if not filters:
            raise RuntimeError("A least a filter must be declared")
        return {self._internal_name:{"filter":filters}}

    def __repr__(self):
        return str(self.q)

class PrefixQuery(Query):
    def __init__(self, field=None, prefix=None, boost=None, **kwargs):
        super(PrefixQuery, self).__init__(**kwargs)
        self._values = {}

        if field is not None and prefix is not None:
            self.add(field, prefix)

    def add(self, field, prefix, boost=None):
        match = {'prefix':prefix}
        if boost:
            if isinstance(boost, (float, int)):
                match['boost'] = boost
            else:
                match['boost'] = float(boost)
        self._values[field] = match

    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/prefix pair must be added")
        return {"prefix":self._values}

class TermQuery(Query):
    _internal_name = "term"

    def __init__(self, field=None, value=None, boost=None, **kwargs):
        super(TermQuery, self).__init__(**kwargs)
        self._values = {}

        if field is not None and value is not None:
            self.add(field, value)

    def add(self, field, value, boost=None):
        if not value.strip():
            raise InvalidParameterQuery("value %r must be valid text" % value)
        match = {'value':value}
        if boost:
            if isinstance(boost, (float, int)):
                match['boost'] = boost
            else:
                match['boost'] = float(boost)
            self._values[field] = match
            return

        self._values[field] = value

    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return {self._internal_name:self._values}

class TermsQuery(TermQuery):
    _internal_name = "terms"

    def __init__(self, *args, **kwargs):
        super(TermsQuery, self).__init__(*args, **kwargs)

    def add(self, field, value, minimum_match=1):
        if isinstance(value, list):
            raise InvalidParameterQuery("value %r must be valid list" % value)
        self._values[field] = value
        if minimum_match:
            if isinstance(minimum_match, int):
                self._values['minimum_match'] = minimum_match
            else:
                self._values['minimum_match'] = int(minimum_match)

class RegexTermQuery(TermQuery):
    _internal_name = "regex_term"

    def __init__(self, *args, **kwargs):
        super(RegexTermQuery, self).__init__(*args, **kwargs)

class StringQuery(Query):
    _internal_name = "query_string"

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
                use_dis_max=True,
                tie_breaker=0,
                clean_text=False,
                **kwargs):
        super(StringQuery, self).__init__(**kwargs)
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
        self.use_dis_max = use_dis_max
        self.tie_breaker = tie_breaker


    def serialize(self):
        filters = {}
        if self.default_field:
            filters["default_field"] = self.default_field
            if not isinstance(self.default_field, (str, unicode)) and isinstance(self.default_field, list):
                if not self.use_dis_max:
                    filters["use_dis_max"] = self.use_dis_max
                if self.tie_breaker != 0:
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
            if isinstance(self.search_fields, (str, unicode)):
                filters["fields"] = [self.search_fields]
            else:
                filters["fields"] = self.search_fields

            if len(filters["fields"]) > 1:
                if not self.use_dis_max:
                    filters["use_dis_max"] = self.use_dis_max
                if self.tie_breaker != 0:
                    filters["tie_breaker"] = self.tie_breaker
        if self.boost != 1.0:
            filters["boost"] = self.boost
        if self.clean_text:
            query = clean_string(self.query)
            if not query:
                raise InvalidQuery("The query is empty")
            filters["query"] = query
        else:
            if not self.query.strip():
                raise InvalidQuery("The query is empty")
            filters["query"] = self.query
        return {self._internal_name:filters}

class RangeQuery(Query):

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

    def serialize(self):
        if not self.ranges:
            raise RuntimeError("A least a range must be declared")
        filters = dict([r.serialize() for r in self.ranges])
        return {"range":filters}

class SpanFirstQuery(TermQuery):
    _internal_name = "span_first"

    def __init__(self, field=None, value=None, end=3, **kwargs):
        super(SpanFirstQuery, self).__init__(**kwargs)
        self._values = {}
        self.end = end
        if field is not None and value is not None:
            self.add(field, value)

    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return {self._internal_name:{"match":{"span_first":self._values},
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
    _internal_name = "span_near"

    def __init__(self, clauses=None, slop=None,
                 in_order=None,
                 collect_payloads=None, **kwargs):
        super(SpanNotQuery, self).__init__(**kwargs)
        self.clauses = clauses or []
        self.slop = slop
        self.in_order = in_order
        self.collect_payloads = collect_payloads

    def _validate(self):
        for clause in self.clauses:
            if not is_a_spanquery(clause):
                raise RuntimeError("Invalid clause:%r" % clause)

    def serialize(self):
        if not self.clauses or len(self.clauses) == 0:
            raise RuntimeError("A least a Span*Query must be added to clauses")
        data = {}
        if self.slop is not None:
            data["slop"] = self.slop
        if self.in_order is not None:
            data["in_order"] = self.in_order
        if self.collect_payloads is not None:
            data["collect_payloads"] = self.collect_payloads

        data['clauses'] = [clause.serizialize() for clause in self.clauses]

        return {self._internal_name:data}

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

    def serialize(self):

        self._validate()
        data = {}
        data['include'] = self.include.serizialize()
        data['exclude'] = self.exclude.serizialize()

        return {self._internal_name:data}

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
    _internal_name = "span_or"

    def __init__(self, clauses=None, **kwargs):
        super(SpanOrQuery, self).__init__(**kwargs)
        self.clauses = clauses or []

    def _validate(self):
        for clause in self.clauses:
            if not is_a_spanquery(clause):
                raise RuntimeError("Invalid clause:%r" % clause)

    def serialize(self):
        if not self.clauses or len(self.clauses) == 0:
            raise RuntimeError("A least a Span*Query must be added to clauses")
        clauses = [clause.serizialize() for clause in self.clauses]
        return {self._internal_name:{"clauses":clauses}}

class SpanTermQuery(TermQuery):
    _internal_name = "span_term"

    def __init__(self, **kwargs):
        super(SpanTermQuery, self).__init__(**kwargs)



class WildcardQuery(TermQuery):
    _internal_name = "wildcard"

    def __init__(self, *args, **kwargs):
        super(WildcardQuery, self).__init__(*args, **kwargs)

class CustomScoreQuery(Query):
    _internal_name = "custom_score"

    def __init__(self, query=None, script=None, params=None, lang=None,
                 **kwargs):
        super(CustomScoreQuery, self).__init__(**kwargs)
        self.query = query
        self.script = script
        self.lang = lang
        if params is None:
            params = {}
        self.params = params

    def add_param(self, name, value):
        """
        Add a parameter
        """
        self.params[name] = value

    def serialize(self):
        data = {}
        if not self.query:
            raise RuntimeError("A least a query must be declared")
        data['query'] = self.query.serialize()
        if not self.script:
            raise RuntimeError("A script must be provided")
        data['script'] = self.script
        if self.params:
            data['params'] = self.params
        if self.lang:
            data['lang'] = self.lang
        return {self._internal_name:data}

    def __repr__(self):
        return str(self.q)
