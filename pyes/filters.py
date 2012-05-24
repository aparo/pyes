# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy

from .exceptions import QueryParameterError
from .utils import ESRange, EqualityComparableUsingAttributeDictionary
from .es import encode_json, json

class Filter(EqualityComparableUsingAttributeDictionary):
    _internal_name = "undefined"

    def __init__(self, _cache=None, _cache_key=None, **kwargs):
        """
        Base Object for every Filter Object
        """
        self._cache=_cache
        self._cache_key=_cache_key

    def serialize(self):
        raise NotImplementedError

    def _add_parameters(self, data):
        """
        Extend the serializable dict adding global parameters if they are set
        """
        if self._cache:
            data["_cache"]=self._cache
        if self._cache_key:
            data["_cache_key"]=self._cache_key
        return data

    @property
    def q(self):
        res = {"filter": self.serialize()}
        return res

    def to_json(self):
        return encode_json(self.q)


class FilterList(Filter):
    def __init__(self, filters, **kwargs):
        super(FilterList, self).__init__(**kwargs)
        self.filters = filters

    def serialize(self):
        if not self.filters:
            raise RuntimeError("A least a filter must be declared")
        return self._add_parameters({self._internal_name: [filter.serialize() for filter in self.filters]})

    def __iter__(self):
        return iter(self.filters)


class ANDFilter(FilterList):
    """
    A filter that matches combinations of other filters using the AND operator

    Example:

    t1 = TermFilter('name', 'john')
    t2 = TermFilter('name', 'smith')
    f = ANDFilter([t1, t2])
    q = FilteredQuery(MatchAllQuery(), f)
    results = conn.search(q)

    """
    _internal_name = "and"

    def __init__(self, *args, **kwargs):
        super(ANDFilter, self).__init__(*args, **kwargs)


class BoolFilter(Filter):
    """
    A filter that matches documents matching boolean combinations of other
    queries. Similar in concept to Boolean query, except that the clauses are
    other filters. Can be placed within queries that accept a filter.
    """

    def __init__(self, must=None, must_not=None, should=None,
                 minimum_number_should_match=1, **kwargs):
        super(BoolFilter, self).__init__(**kwargs)

        self._must = []
        self._must_not = []
        self._should = []
        self.minimum_number_should_match = minimum_number_should_match
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
        return not any([self._must, self._must_not, self._should])

    def serialize(self):
        filters = {}
        if self._must:
            filters['must'] = [f.serialize() for f in self._must]
        if self._must_not:
            filters['must_not'] = [f.serialize() for f in self._must_not]
        if self._should:
            filters['should'] = [f.serialize() for f in self._should]
            filters['minimum_number_should_match'] = self.minimum_number_should_match
        if not filters:
            raise RuntimeError("A least a filter must be declared")
        return self._add_parameters({"bool": filters})


class ORFilter(FilterList):
    """
    A filter that matches combinations of other filters using the OR operator

    Example:

    t1 = TermFilter('name', 'john')
    t2 = TermFilter('name', 'smith')
    f = ORFilter([t1, t2])
    q = FilteredQuery(MatchAllQuery(), f)
    results = conn.search(q)

    """
    _internal_name = "or"

    def __init__(self, *args, **kwargs):
        super(ORFilter, self).__init__(*args, **kwargs)


class NotFilter(Filter):
    _internal_name = "not"

    def __init__(self, filter, **kwargs):
        super(NotFilter, self).__init__(**kwargs)
        self.filter = filter

    def serialize(self):
        if not isinstance(self.filter, Filter):
            raise RuntimeError("NotFilter argument should be a Filter")
        return self._add_parameters({self._internal_name: {"filter": self.filter.serialize()}})


class RangeFilter(Filter):
    def __init__(self, qrange=None, **kwargs):
        super(RangeFilter, self).__init__(**kwargs)

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
        return self._add_parameters({"range": filters})

NumericRangeFilter = RangeFilter

class PrefixFilter(Filter):
    _internal_name = "prefix"

    def __init__(self, field=None, prefix=None, **kwargs):
        super(PrefixFilter, self).__init__(**kwargs)
        self._values = {}

        if field is not None and prefix is not None:
            self.add(field, prefix)

    def add(self, field, prefix):
        self._values[field] = prefix

    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/prefix pair must be added")
        return self._add_parameters({self._internal_name: self._values})


class ScriptFilter(Filter):
    _internal_name = "script"

    def __init__(self, script, params=None, **kwargs):
        super(ScriptFilter, self).__init__(**kwargs)
        self.script = script
        self.params = params


    def add(self, field, value):
        self.params[field] = {'value': value}

    def serialize(self):
        data = {'script': self.script}
        if self.params is not None:
            data['params'] = self.params
        return self._add_parameters({self._internal_name: data})


class TermFilter(Filter):
    _internal_name = "term"

    def __init__(self, field=None, value=None, _name=None, **kwargs):
        super(TermFilter, self).__init__(**kwargs)
        self._values = {}
        self._name = _name

        if field is not None and value is not None:
            self.add(field, value)

    def add(self, field, value):
        self._values[field] = value

    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        result = {self._internal_name: self._values}
        if self._name:
            result[self._internal_name]['_name'] = self._name
        return self._add_parameters({self._internal_name: self._values})


class ExistsFilter(TermFilter):
    _internal_name = "exists"

    def __init__(self, field=None, **kwargs):
        super(ExistsFilter, self).__init__(field="field", value=field, **kwargs)


class MissingFilter(TermFilter):
    _internal_name = "missing"

    def __init__(self, field=None, **kwargs):
        super(MissingFilter, self).__init__(field="field", value=field, **kwargs)


class RegexTermFilter(Filter):
    _internal_name = "regex_term"

    def __init__(self, field=None, value=None, **kwargs):
        super(RegexTermFilter, self).__init__(**kwargs)
        self._values = {}

        if field is not None and value is not None:
            self.add(field, value)

    def add(self, field, value):
        self._values[field] = value

    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return self._add_parameters({self._internal_name: self._values})

class LimitFilter(Filter):
    _internal_name = "limit"

    def __init__(self, value=100, **kwargs):
        super(LimitFilter, self).__init__(**kwargs)
        self.value=value

    def serialize(self):
        return self._add_parameters({self._internal_name: {"value":self.value}})

class TermsFilter(Filter):
    _internal_name = "terms"

    def __init__(self, field=None, values=None, _name=None, execution=None, **kwargs):
        super(TermsFilter, self).__init__(**kwargs)
        self._values = {}
        self._name = _name
        self.execution = execution

        if field is not None and values is not None:
            self.add(field, values)

    def add(self, field, values):
        self._values[field] = values

    def serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        data = copy.deepcopy(self._values)
        if self.execution:
            data['execution'] = self.execution
        if self._name:
            data['_name'] = self._name
        return self._add_parameters({self._internal_name: data})


class QueryFilter(Filter):
    _internal_name = "query"

    def __init__(self, query, **kwargs):
        super(QueryFilter, self).__init__(**kwargs)
        self._query = query

    def serialize(self):
        if not self._query:
            raise RuntimeError("A least a field/value pair must be added")
        return self._add_parameters({self._internal_name: self._query.serialize()})

#
#--- Geo Queries
#http://www.elasticsearch.com/blog/2010/08/16/geo_location_and_search.html

class GeoDistanceFilter(Filter):
    """

    http://github.com/elasticsearch/elasticsearch/issues/279

    """
    _internal_name = "geo_distance"

    def __init__(self, field, location, distance, distance_type="arc", distance_unit=None, **kwargs):
        super(GeoDistanceFilter, self).__init__(**kwargs)
        self.field = field
        self.location = location
        self.distance = distance
        self.distance_type = distance_type
        self.distance_unit = distance_unit

    def serialize(self):
        if self.distance_type not in ["arc", "plane"]:
            raise QueryParameterError("Invalid distance_type")

        params = {"distance": self.distance, self.field: self.location}
        if self.distance_type != "arc":
            params['distance_type'] = self.distance_type

        if self.distance_unit:
            if self.distance_unit not in ["km", "mi", "miles"]:
                raise QueryParameterError("Invalid distance_unit")
            params['distance_unit'] = self.distance_unit

        return self._add_parameters({self._internal_name: params})


class GeoBoundingBoxFilter(Filter):
    """

    http://github.com/elasticsearch/elasticsearch/issues/290

    """
    _internal_name = "geo_bounding_box"

    def __init__(self, field, location_tl, location_br, **kwargs):
        super(GeoBoundingBoxFilter, self).__init__(**kwargs)
        self.field = field
        self.location_tl = location_tl
        self.location_br = location_br

    def serialize(self):
        return self._add_parameters({self._internal_name: {
            self.field: {
                "top_left": self.location_tl,
                "bottom_right": self.location_br
            }
        }
        })


class GeoPolygonFilter(Filter):
    """

    http://github.com/elasticsearch/elasticsearch/issues/294

    """
    _internal_name = "geo_polygon"

    def __init__(self, field, points, **kwargs):
        super(GeoPolygonFilter, self).__init__(**kwargs)
        self.field = field
        self.points = points

    def serialize(self):
        return self._add_parameters({self._internal_name: {
            self.field: {
                "points": self.points,
                }
        }
        })


class MatchAllFilter(Filter):
    """
    A filter that matches on all documents
    """
    _internal_name = "match_all"

    def __init__(self, **kwargs):
        super(MatchAllFilter, self).__init__(**kwargs)

    def serialize(self):
        return self._add_parameters({self._internal_name: {}})


class HasChildFilter(Filter):
    """
    The has_child filter accepts a query and the child type to run against,
    and results in parent documents that have child docs matching the query
    """
    _internal_name = "has_child"

    def __init__(self, type, filter, _scope=None, **kwargs):
        super(HasChildFilter, self).__init__(**kwargs)
        self.filter = filter
        self.type = type
        self._scope = _scope

    def serialize(self):
        if not isinstance(self.filter, Filter):
            raise RuntimeError("NotFilter argument should be a Filter")
        data = {"query": self.filter.serialize(),
                "type": self.type}
        if self._scope is not None:
            data['_scope'] = self._scope
        return self._add_parameters({self._internal_name: data})


class NestedFilter(Filter):
    """
    A nested filter, works in a similar fashion to the nested query, except
    used as a filter. It follows exactly the same structure, but also allows
    to cache the results (set _cache to true), and have it named
    (set the _name value).    """
    _internal_name = "nested"

    def __init__(self, path, filter, **kwargs):
        super(NestedFilter, self).__init__(**kwargs)
        self.path = path
        self.filter = filter

    def serialize(self):
        data = {
            'path': self.path,
            'query': self.filter.serialize()}
        return self._add_parameters({self._internal_name: data})


class IdsFilter(Filter):
    _internal_name = "ids"
    def __init__(self, values, type=None, **kwargs):
        super(IdsFilter, self).__init__(**kwargs)
        self.type = type
        self.values = values

    def serialize(self):
        data = {}
        if self.type:
            data['type'] = self.type
        if isinstance(self.values, basestring):
            data['values'] = [self.values]
        else:
            data['values'] = self.values

        return self._add_parameters({self._internal_name: data})


class RawFilter(Filter):
    """
    Uses exactly the filter provided as an ES filter.
    """

    def __init__(self, filter_text_or_dict, **kwargs):
        super(RawFilter, self).__init__(**kwargs)
        if isinstance(filter_text_or_dict, basestring):
            self._filter = json.loads(filter_text_or_dict)
        else:
            self._filter = filter_text_or_dict

    def serialize(self):
        return self._filter
