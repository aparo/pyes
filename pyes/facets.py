# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .utils import EqualityComparableUsingAttributeDictionary
from .filters import Filter, TermFilter, TermsFilter, ANDFilter, NotFilter


class FacetFactory(EqualityComparableUsingAttributeDictionary):

    def __init__(self):
        self.facets = []

    def add_term_facet(self, *args, **kwargs):
        """Add a term factory facet"""
        self.facets.append(TermFacet(*args, **kwargs))

    def add_date_facet(self, *args, **kwargs):
        """Add a date factory facet"""
        self.facets.append(DateHistogramFacet(*args, **kwargs))

    def add_geo_facet(self, *args, **kwargs):
        """Add a geo factory facet"""
        self.facets.append(GeoDistanceFacet(*args, **kwargs))

    def add(self, facet):
        """Add a term factory"""
        self.facets.append(facet)

    def reset(self):
        """Reset the facets"""
        self.facets = []

    def serialize(self):
        res = {}
        for facet in self.facets:
            res.update(facet.serialize())
        return res


class Facet(EqualityComparableUsingAttributeDictionary):

    def __init__(self, name, scope=None, nested=None, is_global=None,
                 facet_filter=None, **kwargs):
        self.name = name
        self.scope = scope
        self.nested = nested
        self.is_global = is_global
        self.facet_filter = facet_filter

    def serialize(self):
        data = {self._internal_name: self._serialize()}
        if self.scope is not None:
            data["scope"] = self.scope
        if self.nested is not None:
            data["nested"] = self.nested
        if self.is_global:
            data['global'] = self.is_global
        if self.facet_filter:
            data['facet_filter'] = self.facet_filter.serialize()
        return {self.name: data}

    def _serialize(self):
        raise NotImplementedError

    @property
    def _internal_name(self):
        raise NotImplementedError


# TODO: remove these
FacetFilter = Filter
TermFacetFilter = TermFilter
TermsFacetFilter = TermsFilter
ANDFacetFilter = ANDFilter
NotFacetFilter = NotFilter


class QueryFacet(Facet):

    _internal_name = "query"

    def __init__(self, name, query, **kwargs):
        super(QueryFacet, self).__init__(name, **kwargs)
        self.query = query

    def _serialize(self):
        return self.query.serialize()


class FilterFacet(Facet):

    _internal_name = "filter"

    def __init__(self, name, filter, **kwargs):
        super(FilterFacet, self).__init__(name, **kwargs)
        self.filter = filter

    def _serialize(self):
        return self.filter.serialize()


class HistogramFacet(Facet):

    _internal_name = "histogram"

    def __init__(self, name, field=None, interval=None, time_interval=None,
                 key_field=None, value_field=None, key_script=None,
                 value_script=None, params=None, **kwargs):
        super(HistogramFacet, self).__init__(name, **kwargs)
        self.field = field
        self.interval = interval
        self.time_interval = time_interval
        self.key_field = key_field
        self.value_field = value_field
        self.key_script = key_script
        self.value_script = value_script
        self.params = params

    def _add_interval(self, data):
        if self.interval:
            data['interval'] = self.interval
        elif self.time_interval:
            data['time_interval'] = self.time_interval
        else:
            raise RuntimeError("Invalid field: interval or time_interval required")

    def _serialize(self):
        data = {}
        if self.field:
            data['field'] = self.field
            self._add_interval(data)
        elif self.key_field:
            data['key_field'] = self.key_field
            if self.value_field:
                data['value_field'] = self.value_field
            else:
                raise RuntimeError("Invalid key_field: value_field required")
            self._add_interval(data)
        elif self.key_script:
            data['key_script'] = self.key_script
            if self.value_script:
                data['value_script'] = self.value_script
            else:
                raise RuntimeError("Invalid key_script: value_script required")
            if self.params:
                data['params'] = self.params
            if self.interval:
                data['interval'] = self.interval
            elif self.time_interval:
                data['time_interval'] = self.time_interval
        return data


class DateHistogramFacet(Facet):

    _internal_name = "date_histogram"

    def __init__(self, name, field=None, interval=None, time_zone=None, pre_zone=None,
                 post_zone=None, factor=None, pre_offset=None, post_offset=None,
                 key_field=None, value_field=None, value_script=None, params=None, **kwargs):
        super(DateHistogramFacet, self).__init__(name, **kwargs)
        self.field = field
        self.interval = interval
        self.time_zone = time_zone
        self.pre_zone = pre_zone
        self.post_zone = post_zone
        self.factor = factor
        self.pre_offset = pre_offset
        self.post_offset = post_offset
        self.key_field = key_field
        self.value_field = value_field
        self.value_script = value_script
        self.params = params

    def _serialize(self):
        data = {}
        if self.interval:
            data['interval'] = self.interval
        else:
            raise RuntimeError("interval required")
        if self.time_zone:
            data['time_zone'] = self.time_zone
        if self.pre_zone:
            data['pre_zone'] = self.pre_zone
        if self.post_zone:
            data['post_zone'] = self.post_zone
        if self.factor:
            data['factor'] = self.factor
        if self.pre_offset:
            data['pre_offset'] = self.pre_offset
        if self.post_offset:
            data['post_offset'] = self.post_offset
        if self.field:
            data['field'] = self.field
        elif self.key_field:
            data['key_field'] = self.key_field
            if self.value_field:
                data['value_field'] = self.value_field
            elif self.value_script:
                data['value_script'] = self.value_script
                if self.params:
                    data['params'] = self.params
            else:
                raise RuntimeError("Invalid key_field: value_field or value_script required")
        return data


class RangeFacet(Facet):

    _internal_name = "range"

    def __init__(self, name, field=None, ranges=None, key_field=None, value_field=None,
                 key_script=None, value_script=None, params=None, **kwargs):
        super(RangeFacet, self).__init__(name, **kwargs)
        self.field = field
        self.ranges = ranges or []
        self.key_field = key_field
        self.value_field = value_field
        self.key_script = key_script
        self.value_script = value_script
        self.params = params

    def _serialize(self):
        data = {}
        if not self.ranges:
            raise RuntimeError("Invalid ranges")
        data['ranges'] = self.ranges
        if self.field:
            data['field'] = self.field
        elif self.key_field:
            data['key_field'] = self.key_field
            if self.value_field:
                data['value_field'] = self.value_field
            else:
                raise RuntimeError("Invalid key_field: value_field required")
        elif self.key_script:
            data['key_script'] = self.key_script
            if self.value_script:
                data['value_script'] = self.value_script
            else:
                raise RuntimeError("Invalid key_script: value_script required")
            if self.params:
                data['params'] = self.params
        return data


class GeoDistanceFacet(RangeFacet):

    _internal_name = "geo_distance"

    def __init__(self, name, field, pin, ranges=None, value_field=None,
                 value_script=None, distance_unit=None, distance_type=None,
                 params=None, **kwargs):
        super(RangeFacet, self).__init__(name, **kwargs)
        self.field = field
        self.pin = pin
        self.distance_unit = distance_unit
        self.distance_type = distance_type
        self.ranges = ranges or []
        self.value_field = value_field
        self.value_script = value_script
        self.params = params
        self.DISTANCE_TYPES = ['arc', 'plane']
        self.UNITS = ['km', 'mi', 'miles']

    def _serialize(self):
        if not self.ranges:
            raise RuntimeError("Invalid ranges")
        data = {}
        data['ranges'] = self.ranges
        data[self.field] = self.pin
        if self.distance_type:
            if self.distance_type not in self.DISTANCE_TYPES:
                raise RuntimeError("Invalid distance_type: must be one of %s" %
                    self.DISTANCE_TYPES)
            data['distance_type'] = self.distance_type
        if self.distance_unit:
            if self.distance_unit not in self.UNITS:
                raise RuntimeError("Invalid unit: must be one of %s" %
                    self.DISTANCE_TYPES)
            data['unit'] = self.distance_unit
        if self.value_field:
            data['value_field'] = self.value_field
        elif self.value_script:
            data['value_script'] = self.value_script
            if self.params:
                data['params'] = self.params
        return data


class StatisticalFacet(Facet):

    _internal_name = "statistical"

    def __init__(self, name, field=None, script=None, params=None, **kwargs):
        super(StatisticalFacet, self).__init__(name, **kwargs)
        self.field = field
        self.script = script
        self.params = params

    def _serialize(self):
        data = {}
        if self.field:
            data['field'] = self.field
        elif self.script:
            data['script'] = self.script
            if self.params:
                data['params'] = self.params
        return data


class TermFacet(Facet):

    _internal_name = "terms"

    def __init__(self, field=None, fields=None, name=None, size=10, order=None,
                 exclude=None, regex=None, regex_flags="DOTALL", script=None,
                 lang=None, all_terms=None, **kwargs):
        super(TermFacet, self).__init__(name or field, **kwargs)
        self.field = field
        self.fields = fields
        self.size = size
        self.order = order
        self.exclude = exclude or []
        self.regex = regex
        self.regex_flags = regex_flags
        self.script = script
        self.lang = lang
        self.all_terms = all_terms

    def _serialize(self):
        if not self.fields and not self.field and not self.script:
            raise RuntimeError("Field, Fields or Script is required:%s" % self.order)

        data = {}
        if self.fields:
            data['fields'] = self.fields
        elif self.field:
            data['field'] = self.field

        if self.script:
            data['script'] = self.script
            if self.lang:
                data['lang'] = self.lang
        if self.size is not None:
            data['size'] = self.size
        if self.order:
            if self.order not in ['count', 'term', 'reverse_count', 'reverse_term']:
                raise RuntimeError("Invalid order value:%s" % self.order)
            data['order'] = self.order
        if self.exclude:
            data['exclude'] = self.exclude
        if (self.fields or self.field) and self.regex:
            data['regex'] = self.regex
            if self.regex_flags:
                data['regex_flags'] = self.regex_flags
        if self.all_terms:
            data['all_terms'] = self.all_terms
        return data


class TermStatsFacet(Facet):

    _internal_name = "terms_stats"

    def __init__(self, name, size=10, order=None, key_field=None, value_field=None,
                 key_script=None, value_script=None, params=None, **kwargs):
        super(TermStatsFacet, self).__init__(name, **kwargs)
        self.size = size
        self.ORDER_VALUES = ['term', 'reverse_term', 'count', 'reverse_count',
                             'total', 'reverse_total', 'min', 'reverse_min',
                             'max', 'reverse_max', 'mean', 'reverse_mean']
        self.order = order if order is not None else self.ORDER_VALUES[0]
        self.key_field = key_field
        self.value_field = value_field
        self.key_script = key_script
        self.value_script = value_script
        self.params = params

    def _serialize(self):
        data = {}
        if self.size is not None:
            data['size'] = self.size
        if self.order:
            if self.order not in self.ORDER_VALUES:
                raise RuntimeError("Invalid order value:%s" % self.order)
            data['order'] = self.order

        if self.key_field:
            data['key_field'] = self.key_field
        else:
            raise RuntimeError("key_field required")

        if self.value_field:
            data['value_field'] = self.value_field
        elif self.value_script:
            data['value_script'] = self.value_script 
            if self.params:
                data['params'] = self.params
        else:
            raise RuntimeError("Invalid value: value_field OR value_script required")

        return data


class FacetQueryWrap(EqualityComparableUsingAttributeDictionary):

    def __init__(self, wrap_object, **kwargs):
        """Base Object for every Filter Object"""
        self.wrap_object = wrap_object

    def serialize(self):
        return {"query": self.wrap_object.serialize()}
