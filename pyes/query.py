#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import logging
try:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson as json
except ImportError:
    # For Python >= 2.6
    import json

from elasticsearch import ESJsonEncoder


log = logging.getLogger('pyes')

class QueryParameterError(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)
    
class HighLighter:
    def __init__(self, pre_tags = None, post_tags = None, fields = None):
        self.pre_tags = pre_tags
        self.post_tags = post_tags
        self.fields = fields or {}
    
    def add_field(self, name, fragment_size=150, number_of_fragments=3):
        """
        Add a field to Highlinghter
        """
        data = {}
        if fragment_size:
            data['fragment_size'] = fragment_size
        if number_of_fragments:
            data['number_of_fragments'] = number_of_fragments
            
        self.fields[name] = data

    def serialize(self):
        res = {}
        if self.pre_tags:
            res["pre_tags"] = self.pre_tags
        if self.post_tags:
            res["post_tags"] = self.post_tags
        if self.fields:
            res["fields"] = self.fields
        else:
            res["fields"] = {"_all" : {}}
        return res

class Query(object):
    def __init__(self, 
                 return_fields = None,
                 start = 0,
                 size=None,
                 highlight=None,
                 sort = None):
        
        self.return_fields = return_fields
        self.start = start
        self.size = size
        self.highlight=highlight
        self.sort = sort
    
    @property
    def q(self):
        res = {"query":self.serialize()}
        if self.return_fields:
            res['fields']=self.return_fields
        if self.size is not None:
            res['size']=self.size
        if self.start:
            res['from']=self.start
        if self.highlight:
            res['highlight'] = self.highlight.serialize()
        if self.sort:
            res['sort'] = self.sort
        return res

    def add_highlight(self, field, fragment_size=None, number_of_fragments=None):
        """
        Add an highlight field
        """
        if self.highlight is None:
            self.highlight = HighLighter("<b>", "</b>")
        self.highlight.add_field(field, fragment_size, number_of_fragments)
        

    def count(self):
        return self.serialize()

    def __repr__(self):
        return str(self.q)

    def to_json(self):
        return json.dumps(self.q, cls=ESJsonEncoder)


class AbstractFilter(Query):
    _internal_name = "undefined"
    def __init__(self, filters=None, **kwargs):
        super(AbstractFilter, self).__init__(**kwargs)

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
        return {self._internal_name:{"filters":filters}}

class ANDFilterQuery(AbstractFilter):
    _internal_name = "and"
    def __init__(self, *args, **kwargs):
        super(ANDFilterQuery, self).__init__(*args, **kwargs)

class ORFilterQuery(AbstractFilter):
    _internal_name = "or"
    def __init__(self, *args, **kwargs):
        super(ORFilterQuery, self).__init__(*args, **kwargs)
    

class BoolQuery(Query):
    boost = None
    minimum_number_should_match = 1
    
    def __init__(self, must=None, must_not=None, should=None, **kwargs):
        super(BoolQuery, self).__init__(**kwargs)

        self._must = []
        self._must_not = []
        self._should = []
        
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
        if not filters:
            raise RuntimeError("A least a filter must be declared")
        return {"bool":filters}


class ESRange:
    def __init__(self, field, _from=None, _to=None, include_lower=True, include_upper=True, boost=None, **kwargs):
        self.field = field
        self.fromV = _from
        self.to = _to
        self.include_lower = include_lower
        self.include_upper = include_upper
        self.boost = boost
        
    def serialize(self):
        filters = {}
        if self.fromV:
            filters['from'] = self.fromV
        if self.to:
            filters['to'] = self.to
        if not self.include_lower:
            filters['include_lower'] = self.include_lower
        if not self.include_upper:
            filters['include_upper'] = self.include_upper
        if self.boost:
            filters['boost'] = self.boost
        return self.field, filters

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
                match['boost']=boost
            else:
                match['boost']=float(boost)
        self._values[field]=match
    
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
        match = {'value':value}
        if boost:
            if isinstance(boost, (float, int)):
                match['boost']=boost
            else:
                match['boost']=float(boost)
            self._values[field]=match
            return
        
        self._values[field]=value
        
    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return {self._internal_name:self._values}

class WildcardQuery(TermQuery):
    _internal_name = "wildcard"

    def __init__(self, *args, **kwargs):
        super(WildcardQuery, self).__init__(*args, **kwargs)

class RegexTermQuery(TermQuery):
    _internal_name = "regex_term"

    def __init__(self, *args, **kwargs):
        super(RegexTermQuery, self).__init__(*args, **kwargs)

class MatchAllQuery(Query):
    _internal_name = "match_all"
    def __init__(self, boost=None, **kwargs):
        super(MatchAllQuery, self).__init__(**kwargs)
        self.boost = boost
        
    def serialize(self):
        filters = {}
        if self.boost:
            if isinstance(self.boost, (float, int)):
                filters['boost']=self.boost
            else:
                filters['boost']=float(self.boost)
        return {self._internal_name:filters}

class StringQuery(Query):
    _internal_name = "query_string"
    
    def __init__(self, query, default_field = None,
                default_operator = "OR",
                analyzer = None,
                allow_leading_wildcard = True,
                lowercase_expanded_terms = True,
                enable_position_increments = True,
                fuzzy_prefix_length = 0,
                fuzzy_min_sim = 0.5,
                phrase_slop = 0,
                boost = 1.0,
                use_dis_max = True,
                tie_breaker = 0, **kwargs):
        super(StringQuery, self).__init__(**kwargs)
        self.text = query
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
            
        if self.boost!=1.0:
            filters["boost"] = self.boost
        filters["query"] = self.text
        
        return {self._internal_name:filters}

class FieldParameter:

    def __init__(self, field, 
                 query, 
                 default_operator = "OR",
                    analyzer = None, 
                    allow_leading_wildcard = True, 
                    lowercase_expanded_terms = True, 
                    enable_position_increments = True, 
                    fuzzy_prefix_length = 0, 
                    fuzzy_min_sim = 0.5, 
                    phrase_slop = 0, 
                    boost = 1.0):
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
            
        if self.boost!=1.0:
            filters["boost"] = self.boost
        if filters:
            filters["query"] = self.query
        else:
            filters = self.query
        return self.field, filters


class FieldQuery(Query):
    _internal_name = "field"
    
    def __init__(self, fieldparameters=None, default_operator = "OR",
                analyzer = None,
                allow_leading_wildcard = True,
                lowercase_expanded_terms = True,
                enable_position_increments = True,
                fuzzy_prefix_length = 0,
                fuzzy_min_sim = 0.5,
                phrase_slop = 0,
                boost = 1.0,
                use_dis_max = True,
                tie_breaker = 0, **kwargs):
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

class DisMaxQuery(Query):
    _internal_name = "dis_max"
    
    def __init__(self, query=None, tie_breaker = 0.0, boost =  1.0, **kwargs ):
        super(DisMaxQuery, self).__init__(**kwargs)
        self.queries = []
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
        
        return {self._internal_name:filters}

class ConstantScoreQuery(Query):
    _internal_name = "constant_score"

    def __init__(self, filter=None, boost =  1.0, **kwargs ):
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

    def serialize(self):
        filters = {}

        if self.boost != 1.0:
            filters["boost"] = self.boost
        
        for f in self.filters:
            filters.update(f.serialize())
        
        return {self._internal_name:filters}
                
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

class MoreLikeThisQuery(Query):
    _internal_name = "more_like_this"

    def __init__(self, fields, like_text, 
                     percent_terms_to_match = 0.3,
                    min_term_freq = 2,
                    max_query_terms = 25,
                    stop_words = None,
                    min_doc_freq = 5,
                    max_doc_freq = None,
                    min_word_len = 0,
                    max_word_len = 0,
                    boost_terms = 1,
                    boost = 1.0, **kwargs):
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

class MoreLikeThisFieldQuery(Query):
    _internal_name = "more_like_this_field"

    def __init__(self, field, like_text, 
                     percent_terms_to_match = 0.3,
                    min_term_freq = 2,
                    max_query_terms = 25,
                    stop_words = None,
                    min_doc_freq = 5,
                    max_doc_freq = None,
                    min_word_len = 0,
                    max_word_len = 0,
                    boost_terms = 1,
                    boost = 1.0,
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
                     ignore_tf = False, max_query_terms = 25,
                     boost = 1.0, **kwargs):
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

class FuzzyLikeThisFieldQuery(Query):
    _internal_name = "fuzzy_like_this_field"

    def __init__(self, field, like_text,
                     ignore_tf = False, max_query_terms = 25,
                     boost = 1.0, **kwargs):
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

class SpanTermQuery(TermQuery):
    _internal_name = "span_term"

    def __init__(self, **kwargs):
        super(SpanTermQuery, self).__init__(**kwargs)

class SpanFirstQuery(TermQuery):
    _internal_name = "span_first"

    def __init__(self, field=None, value=None, end=3):
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

#
#--- Geo Queries
#http://www.elasticsearch.com/blog/2010/08/16/geo_location_and_search.html

class GeoDistanceQuery(Query):
    """
    
    http://github.com/elasticsearch/elasticsearch/issues/279
    
    """
    _internal_name = "geo_distance"

    def __init__(self, field, location, distance, distance_type="arc"):
        self.field = field
        self.location = location
        self.distance = distance
        self.distance_type = distance_type
    
    def serialize(self):
        if self.distance_type not in ["arc", "plane"]:
            raise QueryParameterError("Invalid distance_type")
        
        params = {"distance":self.distance, self.field:self.location}
        if self.distance_type!="arc":
            params['distance_type'] = self.distance_type
            
        return {self._internal_name:params}



def GeoBoundingBoxQuery(Query):
    """
    
    http://github.com/elasticsearch/elasticsearch/issues/290
    
    """
    _internal_name = "geo_bounding_box"

    def __init__(self, field, location_tl, location_br):
        self.field = field
        self.location_tl = location_tl
        self.location_br = location_br
    
    def serialize(self):
        
        return {self._internal_name:{
                                     self.field:{
                                                 "top_left":self.location_tl, 
                                                 "bottom_right":self.location_br
                                                 }
                                     }
        }

class GeoPolygonQuery(Query):
    """
    
    http://github.com/elasticsearch/elasticsearch/issues/294
    
    """
    _internal_name = "geo_polygon"

    def __init__(self, field, points):
        self.field = field
        self.points = points
    
    def serialize(self):
        
        return {self._internal_name:{
                                     self.field:{
                                                 "points":self.points, 
                                                 }
                                     }
        }

         

#class SpanNearQuery(Query):
#
#    
#{
#    "span_near" : {
#        "clauses" : [
#            { "span_term" : { "field" : "value1" } },
#            { "span_term" : { "field" : "value2" } },
#            { "span_term" : { "field" : "value3" } }
#        ],
#        "slop" : 12,
#        "in_order" : false,
#        "collect_payloads" : false
#    }
#}