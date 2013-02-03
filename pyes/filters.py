# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .exceptions import QueryParameterError
from .utils import ESRange, EqualityComparableUsingAttributeDictionary
from .es import encode_json, json
from .query import Query

class Filter(EqualityComparableUsingAttributeDictionary):

    _extra_properties = ("_cache", "cache_key", "_name")

    def __init__(self, **kwargs):
        self._extra_values = {key: kwargs.pop(key)
                              for key in self._extra_properties
                              if kwargs.get(key) is not None}
        if kwargs:
            raise ValueError("Unknown properties: %s" % kwargs.keys())

    def to_json(self):
        return encode_json(self.q)

    @property
    def q(self):
        return {"filter": self.serialize()}

    def serialize(self):
        data = self._serialize()
        if self._extra_values:
            data.update(self._extra_values)
        return {self._internal_name: data}

    def _serialize(self):
        raise NotImplementedError

    @property
    def _internal_name(self):
        raise NotImplementedError



class FilterList(Filter):

    def __init__(self, filters, **kwargs):
        super(FilterList, self).__init__(**kwargs)
        self.filters = filters

    def _serialize(self):
        if not self.filters:
            raise RuntimeError("A least a filter must be declared")
        serialized = [filter.serialize() for filter in self.filters]
        if self._extra_values:
            serialized = {"filters": serialized}
        return serialized

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


class BoolFilter(Filter):
    """
    A filter that matches documents matching boolean combinations of other
    queries. Similar in concept to Boolean query, except that the clauses are
    other filters. Can be placed within queries that accept a filter.
    """

    _internal_name = "bool"

    def __init__(self, must=None, must_not=None, should=None,
                 **kwargs):
        super(BoolFilter, self).__init__(**kwargs)

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
        return not any([self._must, self._must_not, self._should])

    def _serialize(self):
        filters = {}
        if self._must:
            filters["must"] = [f.serialize() for f in self._must]
        if self._must_not:
            filters["must_not"] = [f.serialize() for f in self._must_not]
        if self._should:
            filters["should"] = [f.serialize() for f in self._should]
        if not filters:
            raise RuntimeError("A least a filter must be declared")
        return filters


class NotFilter(Filter):

    _internal_name = "not"

    def __init__(self, filter, **kwargs):
        super(NotFilter, self).__init__(**kwargs)
        self.filter = filter

    def _serialize(self):
        if not isinstance(self.filter, Filter):
            raise RuntimeError("NotFilter argument should be a Filter")
        return {"filter": self.filter.serialize()}


class RangeFilter(Filter):

    _internal_name = "range"

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

    def negate(self):
        """Negate some ranges: useful to resolve a NotFilter(RangeFilter(**))"""
        for r in self.ranges:
            r.negate()

    def _serialize(self):
        if not self.ranges:
            raise RuntimeError("A least a range must be declared")
        return dict([r.serialize() for r in self.ranges])

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

    def _serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/prefix pair must be added")
        return self._values


class ScriptFilter(Filter):

    _internal_name = "script"

    def __init__(self, script, params=None, lang=None, **kwargs):
        super(ScriptFilter, self).__init__(**kwargs)
        self.script = script
        self.params = params
        self.lang = lang

    def add(self, field, value):
        self.params[field] = {"value": value}

    def _serialize(self):
        data = {"script": self.script}
        if self.params is not None:
            data["params"] = self.params
        if self.lang is not None:
            data["lang"] = self.lang
        return data


class TermFilter(Filter):

    _internal_name = "term"

    def __init__(self, field=None, value=None, **kwargs):
        super(TermFilter, self).__init__(**kwargs)
        self._values = {}
        if field is not None and value is not None:
            self.add(field, value)

    def add(self, field, value):
        self._values[field] = value

    def _serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return self._values


class TypeFilter(Filter):

    _internal_name = "type"

    def __init__(self, type, **kwargs):
        super(TypeFilter, self).__init__(**kwargs)
        self.type = type

    def _serialize(self):
        return {"value": self.type}


class ExistsFilter(Filter):

    _internal_name = "exists"

    def __init__(self, field, **kwargs):
        super(ExistsFilter, self).__init__(**kwargs)
        self.field = field

    def _serialize(self):
        return {"field": self.field}


class MissingFilter(Filter):

    _internal_name = "missing"

    def __init__(self, field, **kwargs):
        super(MissingFilter, self).__init__(**kwargs)
        self.field = field

    def _serialize(self):
        return {"field": self.field}


class RegexTermFilter(Filter):

    _internal_name = "regex_term"

    def __init__(self, field=None, value=None, ignorecase=False, **kwargs):
        super(RegexTermFilter, self).__init__(**kwargs)
        self._values = {}
        self.ignorecase = ignorecase
        if field is not None and value is not None:
            self.add(field, value, ignorecase=ignorecase)

    def add(self, field, value, ignorecase=False):
        if ignorecase:
            self._values[field] = {"term":value, "ignorecase":ignorecase}
        else:
            self._values[field] = value

    def _serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        return self._values


class LimitFilter(Filter):

    _internal_name = "limit"

    def __init__(self, value=100, **kwargs):
        super(LimitFilter, self).__init__(**kwargs)
        self.value = value

    def _serialize(self):
        return {"value": self.value}


class TermsFilter(Filter):

    _internal_name = "terms"

    def __init__(self, field=None, values=None, execution=None, **kwargs):
        super(TermsFilter, self).__init__(**kwargs)
        self._values = {}
        self.execution = execution
        if field is not None and values is not None:
            self.add(field, values)

    def add(self, field, values):
        self._values[field] = values

    def _serialize(self):
        if not self._values:
            raise RuntimeError("A least a field/value pair must be added")
        data = self._values.copy()
        if self.execution:
            data["execution"] = self.execution
        return data


class QueryFilter(Filter):

    _internal_name = "query"

    def __init__(self, query, **kwargs):
        super(QueryFilter, self).__init__(**kwargs)
        self._query = query

    def _serialize(self):
        if not self._query:
            raise RuntimeError("A least a field/value pair must be added")
        return self._query.serialize()

#
#--- Geo Queries
#http://www.elasticsearch.com/blog/2010/08/16/geo_location_and_search.html

class GeoDistanceFilter(Filter):
    """http://github.com/elasticsearch/elasticsearch/issues/279"""

    _internal_name = "geo_distance"

    def __init__(self, field, location, distance, distance_type="arc", distance_unit=None, **kwargs):
        super(GeoDistanceFilter, self).__init__(**kwargs)
        self.field = field
        self.location = location
        self.distance = distance
        self.distance_type = distance_type
        self.distance_unit = distance_unit

    def _serialize(self):
        if self.distance_type not in ["arc", "plane"]:
            raise QueryParameterError("Invalid distance_type")

        params = {"distance": self.distance, self.field: self.location}
        if self.distance_type != "arc":
            params["distance_type"] = self.distance_type

        if self.distance_unit:
            if self.distance_unit not in ["km", "mi", "miles"]:
                raise QueryParameterError("Invalid distance_unit")
            params["distance_unit"] = self.distance_unit

        return params


class GeoBoundingBoxFilter(Filter):
    """http://github.com/elasticsearch/elasticsearch/issues/290"""

    _internal_name = "geo_bounding_box"

    def __init__(self, field, location_tl, location_br, **kwargs):
        super(GeoBoundingBoxFilter, self).__init__(**kwargs)
        self.field = field
        self.location_tl = location_tl
        self.location_br = location_br

    def _serialize(self):
        return {self.field: {"top_left": self.location_tl,
                             "bottom_right": self.location_br}}


class GeoPolygonFilter(Filter):
    """http://github.com/elasticsearch/elasticsearch/issues/294"""

    _internal_name = "geo_polygon"

    def __init__(self, field, points, **kwargs):
        super(GeoPolygonFilter, self).__init__(**kwargs)
        self.field = field
        self.points = points

    def _serialize(self):
        return {self.field: {"points": self.points}}


class MatchAllFilter(Filter):
    """A filter that matches on all documents"""

    _internal_name = "match_all"

    def __init__(self, **kwargs):
        super(MatchAllFilter, self).__init__(**kwargs)

    def _serialize(self):
        return {}


class HasFilter(Filter):

    def __init__(self, type, query, _scope=None, **kwargs):
        if not isinstance(query, Query):
            raise RuntimeError("%s expects a Query" % self.__class__.__name__)
        super(HasFilter, self).__init__(**kwargs)
        self.query = query
        self.type = type
        self._scope = _scope

    def _serialize(self):
        data = {"query": self.query.serialize(), "type": self.type}
        if self._scope is not None:
            data["_scope"] = self._scope
        return data


class HasChildFilter(HasFilter):
    """
    The has_child filter accepts a query and the child type to run against,
    and results in parent documents that have child docs matching the query
    """

    _internal_name = "has_child"


class HasParentFilter(HasFilter):
    """
    The has_parent filter accepts a query and the parent type to run against,
    and results in child documents that have parent docs matching the query
    """

    _internal_name = "has_parent"


class NestedFilter(Filter):
    """
    A nested filter, works in a similar fashion to the nested query, except
    used as a filter. It follows exactly the same structure, but also allows
    to cache the results (set _cache to true), and have it named
    (set the _name value).
    """

    _internal_name = "nested"

    def __init__(self, path, filter, **kwargs):
        super(NestedFilter, self).__init__(**kwargs)
        self.path = path
        self.filter = filter

    def _serialize(self):
        return {"path": self.path, "query": self.filter.serialize()}


class IdsFilter(Filter):

    _internal_name = "ids"

    def __init__(self, values, type=None, **kwargs):
        super(IdsFilter, self).__init__(**kwargs)
        self.type = type
        self.values = values

    def _serialize(self):
        data = {}
        if self.type:
            data["type"] = self.type
        if isinstance(self.values, basestring):
            data["values"] = [self.values]
        else:
            data["values"] = self.values
        return data


class RawFilter(Filter):
    """Uses exactly the filter provided as an ES filter."""

    def __init__(self, filter_text_or_dict, **kwargs):
        super(RawFilter, self).__init__(**kwargs)
        if isinstance(filter_text_or_dict, basestring):
            self._filter = json.loads(filter_text_or_dict)
        else:
            self._filter = filter_text_or_dict

    def serialize(self):
        return self._filter
