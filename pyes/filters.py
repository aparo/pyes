#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'
from pyes.exceptions import QueryParameterError, InvalidParameter

from pyes.es import encode_json
from pyes.models import DotDict

FILTER_PARAMETERS = {
                    "GeoDistanceFilter":{
                                   "field":{"type":basestring},
                                   "location":{},
                                   "distance":{"type":basestring},
                                   "distance_type":{"type":basestring, "default":'arc', "values":["arc", "plane"]},
                                   "distance_unit":{"type":basestring, "values":["km", "mi", "miles"]},
                                   },

                    "IdsFilter":{
                                      "type":{"type":basestring},
                                      "values":{"type":list},
                                      },
                    "NestedFilter":{
                                   "path":{"type":basestring},
                                   "query":{"type":dict},
                                   "score_mode":{"type":basestring, "default":'avg', "values":["avg", "total", "max"]}
                                   },
                     "ScriptFilter":{
                                   "script":{"type":basestring},
                                   "params":{"type":dict},
                                     }
                     }

class Filter(DotDict):

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

            parameters = FILTER_PARAMETERS.get(self.__class__.__name__, {})
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
        return {self.filter_name:self}

    @property
    def q(self):
        res = {"filter":self.serialize()}
        return res

    def to_json(self):
        return encode_json(self.q)

class FilterList(object):
    def __init__(self, filters, **kwargs):
        super(FilterList, self).__init__(**kwargs)
        self.filters = filters



class ANDFilter(Filter):
    filter_name = "and"
    def __init__(self, filters):
        super(ANDFilter, self).__init__()
        self.__initialised = True
        self[self.filter_name] = [f.serialize() for f in filters]

    def serialize(self):
        return self

class BoolFilter(Filter):
    """
    A filter that matches documents matching boolean combinations of other 
    queries. Similar in concept to Boolean query, except that the clauses are 
    other filters. Can be placed within queries that accept a filter.
    """

    def __init__(self, must=None, must_not=None, should=None, minimum_number_should_match=1):
        super(BoolFilter, self).__init__()
        self.__initialised = True

        self.minimum_number_should_match = minimum_number_should_match
        if must:
            self.add_must(must)

        if must_not:
            self.add_must_not(must_not)

        if should:
            self.add_should(should)

    def add_must(self, queries):
        """Add a filter to the "must" clause of the filter.

        The BoolFilter object will be returned, so calls to this can be chained.

        """
        if self.must is None:
            self.must = []
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            if isinstance(query, Filter):
                self.must.append(query.serialize())
            else:
                self.must.append(query)
        return self

    def add_should(self, queries):
        """Add a filter to the "should" clause of the filter.

        The BoolFilter object will be returned, so calls to this can be chained.

        """
        if self.should is None:
            self.should = []
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            if isinstance(query, Filter):
                self.should.append(query.serialize())
            else:
                self.should.append(query)
        return self

    def add_must_not(self, queries):
        """Add a filter to the "must_not" clause of the filter.

        The BoolFilter object will be returned, so calls to this can be chained.

        """
        if self.must_not is None:
            self.must_not = []
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            if isinstance(query, Filter):
                self.must_not.append(query.serialize())
            else:
                self.must_not.append(query)
        return self


    def is_empty(self):
        if self._must:
            return False
        if self._must_not:
            return False
        if self._should:
            return False
        return True


class ORFilter(Filter):
    filter_name = "or"

    def __init__(self, filters):
        super(ORFilter, self).__init__()
        self.__initialised = True
        self[self.filter_name] = [f.serialize() for f in filters]

    def serialize(self):
        return self

class NotFilter(Filter):
    filter_name = "not"
    def __init__(self, filter, **kwargs):
        super(NotFilter, self).__init__(**kwargs)
        self.__initialised = True
        self.filter = filter

    def _validate_field(self, key, value):
        """
        If key is None, remove from fields
        """
        if key == "filter":
            if isinstance(value, Filter):
                return key, value.serialize()
        return key, value

class RangeFilter(Filter):

    def __init__(self, ranges, **kwargs):
        super(RangeFilter, self).__init__(**kwargs)
        self.__initialised = True
        self.range = []
        self.add(ranges)

    def add(self, qrange):
        from pyes.query import ESRange
        if isinstance(qrange, list):
            for r in qrange:
                self.range.append(r.serialize())
        elif isinstance(qrange, ESRange):
            self.range.append(qrange.serialize())

NumericRangeFilter = RangeFilter

class PrefixFilter(Filter):
    filter_name = "prefix"

    def __init__(self, field, prefix, **kwargs):
        super(PrefixFilter, self).__init__(**kwargs)
        self.__initialised = True
        self.add(field, prefix)

    def add(self, field, prefix):
        self[field] = prefix

class ScriptFilter(Filter):
    filter_name = "script"

    def __init__(self, script, params=None):
        super(ScriptFilter, self).__init__()
        self.__initialised = True
        self.script = script
        self.params = params

class TermFilter(Filter):
    filter_name = "term"

    def __init__(self, field, value, _name=None):
        super(TermFilter, self).__init__()
        self.__initialised = True
        self._name = _name

        self.add(field, value)

    def add(self, field, value):
        self[field] = value

class ExistsFilter(TermFilter):
    filter_name = "exists"
    def __init__(self, field=None, **kwargs):
        self.__initialised = True
        super(ExistsFilter, self).__init__(field="field", value=field, **kwargs)

class MissingFilter(TermFilter):
    filter_name = "missing"
    def __init__(self, field=None, **kwargs):
        self.__initialised = True
        super(MissingFilter, self).__init__(field="field", value=field, **kwargs)

class RegexTermFilter(Filter):
    filter_name = "regex_term"

    def __init__(self, field, value):
        super(RegexTermFilter, self).__init__()
        self.__initialised = True
        self.add(field, value)

    def add(self, field, value):
        self[field] = value

class TypeFilter(TermFilter):
    filter_name = 'type'

    def __init__(self, field=None, **kwargs):
        self.__initialized = True
        super(TypeFilter, self).__init__(field="value", value=field, **kwargs)

class TermsFilter(Filter):
    filter_name = "terms"

    def __init__(self, field, values, _name=None):
        super(TermsFilter, self).__init__()
        self.__initialised = True
        self._name = _name

        self.add(field, values)

    def add(self, field, values):
        self[field] = values


class QueryFilter(Filter):
    filter_name = "query"

    def __init__(self, query):
        super(QueryFilter, self).__init__()
        self.__initialised = True
        self.query = query

    def _validate_field(self, key, value):
        """
        If key is None, remove from fields
        """
        if key == "query":
            from pyes.query import Query
            if isinstance(value, Query):
                return key, value.serialize()
        return key, value
#
#--- Geo Queries
#http://www.elasticsearch.com/blog/2010/08/16/geo_location_and_search.html

class GeoDistanceFilter(Filter):
    """
    
    http://github.com/elasticsearch/elasticsearch/issues/279
    
    """
    filter_name = "geo_distance"

    def __init__(self, field, location, distance, distance_type="arc", distance_unit=None):
        super(GeoDistanceFilter, self).__init__()
        self.__initialised = True
        self.field = field
        self.location = location
        self.distance = distance
        self.distance_type = distance_type
        self.distance_unit = distance_unit

class GeoBoundingBoxFilter(Filter):
    """
    
    http://github.com/elasticsearch/elasticsearch/issues/290
    
    """
    filter_name = "geo_bounding_box"

    def __init__(self, field, location_tl, location_br):
        super(GeoBoundingBoxFilter, self).__init__()
        self.__initialised = True
        self[field] = DotDict(top_left=location_tl,
                            bottom_right=location_br)

class GeoPolygonFilter(Filter):
    """
    
    http://github.com/elasticsearch/elasticsearch/issues/294
    
    """
    filter_name = "geo_polygon"

    def __init__(self, field, points):
        super(GeoPolygonFilter, self).__init__()
        self.__initialised = True
        self[field] = DotDict(points=points)

class MatchAllFilter(Filter):
    """
    A filter that matches on all documents
    """
    filter_name = "match_all"
    def __init__(self):
        super(MatchAllFilter, self).__init__()
        self.__initialised = True

class HasChildFilter(Filter):
    """
    The has_child filter accepts a query and the child type to run against, 
    and results in parent documents that have child docs matching the query
    """
    filter_name = "has_child"
    def __init__(self, type, filter, _scope=None):
        self.__initialised = True
        super(HasChildFilter, self).__init__()
        self.filter = filter
        self.type = type
        self._scope = _scope

    def _validate_field(self, key, value):
        """
        If key is None, remove from fields
        """
        if key == "filter":
            if isinstance(value, Filter):
                return key, value.serialize()
        return key, value

class NestedFilter(Filter):
    """
    A nested filter, works in a similar fashion to the nested query, except 
    used as a filter. It follows exactly the same structure, but also allows 
    to cache the results (set _cache to true), and have it named 
    (set the _name value).    """
    filter_name = "nested"

    def __init__(self, path, filter, **kwargs):
        super(NestedFilter, self).__init__(**kwargs)
        self.__initialised = True
        self.path = path
        self.filter = filter

class IdsFilter(Filter):
    filter_name = "ids"
    def __init__(self, type, values, **kwargs):
        super(IdsFilter, self).__init__(**kwargs)
        self.__initialised = True
        self.type = type
        self.values = values
