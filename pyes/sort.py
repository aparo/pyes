# -*- coding: utf-8 -*-
from .exceptions import InvalidSortOrder
from .utils import EqualityComparableUsingAttributeDictionary


class SortOrder(EqualityComparableUsingAttributeDictionary):
    """
    Defines sort order
    """
    MODE_MIN = 'min'
    MODE_MAX = 'max'
    MODE_SUM = 'sum'  # not available for geo sorting
    MODE_AVG = 'avg'
    MODES = (MODE_MIN, MODE_MAX, MODE_SUM, MODE_AVG)

    def __init__(self, field=None, order=None, mode=None, nested_path=None,
                 nested_filter=None, missing=None, ignore_unmapped=None):
        self.field = field
        self.mode = mode
        self.order = order
        self.nested_path = nested_path
        self.nested_filter = nested_filter
        self.missing = missing
        self.ignore_unmapped = ignore_unmapped

    def serialize_order_params(self):
        res = {}
        if self.order:
            res['order'] = self.order
        if self.mode:
            res['mode'] = self.mode
        if self.nested_path:
            res['nested_path'] = self.nested_path
        if self.nested_filter:
            res['nested_filter'] = self.nested_filter.serialize()
        if self.missing:
            res['missing'] = self.missing
        if self.ignore_unmapped is not None:
            res['ignore_unmapped'] = self.ignore_unmapped

        return res

    def serialize(self):
        """Serialize the search to a structure as passed for a search body."""
        if not self.field:
            raise InvalidSortOrder('sort order must contain field name')

        return {self.field: self.serialize_order_params()}

    def __repr__(self):
        return str(self.serialize())


class GeoSortOrder(SortOrder):

    def __init__(self, lat=None, lon=None, geohash=None, unit=None,
                 **kwargs):
            super(GeoSortOrder, self).__init__(**kwargs)
            self.lat = lat
            self.lon = lon
            self.geohash = geohash
            self.unit = unit

    def serialize_order_params(self):
        res = super(GeoSortOrder, self).serialize_order_params()
        if self.geohash:
            res[self.field] = self.geohash
        elif self.lat is not None and self.lon is not None:
            res[self.field] = [self.lat, self.lon]
        else:
            raise InvalidSortOrder('Either geohash or lat and lon must be set')
        if self.unit:
            res['unit'] = self.unit

        return res

    def serialize(self):
        res = {
            '_geo_distance': self.serialize_order_params()
        }

        return res


class ScriptSortOrder(SortOrder):

    def __init__(self, script, type=None, params=None, **kwargs):
        super(ScriptSortOrder, self).__init__(**kwargs)
        self.script = script
        self.type = type
        self.params = params

    def serialize(self):
        res = {
            'script': self.script
        }
        if self.type:
            res['type'] = self.type
        if self.params:
            res['params'] = self.params
        if self.order:
            res['order'] = self.order

        res = {'_script': res}
        return res


class SortFactory(EqualityComparableUsingAttributeDictionary):
    """
    Container for SortOrder objects
    """

    def __init__(self):
        self.sort_orders = []

    def __bool__(self):
            return bool(self.sort_orders)

    def serialize(self):
        """Serialize the search to a structure as passed for a search body."""
        res = []
        for _sort in self.sort_orders:
            res.append(_sort.serialize())
        return res or None

    def __repr__(self):
        return str(self.serialize())

    def add(self, sort_order):
        """Add sort order"""
        self.sort_orders.append(sort_order)

    def reset(self):
        """Reset sort orders"""
        self.sort_orders = []
