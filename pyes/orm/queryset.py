#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The main QuerySet implementation. This provides the public API for the ORM.
"""

import copy
from pyes.es import ResultSetList, EmptyResultSet, ResultSet
from pyes.filters import ANDFilter, ORFilter, NotFilter, Filter, TermsFilter, TermFilter, RangeFilter, ExistsFilter, RegexTermFilter, IdsFilter, PrefixFilter, MissingFilter
from pyes.facets import Facet, TermFacet, StatisticalFacet, HistogramFacet, DateHistogramFacet, TermStatsFacet
from pyes.query import MatchAllQuery, BoolQuery, FilteredQuery, Search
from pyes.utils import ESRange, make_id
from pyes.exceptions import NotFoundException
try:
    from django.db.models import Q
except ImportError:
    class Q:pass

import six
from pyes_engine import logger

from brainaetic.documental import get_model_from_str
import re
from django.utils.functional import SimpleLazyObject

REPR_OUTPUT_SIZE = 20

# Calculate the verbose_name by converting from InitialCaps to "lowercase with spaces".
get_verbose_name = lambda class_name: re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', ' \\1',
                                             class_name).lower().strip()
FIELD_SEPARATOR = "__"

from pyes.scriptfields import ScriptField
from pyes.exceptions import InvalidParameter


class QuerySet(object):
    """
    Represents a lazy database lookup for a set of objects.
    """

    def __init__(self, model=None, using=None, connection=None):
        #TODO: dfix
        self.model = model
        # EmptyQuerySet instantiates QuerySet with model as None
        self._using = using
        self._index = using
        self._size = 10
        self._type = None
        self._connection = connection
        self._queries = []
        self._filters = []
        self._facets = []
        self._ordering = []
        self._scan = None
        self._rescorer = None
        self._fields = [] #fields to load
        self._result_cache = None #hold the resultset
        if model:
            self._using = model._meta.using
            if connection:
                self._index = connection.database
            if model._meta.ordering:
                self._insert_ordering(self, *model._meta.ordering)

    def get_queryset(self):
        return self

    def using(self, using):
        self._using = using
        return self

    def scan(self, active=True):
        self._scan = active
        return self

    def _clear_ordering(self):
        #reset ordering
        self._ordering = []

    @property
    def type(self):
        if self._type:
            return self._type
        return self.model._meta.db_table

    def _next_is_sticky(self):
        return self

    def select_related(self, *fields, **kwargs):
        return self

        ########################

    # PYTHON MAGIC METHODS #
    ########################

    def __deepcopy__(self, memo):
        """
        Deep copy of a QuerySet doesn't populate the cache
        """
        obj = self.__class__()
        for k, v in self.__dict__.items():
            if k in ('_iter', '_result_cache'):
                obj.__dict__[k] = None
            else:
                obj.__dict__[k] = copy.deepcopy(v, memo)
        return obj

    def __getstate__(self):
        """
        Allows the QuerySet to be pickled.
        """
        # Force the cache to be fully populated.
        len(self)

        obj_dict = self.__dict__.copy()
        obj_dict['_iter'] = None
        return obj_dict

    def __repr__(self):
        data = list(self[:REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return repr(data)

    def _build_query(self):
        if not self._queries and not self._filters:
            return MatchAllQuery()
        query = MatchAllQuery()
        if self._queries:
            if len(self._queries) == 1:
                query = self._queries[0]
            else:
                query = BoolQuery(must=self._queries)
        if not self._filters:
            return query
        if len(self._filters) == 1:
            return FilteredQuery(query, self._filters[0])
        return FilteredQuery(query, ANDFilter(self._filters))

    def _build_search(self):
        query = Search(self._build_query(), version=True)

        if self._ordering:
            query.sort = self._ordering
        if self._facets:
            for facet in self._facets:
                query.facet.add(facet)
        if self._size==0:
            query.size=0
        if self._rescorer:
            query.rescore=self._rescorer

        return query

    def _build_model(self, m, record):
        from django.db import models

        data = record["_source"]
        data["id"] = record["_id"]
        fields = self.model._meta.fields
        for field in fields:
            if field.attname not in data:
                continue

            if isinstance(field, models.ListField):
                model = field.item_field.model
                if isinstance(model, six.string_types):
                    model = get_model_from_str(model)
                if isinstance(field.item_field, models.ForeignKey):
                    #data[field.attname] = ModelIteratorResolver(field.item_field.model, data[field.attname])
                    if data[field.attname]:
                        data[field.attname] = [model.objects.get(pk=id) for id in data[field.attname]]
                    else:
                        data[field.attname] = []
            elif isinstance(field, models.SetField):
                model = field.item_field.model
                if isinstance(model, six.string_types):
                    model = get_model_from_str(model)
                if isinstance(field.item_field, models.ForeignKey):
                    if data[field.attname]:
                    #data[field.attname] = ModelIteratorResolver(field.item_field.model, data[field.attname])
                        data[field.attname] = set([model.objects.get(pk=id) for id in data[field.attname]])
                    else:
                        data[field.attname] = []
                else:
                    data[field.attname] = set(data[field.attname])
        value = self.model(**data)
        setattr(value, "_index", record["_index"])
        setattr(value, "_type", record["_type"])

        if "_score" in record:
            setattr(value, "_score", record["_score"])
        if "sort" in record:
            setattr(value, "_sort", record["sort"])
        return value

    def _is_valid_scan(self):
        """
        Detect if a type
        :return: a boolean
        """
        if self._scan is not None:
            return self._scan
        if self._ordering:
            return False
        if self._facets:
            return False
            #TODO check for child or nested query
        return True

    def _do_query(self):
        connection = self.model._meta.dj_connection
        index = self.get_index(connection)
        from pyes.es import ES

        if not isinstance(connection.connection, ES):
            print("Strange connection object", connection)
            #refresh data
        if connection._dirty:
            connection.connection.refresh(indices=index)
            connection._dirty = False

        #check ids
        if not self._facets and not self._queries and len(self._filters) == 1 and isinstance(self._filters[0],
                                                                                             IdsFilter):
            filter = self._filters[0]
            if len(filter.values) == 1:
                try:
                    return ResultSetList(items=[
                        connection.connection.get(index, self.type, str(filter.values[0]),
                                                  model=self._build_model)],
                                         model=self._build_model)
                except NotFoundException:
                    return EmptyResultSet()

        search = self._build_search()
        # if isinstance(search.query, FilteredQuery) and isinstance(search.query.query, MatchAllQuery) and \
        #     isinstance(search.query.filter, IdsFilter) and len(search.query.filter.values) == 1:
        #     results = [connection.connection.get(index, self.type,search.query.filter.values[0], model=self._build_model)]
        #     #iterator

        # show query
        scan = self._is_valid_scan()
        if scan:
            search.sort = {}
        #print "scan?", scan, index, self.type, search.serialize()
        return connection.connection.search(search, indices=index, doc_types=self.type,
                                            model=self._build_model, scan=scan)


    def __len__(self):
        # Since __len__ is called quite frequently (for example, as part of
        # list(qs), we make some effort here to be as efficient as possible
        # whilst not messing up any existing iterators against the QuerySet.
        if self._result_cache is None:
            self._result_cache = self._do_query()
        return self._result_cache.total

    def __iter__(self):
        if self._result_cache is None:
            len(self)
            # Python's list iterator is better than our version when we're just
        # iterating over the cache.
        return iter(self._result_cache)

    def __bool__(self):
        return self.__nonzero__()

    def __nonzero__(self):
        if self._result_cache is not None:
            len(self)
            return bool(self._result_cache.total != 0)
        try:
            next(iter(self))
        except StopIteration:
            return False
        return True

    #    def __contains__(self, val):
    #        # The 'in' operator works without this method, due to __iter__. This
    #        # implementation exists only to shortcut the creation of Model
    #        # instances, by bailing out early if we find a matching element.
    #        pos = 0
    #        if self._result_cache is not None:
    #            if val in self._result_cache:
    #                return True
    #            elif self._iter is None:
    #                # iterator is exhausted, so we have our answer
    #                return False
    #            # remember not to check these again:
    #            pos = len(self._result_cache)
    #        else:
    #            # We need to start filling the result cache out. The following
    #            # ensures that self._iter is not None and self._result_cache is not
    #            # None
    #            it = iter(self)
    #
    #        # Carry on, one result at a time.
    #        while True:
    #            if len(self._result_cache) <= pos:
    #                self._fill_cache(num=1)
    #            if self._iter is None:
    #                # we ran out of items
    #                return False
    #            if self._result_cache[pos] == val:
    #                return True
    #            pos += 1

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, (slice,) + six.integer_types):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0))
                or (isinstance(k, slice) and (k.start is None or k.start >= 0)
                    and (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        if self._result_cache is None:
            len(self)
        return self._result_cache.__getitem__(k)

    def __and__(self, other):
        combined = self._clone()
        if not other._filters:
            return combined
        if other._filters:
            combined._filters.extend(other._filters)
        return combined

    def __or__(self, other):
        combined = self._clone()
        if not other._filters:
            return other._clone()
        combined._filters = ORFilter([combined._filters, other._filters])
        return combined

    ####################################
    # METHODS THAT DO DATABASE QUERIES #
    ####################################

    def iterator(self):
        """
        An iterator over the results from applying this QuerySet to the
        database.
        """
        if not self._result_cache:
            len(self)
        for r in self._result_cache:
            yield r

    def aggregate(self, *args, **kwargs):
        """
        Returns a dictionary containing the calculations (aggregation)
        over the current queryset

        If args is present the expression is passed as a kwarg using
        the Aggregate object's default alias.
        """
        obj = self._clone()
        obj._facets = [] #reset facets
        from django.db.models import Avg, Max, Min

        for arg in args:
            if isinstance(arg, (Avg, Max, Min)):

                field, djfield = self._django_to_es_field(arg.lookup)
                if not djfield:
                    obj = obj.annotate(field)
                from pyes.facets import StatisticalFacet

                obj = obj.annotate(StatisticalFacet(field, field))
        facets = obj.get_facets()
        #collecting results
        result = {}
        for name, values in facets.items():
            for k, v in values.items():
                if k.startswith("_"):
                    continue
                result[u'%s__%s' % (name, k)] = v

        return result

    def count(self):
        """
        Performs a SELECT COUNT() and returns the number of records as an
        integer.

        If the QuerySet is already fully cached this simply returns the length
        of the cached results set to avoid multiple SELECT COUNT(*) calls.
        """
        return len(self)

    def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        clone = self.filter(*args, **kwargs)
        num = len(clone)
        if num == 1:
            return clone._result_cache[0]
        if not num:
            raise self.model.DoesNotExist(
                "%s matching query does not exist. "
                "Lookup parameters were %s" %
                #(self.model._meta.object_name, kwargs))
                (self.model.__class__.__name__, kwargs))
        raise self.model.MultipleObjectsReturned(
            "get() returned more than one %s -- it returned %s! "
            "Lookup parameters were %s" %
            #(self.model._meta.object_name, num, kwargs))
            (self.model.__class__.__name__, num, kwargs))

    def create(self, **kwargs):
        """
        Creates a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        obj = self.model(**kwargs)
        obj.save(force_insert=True, using=self._using)
        return obj

    def bulk_create(self, objs, batch_size=None):
        """
        Inserts each of the instances into the database. This does *not* call
        save() on each of the instances, does not send any pre/post save
        signals, and does not set the primary key attribute if it is an
        autoincrement field.
        """
        self._insert(objs, batch_size=batch_size, return_id=False, force_insert=True)
        self.refresh()

    def get_or_create(self, **kwargs):
        """
        Looks up an object with the given kwargs, creating one if necessary.
        Returns a tuple of (object, created), where created is a boolean
        specifying whether an object was created.
        """
        assert kwargs, \
            'get_or_create() must be passed at least one keyword argument'
        defaults = kwargs.pop('defaults', {})
        lookup = kwargs.copy()
        #TODO: check fields
        try:
            return self.get(**lookup), False
        except self.model.DoesNotExist:
            params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
            params.update(defaults)
            obj = self.model(**params)
            obj.save(force_insert=True)
            return obj, True

    def latest(self, field_name=None):
        """
        Returns the latest object, according to the model's 'get_latest_by'
        option or optional given field_name.
        """
        latest_by = field_name or "_id"#self.model._meta.get_latest_by
        assert bool(latest_by), "latest() requires either a field_name parameter or 'get_latest_by' in the model"
        obj = self._clone()
        obj.size = 1
        obj._clear_ordering()
        obj._ordering.append({latest_by: "desc"})
        return obj.get()

    def in_bulk(self, id_list):
        """
        Returns a dictionary mapping each of the given IDs to the object with
        that ID.
        """
        if not id_list:
            return {}
        qs = self._clone()
        qs.add_filter(('pk__in', id_list))
        qs._clear_ordering(force_empty=True)
        return dict([(obj._get_pk_val(), obj) for obj in qs])

    def delete(self):
        """
        Deletes the records in the current QuerySet.
        """
        del_query = self._clone()

        # The delete is actually 2 queries - one to find related objects,
        # and one to delete. Make sure that the discovery of related
        # objects is performed on the same database as the deletion.
        del_query._clear_ordering()
        connection = self.model._meta.dj_connection

        connection.connection.delete_by_query(indices=connection.database, doc_types=self.model._meta.db_table,
                                              query=del_query._build_query())
        connection.connection.indices.refresh(indices=connection.database)
        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None

    def update(self, *args, **kwargs):
        """
        Updates all elements in the current QuerySet, setting all the given
        fields to the appropriate values.
        """
        if args:
            for arg in args:
                if not isinstance(arg, ScriptField):
                    raise InvalidParameter("%s this must be a ScriptField or derivated" % arg)

        query = self._build_query()
        connection = self.model._meta.dj_connection
        query.fields = ["_id", "_type", "_index"]
        # results = connection.connection.search(query, indices=connection.database, doc_types=self.type,
        #                             model=self.model, scan=True)

        conn = connection.connection
        results = conn.search(query, indices=connection.database, doc_types=self.type, scan=True)

        for item in results:
            if kwargs:
                conn.update(item._meta.index, item._meta.type, item._meta.id, document=kwargs, bulk=True)
            for script in args:
                conn.update(item._meta.index, item._meta.type, item._meta.id,
                            script=script.script, lang=script.lang, params=script.params, bulk=True)

        connection.connection.flush_bulk(True)
        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None

    def exists(self):
        if self._result_cache is None:
            len(self)
        return bool(self._result_cache.total != 0)

    ##################################################
    # PUBLIC METHODS THAT RETURN A QUERYSET SUBCLASS #
    ##################################################

    def _django_to_es_field(self, field):
        """We use this function in value_list and ordering to get the correct fields name"""
        from django.db import models

        prefix = ""
        if field.startswith("-"):
            prefix = "-"
            field = field.lstrip("-")

        if field in ["id", "pk"]:
            return "_id", models.AutoField

        try:
            dj_field, _, _, _ = self.model._meta.get_field_by_name(field)
            if isinstance(dj_field, models.ForeignKey):
                return prefix + field + "_id", models.ForeignKey
            else:
                return prefix + field, dj_field
        except models.FieldDoesNotExist:
            pass

        return prefix + field.replace(FIELD_SEPARATOR, "."), None


    def _django_to_es_fields(self, dj_fields):
        """We use this function in value_list and ordering to get the correct fields name"""
        return [self._django_to_es_field(field)[0] for field in dj_fields]

    def _cooked_fields(self, dj_fields):
        """
        Returns a tuple of cooked fields
        :param dj_fields: a list of django name fields
        :return:
        """
        from django.db import models

        valids = []
        for field in dj_fields:
            try:
                dj_field, _, _, _ = self.model._meta.get_field_by_name(field)
                if isinstance(dj_field, models.ForeignKey):
                    valids.append((field + "_id", field, dj_field))
                else:
                    valids.append((field, field, dj_field))
            except models.FieldDoesNotExist:
                valids.append((field, field, None))
        return valids


    def values(self, *fields):
        assert fields, "A least a field is required"
        search = self._build_search()
        search.facet.reset()
        search.fields = self._django_to_es_fields(fields)
        connection = self.model._meta.dj_connection

        return connection.connection.search(search, indices=connection.database, doc_types=self.type)

    def values_list(self, *fields, **kwargs):
        flat = kwargs.pop('flat', False)
        if kwargs:
            raise TypeError('Unexpected keyword arguments to values_list: %s'
                            % (kwargs.keys(),))
        if flat and len(fields) > 1:
            raise TypeError("'flat' is not valid when values_list is called with more than one field.")
        assert fields, "A least a field is required"
        search = self._build_search()
        search.facet.reset()
        search.fields = self._django_to_es_fields(fields)
        connection = self.model._meta.dj_connection

        values_resolver = ValueListResolver(self.model, self._cooked_fields(fields), flat)
        return connection.connection.search(search, indices=connection.database, doc_types=self.type,
                                            model=values_resolver)

    def dates(self, field_name, kind, order='ASC'):
        """
        Returns a list of datetime objects representing all available dates for
        the given field_name, scoped to 'kind'.
        """

        assert kind in ("month", "year", "day", "week", "hour", "minute"), \
            "'kind' must be one of 'year', 'month', 'day', 'week', 'hour' and 'minute'."
        assert order in ('ASC', 'DESC'), \
            "'order' must be either 'ASC' or 'DESC'."

        search = self._build_search()
        search.facet.reset()
        search.facet.add_date_facet(name=field_name.replace("__", "."),
                                    field=field_name, interval=kind)
        search.size = 0
        connection = self.model._meta.dj_connection

        resulset = connection.connection.search(search, indices=connection.database, doc_types=self.type)
        resulset.fix_facets()
        entries = []
        for val in resulset.facets.get(field_name.replace("__", ".")).get("entries", []):
            if "time" in val:
                entries.append(val["time"])
        if order == "ASC":
            return sorted(entries)

        return sorted(entries, reverse=True)

    def none(self):
        """
        Returns an empty QuerySet.
        """
        return EmptyQuerySet(model=self.model, using=self._using, connection=self._connection)


    ##################################################################
    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
    ##################################################################

    def all(self):
        """
        Returns a new QuerySet that is a copy of the current one. This allows a
        QuerySet to proxy for a model manager in some cases.
        """
        return self._clone()

    def query(self, *args, **kwargs):
        """
        Returns a new QuerySet instance with the args ANDed to the existing
        set.
        """
        clone = self._clone()
        queries = []
        from pyes.query import Query

        if args:
            for f in args:
                if isinstance(f, Query):
                    queries.append(f)
                else:
                    raise TypeError('Only Query objects can be passed as argument')

        for field, value in kwargs.items():
            if value == [None]:
                value = ["$$$$"]
            queries.append(self._build_inner_query(field, value))

        clone._queries.extend(queries)
        return clone

    def rescorer(self, rescorer):
        """
        Returns a new QuerySet with a set rescorer.
        """
        clone = self._clone()
        clone._rescorer=rescorer
        return clone

    def filter(self, *args, **kwargs):
        """
        Returns a new QuerySet instance with the args ANDed to the existing
        set.
        """
        return self._filter_or_exclude(False, *args, **kwargs)

    def exclude(self, *args, **kwargs):
        """
        Returns a new QuerySet instance with NOT (args) ANDed to the existing
        set.
        """
        return self._filter_or_exclude(True, *args, **kwargs)


    def _filter_or_exclude(self, negate, *args, **kwargs):
        clone = self._clone()
        filters = self._build_filter(*args, **kwargs)

        if negate:
            if len(filters) > 1:
                filters = ANDFilter(filters)
            else:
                filters = filters[0]
            clone._filters.append(NotFilter(filters))
        else:
            clone._filters.extend(filters)
        return clone

    FILTER_OPERATORS = {
        'exact': '',
        'iexact': "",
        'contains': "",
        'icontains': "",
        'regex': '',
        'iregex': "",
        'gt': '',
        'gte': '',
        'lt': '',
        'lte': '',
        'startswith': "",
        'endswith': "",
        'istartswith': "",
        'iendswith': "",
        'in': "",
        'ne': "",
        'isnull': "",
        'ismissing': "",
        'exists': "",
        'year': "",
        'prefix': "",
        'match': "",
    }

    def _get_filter_modifier(self, field):
        """Detect the filter modifier"""
        tokens = field.split(FIELD_SEPARATOR)
        if len(tokens) == 1:
            return field, ""
        if tokens[-1] in self.FILTER_OPERATORS.keys():
            return u'.'.join(tokens[:-1]), tokens[-1]
        return u'.'.join(tokens), ""

    def _prepare_value(self, value, dj_field=None):
        """Cook the value"""
        from django.db import models

        if isinstance(value, (six.string_types, int, float)):
            return value
        elif isinstance(value, SimpleLazyObject):
            return value.pk
        elif isinstance(value, models.Model):
            if dj_field:
                if isinstance(dj_field, models.ForeignKey):
                    return value.pk
                    #TODO validate other types
            return value
        elif isinstance(value, (ResultSet, EmptyQuerySet, EmptyResultSet, list)):
            return [self._prepare_value(v, dj_field=dj_field) for v in value]
        elif isinstance(value, QuerySet):
            value = value._clone()
            return [self._prepare_value(v, dj_field=dj_field) for v in value]
        return value

    def _build_inner_filter(self, field, value):
        from django.db import models


        field, modifier = self._get_filter_modifier(field)
        dj_field = None
        try:
            dj_field, _, _, _ = self.model._meta.get_field_by_name(field)
            if isinstance(dj_field, models.ForeignKey):
                field += "_id"
                if isinstance(value, models.Model):
                    if not value.pk:
                        value.save()
                    value = value.pk
            if dj_field:
                if isinstance(dj_field, models.ForeignKey) and modifier == "id":
                    field += "_id"
                    modifier = ""
                elif isinstance(dj_field, models.ListField) and isinstance(dj_field.item_field, models.ForeignKey):
                    dj_field = dj_field.item_field

        except models.FieldDoesNotExist:
            pass

        #calculating lazy resultset
        value = self._prepare_value(value, dj_field=dj_field)

        pk_column = self.model._meta.pk.column
        #case filter id
        if modifier in ["", "in"] and field in ["pk", pk_column]:
            if isinstance(value, list):
                return IdsFilter(value)
            return IdsFilter([value])

        if not modifier:
            if isinstance(value, list):
                return TermsFilter(field, value)
            return TermFilter(field, value)

        if modifier == "in":
            return TermsFilter(field, value)
        elif modifier == "gt":
            return RangeFilter(ESRange(field, from_value=value, include_lower=False))
        elif modifier == "gte":
            return RangeFilter(ESRange(field, from_value=value, include_lower=True))
        elif modifier == "lte":
            return RangeFilter(ESRange(field, to_value=value, include_upper=True))
        elif modifier == "lt":
            return RangeFilter(ESRange(field, to_value=value, include_upper=False))
        elif modifier == "in":
            return TermsFilter(field, values=value)
        elif modifier == "ne":
            return NotFilter(TermFilter(field, value))
        elif modifier == "exists":
            if isinstance(value, bool) and value:
                return ExistsFilter(field)
            return NotFilter(ExistsFilter(field))
        elif modifier in ["startswith", "istartswith"]:
            return RegexTermFilter(field, "^" + value + ".*",
                                   ignorecase=modifier == "istartswith")
        elif modifier in ["endswith", "iendswith"]:
            return RegexTermFilter(field, ".*" + value + "$",
                                   ignorecase=modifier == "iendswith")
        elif modifier in ["contains", "icontains"]:
            return RegexTermFilter(field, ".*" + value + ".*",
                                   ignorecase=modifier == "icontains")
        elif modifier in ["regex", "iregex"]:
            return RegexTermFilter(field, value,
                                   ignorecase=modifier == "iregex")
        elif modifier == "prefix":
            return PrefixFilter(field, value)

        elif modifier in ["exact", "iexact"]:
            return TermFilter(field, value)
        elif modifier == "year":
            if isinstance(value, list):
                return RangeFilter(ESRange(field, value[0], value[1], True, True))
            if isinstance(value, tuple):
                return RangeFilter(ESRange(field, value[0], value[1], True, True))
            else:
                import datetime
                from dateutil.relativedelta import relativedelta

                start = datetime.datetime(value, 1, 1)
                end = start + relativedelta(years=1)
                return RangeFilter(ESRange(field, start, end, True, False))
        elif modifier in ["isnull"]:
            if value:
                return MissingFilter(field)
            return ExistsFilter(field)

        raise NotImplementedError()

    def _build_inner_query(self, field, value):
        from django.db import models
        from pyes.query import IdsQuery, TermQuery, TermsQuery, RangeQuery, RegexTermQuery, PrefixQuery, MatchQuery

        field, modifier = self._get_filter_modifier(field)
        dj_field = None
        try:
            dj_field, _, _, _ = self.model._meta.get_field_by_name(field)
            if isinstance(dj_field, models.ForeignKey):
                field += "_id"
                if isinstance(value, models.Model):
                    if not value.pk:
                        value.save()
                    value = value.pk
            if dj_field:
                if isinstance(dj_field, models.ForeignKey) and modifier == "id":
                    field += "_id"
                    modifier = ""
                elif isinstance(dj_field, models.ListField) and isinstance(dj_field.item_field, models.ForeignKey):
                    dj_field = dj_field.item_field

        except models.FieldDoesNotExist:
            pass

        #calculating lazy resultset
        value = self._prepare_value(value, dj_field=dj_field)

        pk_column = self.model._meta.pk.column
        #case filter id
        if modifier in ["", "in"] and field in ["pk", pk_column]:
            if isinstance(value, list):
                return IdsQuery(value)
            return IdsQuery([value])

        if not modifier:
            if isinstance(value, list):
                return TermsQuery(field, value)
            return TermQuery(field, value)

        if modifier == "in":
            return TermsQuery(field, value)
        elif modifier == "gt":
            return RangeQuery(ESRange(field, from_value=value, include_lower=False))
        elif modifier == "gte":
            return RangeQuery(ESRange(field, from_value=value, include_lower=True))
        elif modifier == "lte":
            return RangeQuery(ESRange(field, to_value=value, include_upper=True))
        elif modifier == "lt":
            return RangeQuery(ESRange(field, to_value=value, include_upper=False))
        elif modifier == "in":
            return TermsQuery(field, values=value)
        elif modifier in ["startswith", "istartswith"]:
            return RegexTermQuery(field, "^" + value + ".*",
                                  ignorecase=modifier == "istartswith")
        elif modifier in ["endswith", "iendswith"]:
            return RegexTermQuery(field, ".*" + value + "$",
                                  ignorecase=modifier == "iendswith")
        elif modifier in ["contains", "icontains"]:
            return RegexTermQuery(field, ".*" + value + ".*",
                                  ignorecase=modifier == "icontains")
        elif modifier in ["regex", "iregex"]:
            return RegexTermQuery(field, value,
                                  ignorecase=modifier == "iregex")
        elif modifier == "prefix":
            return PrefixQuery(field, value)

        elif modifier in ["exact", "iexact"]:
            return TermQuery(field, value)
        elif modifier == "year":
            if isinstance(value, list):
                return RangeQuery(ESRange(field, value[0], value[1], True, True))
            if isinstance(value, tuple):
                return RangeQuery(ESRange(field, value[0], value[1], True, True))
            else:
                import datetime
                from dateutil.relativedelta import relativedelta

                start = datetime.datetime(value, 1, 1)
                end = start + relativedelta(years=1)
                return RangeQuery(ESRange(field, start, end, True, False))
        elif modifier in ["match"]:
            return MatchQuery(field, value)
        raise NotImplementedError()

    def _Q_to_filter(self, q):
        """
        Convert a Q object to filter
        :param q: a Q Object
        :return: a filter object
        """
        default_filter = ANDFilter
        if q.connector == "OR":
            default_filter = ORFilter
        filters = []
        for child in q.children:
            if isinstance(child, Q):
                if child.children:
                    filters.append(self._Q_to_filter(child))
            elif isinstance(child, tuple):
                field, value = child
                filters.append(self._build_inner_filter(field, value))
        if len(filters) == 1:
            filter = filters[0]
            if q.negated:
                return NotFilter(filter)
            return filter
        if q.negated:
            return NotFilter(default_filter(filters))
        return default_filter(filters)


    def _build_filter(self, *args, **kwargs):
        filters = []

        if args:
            for f in args:
                if isinstance(f, Filter):
                    filters.append(f)
                    #elif isinstance(f, dict):
                    #TODO: dict parser
                elif isinstance(f, Q):
                    filters.append(self._Q_to_filter(f))
                else:
                    raise TypeError('Only Filter objects can be passed as argument')

        for field, value in kwargs.items():
            if value == [None]:
                value = ["$$$$"]
                # if FIELD_SEPARATOR in field:
            #     if field.rsplit(FIELD_SEPARATOR, 1)[1] == 'isnull' and value == False:
            #         return filters
            filters.append(self._build_inner_filter(field, value))
        return filters

    def connection(self, connection):
        self._connection = connection
        return self

    def complex_filter(self, filter_obj):
        """
        Returns a new QuerySet instance with filter_obj added to the filters.

        filter_obj can be a Q object (or anything with an add_to_query()
        method) or a dictionary of keyword lookup arguments.

        This exists to support framework features such as 'limit_choices_to',
        and usually it will be more natural to use other methods.
        """
        if isinstance(filter_obj, Filter):
            clone = self._clone()
            clone._filters.add(filter_obj)
            return clone
        return self._filter_or_exclude(None, **filter_obj)


    def facet(self, *args, **kwargs):
        return self.annotate(*args, **kwargs)

    def annotate(self, *args, **kwargs):
        """
        Return a query set in which the returned objects have been annotated
        with data aggregated from related fields.
        """
        obj = self._clone()
        if args:
            for arg in args:
                if isinstance(arg, Facet):
                    obj._facets.append(arg)
                elif isinstance(arg, six.string_types):
                    modifier = "term"
                    tokens = arg.split("__")
                    if len(tokens)>1 and tokens[-1] in ["term", "stat", "histo", "date"]:
                        modifier=tokens[-1]
                        tokens=tokens[:-1]
                    field, djfield = self._django_to_es_field("__".join(tokens))
                    if modifier=="term":
                        obj._facets.append(TermFacet(name=arg, field=field, **kwargs))
                    elif modifier=="term_stat":
                        obj._facets.append(TermStatsFacet(name=arg, **kwargs))
                    elif modifier=="stat":
                        obj._facets.append(StatisticalFacet(name=arg, field=field, **kwargs))
                    elif modifier=="histo":
                        obj._facets.append(HistogramFacet(name=arg, field=field, **kwargs))
                    elif modifier=="date":
                        obj._facets.append(DateHistogramFacet(name=arg, field=field, **kwargs))
                else:
                    raise NotImplementedError("invalid type")
        else:
            # Add the aggregates/facet to the query
            for name, field in kwargs.items():
                obj._facets.append(
                    TermFacet(field=field.replace(FIELD_SEPARATOR, "."), name=name.replace(FIELD_SEPARATOR, ".")))

        return obj

    def order_by(self, *field_names):
        """
        Returns a new QuerySet instance with the ordering changed.
        We have a special field "_random"
        """
        obj = self._clone()
        obj._clear_ordering()
        self._insert_ordering(obj, *field_names)
        return obj


    def _insert_ordering(self, obj, *field_names):

        for field in field_names:
            if isinstance(field, dict):
                obj._clear_ordering()
                obj._ordering.append(field)
            elif field == "_random":
                obj._clear_ordering()
                obj._ordering.append({
                    "_script": {
                        "script": "Math.random()",
                        "type": "number",
                        "params": {},
                        "order": "asc"
                    }
                })
                break
            elif field.startswith("-"):
                obj._ordering.append({field.lstrip("-"): {"order": "desc", "ignore_unmapped": True}})
            else:
                obj._ordering.append({field: {"order": "asc", "ignore_unmapped": True}})
        return obj


    def distinct(self, *field_names):
        """
        Returns a new QuerySet instance that will select only distinct results.
        """
        return self


    def reverse(self):
        """
        Reverses the ordering of the QuerySet.
        """
        clone = self._clone()
        assert self._ordering, "You need to set an ordering for reverse"
        ordering = []
        for order in self._ordering:
            for k, v in order.items():
                if v == "asc":
                    ordering.append({k: "desc"})
                else:
                    ordering.append({k: "asc"})
        clone._ordering = ordering
        return clone

    def defer(self, *fields):
        """
        Defers the loading of data for certain fields until they are accessed.
        The set of fields to defer is added to any existing set of deferred
        fields. The only exception to this is if None is passed in as the only
        parameter, in which case all deferrals are removed (None acts as a
        reset option).
        """
        raise NotImplementedError()

    #        clone = self._clone()
    #        if fields == (None,):
    #            clone.query.clear_deferred_loading()
    #        else:
    #            clone.query.add_deferred_loading(fields)
    #        return clone

    def only(self, *fields):
        """
        Essentially, the opposite of defer. Only the fields passed into this
        method and that are not already specified as deferred are loaded
        immediately when the queryset is evaluated.
        """
        clone = self._clone()
        clone._fields = fields
        return clone

    def index(self, alias):
        """
        Selects which database this QuerySet should execute its query against.
        """
        clone = self._clone()
        clone._index = alias
        return clone

    def size(self, size):
        """
        Set the query size of  this QuerySet should execute its query against.
        """
        clone = self._clone()
        clone._size = size
        return clone

    ###################################
    # PUBLIC INTROSPECTION ATTRIBUTES #
    ###################################

    def ordered(self):
        """
        Returns True if the QuerySet is ordered -- i.e. has an order_by()
        clause or a default ordering on the model.
        """
        return len(self._ordering) > 0

    ordered = property(ordered)


    ###################
    # PUBLIC METHODS  #
    ###################

    @classmethod
    def from_qs(cls, qs, **kwargs):
        """
        Creates a new queryset using class `cls` using `qs'` data.

        :param qs: The query set to clone
        :keyword kwargs: The kwargs to pass to _clone method
        """
        assert issubclass(cls, QuerySet), "%s is not a QuerySet subclass" % cls
        assert isinstance(qs, QuerySet), "qs has to be an instance of queryset"
        return qs._clone(klass=cls, **kwargs)

    def evaluated(self):
        """
        Lets check if the queryset was already evaluated without accessing
        private methods / attributes
        """
        return not self._result_cache is None

    ###################
    # PRIVATE METHODS #
    ###################
    def _batched_insert(self, objs, fields, batch_size):
        """
        A little helper method for bulk_insert to insert the bulk one batch
        at a time. Inserts recursively a batch from the front of the bulk and
        then _batched_insert() the remaining objects again.
        """
        raise NotImplementedError()

    #        if not objs:
    #            return
    #        ops = connections[self.db].ops
    #        batch_size = (batch_size or max(ops.bulk_batch_size(fields, objs), 1))
    #        for batch in [objs[i:i+batch_size]
    #                      for i in range(0, len(objs), batch_size)]:
    #            self.model._base_manager._insert(batch, fields=fields,
    #                                             using=self.db)

    def _get_hash_id(self, record, uniq_together):
        valid_fields = []
        if isinstance(uniq_together, six.string_types):
            valid_fields.append(uniq_together)
        elif isinstance(uniq_together, (list, tuple)):
            for v in uniq_together:
                if isinstance(v, six.string_types):
                    valid_fields.append(v)
                else:
                    valid_fields.extend(list(v))
        if not valid_fields:
            return None

        values = []
        for f in valid_fields:
            val = record.get(f, u"")
            if val:
                values.append(unicode(val))
        if not values:
            return None

        return make_id("_".join(values).strip().lower())

    def _insert(self, objs, fields=None, **kwargs):

        single = False
        using = kwargs.get("using")
        if not isinstance(objs, list):
            single = True
            objs = [objs]
        if len(objs) == 1:
            single = True

        #get fields
        if not fields:
            fields = self.model._meta.concrete_fields

        connection = self.model._meta.dj_connection

        if using and using not in ["default", "echidnasearch"]:
            database = using
        else:
            database=connection.database

        meta = self.model._meta

        db_table = meta.db_table
        bulk = not kwargs.get("return_id", False)
        force_insert = kwargs.get("force_insert", False)
        pk_column = meta.pk.column
        unique_together_name = []
        valid_fields = []
        if isinstance(meta.unique_together, six.string_types):
            valid_fields.append(meta.uniq_together)
        elif isinstance(meta.unique_together, (list, tuple)):
            for v in meta.unique_together:
                if isinstance(v, six.string_types):
                    valid_fields.append(v)
                else:
                    valid_fields.extend(list(v))
                    # for field in fields:
                    #     if field.name in valid_fields:
                    #         unique_together_name.append(field.attname)

        ids = []
        for obj in objs:
            record = obj.to_dict(fields, **kwargs)
            pk = record.get(pk_column, None)
            record.pop("_id", None)
            #remove empty values
            if pk is None:
                # pk = self._get_hash_id(record, meta.unique_together)
                pk = obj.calc_pk()

            res = connection.connection.index(record, index=database, doc_type=db_table, id=pk, bulk=bulk,
                                              force_insert=force_insert)
            if not bulk:
                ids.append(res._id)
        if connection.force_refresh:
            connection.connection.refresh()
        else:
            connection._dirty = True
        if bulk:
            return []
        if single:
            return ids[0]
        return ids

    _insert.queryset_only = False

    def _clone(self, klass=None, setup=False, **kwargs):
        params = dict(model=self.model, using=self.index)
        if klass is None:
            klass = self.__class__
        if repr(klass) == "<class 'django.db.models.fields.related.RelatedManager'>":
            params["instance"] = getattr(self, "instance", None)# only for RelatedManager
        c = klass(**params)
        #copy filters/queries/facet????
        c.__dict__.update(kwargs)
        c._queries = list(self._queries)
        c._filters = list(self._filters)
        c._facets = list(self._facets)
        c._fields = list(self._fields)
        c._ordering = list(self._ordering)
        c._size = self._size
        c._scan = self._scan
        c._rescorer = self._rescorer
        c._connection = self._connection
        c._using = self._using
        return c

    # When used as part of a nested query, a queryset will never be an "always
    # empty" result.
    value_annotation = True

    def get_facets(self):
        len(self)
        if isinstance(self._result_cache, ResultSetList):
            self._result_cache = None
            len(self)
        self._result_cache.fix_facets()
        return FacetHelper(self.model, self._result_cache.facets)

    #converting functions
    #TODO: remove
    def convert_value_for_db(self, db_type, value):
        if db_type == "unicode" and not isinstance(value, six.string_types):
            return unicode(value)
        return value

    #def _build_objects(self, objs, fields=None, raw=False, **kwargs):
    #    from django.db import connections
    #
    #    connection = connections[self.model._meta.using]
    #    from django.db.models import AutoField
    #
    #    for obj in objs:
    #        data = {}
    #        for f in fields:
    #            val = f.get_db_prep_save(getattr(obj, f.attname) if raw else f.pre_save(obj, True),
    #                                     connection=connection)
    #
    #            if not f.null and val is None:
    #                if isinstance(f, AutoField):
    #                    continue
    #                raise IntegrityError("You can't set %s (a non-nullable field) to None!" % f.name)
    #
    #            db_type = f.db_type(connection=connection)
    #            value = self.convert_value_for_db(db_type, val)
    #            if value is None:
    #                continue
    #            data[f.column] = value
    #        yield (obj, data)
    #
    #    raise StopIteration

    def refresh(self):
        """Refresh an index"""
        connection = self.model._meta.dj_connection
        return connection.connection.indices.refresh(indices=connection.database)


    def terms(self, field):
        connection = self.model._meta.dj_connection
        return connection.connection.terms(connection.database, self.model._meta.db_table, field=field)["terms"]

    def _update(self, values):

        connection = self.model._meta.dj_connection
        index = self.get_index(connection)

        meta = self.model._meta
        db_table = meta.db_table
        updated = False
        for obj in self:
            record = {}
            for field, boh, new_value in values:
                record[field.attname] = field.get_db_prep_save(new_value, connection=connection)
            res = connection.connection.update(index=index, doc_type=self.type, id=obj.pk,
                                               document=record)
            updated = True
        return updated

    _update.queryset_only = False

    def get_objects_for_user(self, user, perms=None):
        if user.is_superuser:
            return self.all()
        prefix = "u.%s" % user.pk
        group_perms = user.get_group_cooked_perm_list()

        return self.filter(perms__startswith=prefix)

        # if perms is None:
        #     perms = [u'%s.%s.view' % (self.model._meta.app_label, self.model._meta.model_name)]
        #
        # return get_objects_for_user(user, perms=perms, klass=self.model)

    def get_index(self, connection=None):
        if self.model._meta.index :
            return self.model._meta.index
        if self._using and self._using not in ["default", "echidnasearch"]:
            return self._using
        return self.model._meta.get_index(connection=connection)


class EmptyQuerySet(QuerySet):
    def _do_query(self):
        return EmptyResultSet()


class ValueListResolver(object):
    """
    Class to resolve vertices in django objects
    """

    def __init__(self, model, fields, flat=False):
        """
        :param model: the current model
        :param fields: a cooked fields set (es_field, djfield, field)
        """
        self.fields = fields
        self.model = model
        self.flat = flat

    def __call__(self, *args, **kwargs):
        results = []
        from django.db import models

        es_fields = args[1].get("fields", {})
        for es_name, dj_name, djfield in self.fields:
            if es_name == "pk":
                value = args[1]["_id"]
            elif es_name == "id":
                value = es_fields.get(es_name, args[1]["_id"])
            else:
                value = es_fields.get(es_name, None)
            if value and isinstance(djfield, models.ForeignKey):
                djfield.rel.to.objects.get(pk=value)
            if self.flat:
                return value
            results.append(value)
        return tuple(results)


class ModelIteratorResolver(object):
    def __init__(self, model, items=None):
        self.model = model
        self.items = items
        self.iterpos = 0
        self._current_item = 0

    def __len__(self):
        return len(self.items)

    def count(self):
        return len(self.items)

    def total(self):
        return len(self.items)

    def __call__(self, *args, **kwargs):
        return list(self)

    def __getitem__(self, val):
        if not isinstance(val, (int, long, slice)):
            raise TypeError('%s indices must be integers, not %s' % (
                self.__class__.__name__, val.__class__.__name__))

        def get_start_end(val):
            if isinstance(val, slice):
                start = val.start
                if not start:
                    start = 0
                end = val.stop or len(self.items)
                if end < 0:
                    end = len(self.items) + end
                if end > len(self.items):
                    end = len(self.items)
                return start, end
            return val, val + 1

        start, end = get_start_end(val)

        if not isinstance(val, slice):
            if len(self.items) == 1:
                val = self.get_model(self.items[0])
                if val:
                    return val
                raise StopIteration
            raise IndexError
        return [v for v in [self.get_model(hit) for hit in self.items[start:end]] if v]

    def next(self):
        if len(self.items) == self.iterpos:
            raise StopIteration

        res = self.items[self.iterpos]
        val = self.get_model(res)
        if not val:
            return self.next()

        self.iterpos += 1
        if len(self.items) == self.iterpos:
            raise StopIteration
        return val

    def __iter__(self):
        self.iterpos = 0
        self._current_item = 0
        return self

    def get_model(self, object_id):
        try:
            return self.model.objects.get(pk=object_id)
        except self.model.DoesNotExist:
            self.items.remove(object_id)
            return None


class FacetHelper(dict):
    def __init__(self, model, facets):
        self._model = model
        self.update(facets)

    def __setattr__(self, key, value):
        if not self.__dict__.has_key(
                '_FacetHelper__initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, key, value)
        elif self.__dict__.has_key(key):       # any normal attributes are handled normally
            dict.__setattr__(self, key, value)
        else:
            self.__setitem__(key, value)

    def get_as_list(self, name):
        terms = self.get(name, {}).get("terms", [])
        for term in terms:
            yield term["term"]
        raise StopIteration
