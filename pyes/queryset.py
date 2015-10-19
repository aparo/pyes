#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The main QuerySet implementation. This provides the public API for the ORM.

Taken from django one and from django-elasticsearch.
"""


import copy
import six

# The maximum number of items to display in a QuerySet.__repr__
from .es import ES
from .filters import ANDFilter, ORFilter, NotFilter, Filter, TermsFilter, TermFilter, RangeFilter, ExistsFilter
from .facets import Facet, TermFacet
from .aggs import Agg, TermsAgg
from .models import ElasticSearchModel
from .orm.exceptions import DoesNotExist, MultipleObjectsReturned
from .query import MatchAllQuery, BoolQuery, FilteredQuery, Search
from .utils import ESRange
from .utils.compat import integer_types
REPR_OUTPUT_SIZE = 20


def get_es_connection(es_url, es_kwargs):
    #import pdb;pdb.set_trace()
    if es_url:
        es_kwargs.update(server=es_url)
    return ES(**es_kwargs)


class ESModel(ElasticSearchModel):

    def __init__(self, index, type, es_url=None, es_kwargs={}):
        self._index = index
        self._type = type
        self.objects = QuerySet(self, es_url=es_url, es_kwargs=es_kwargs)
        setattr(self, "DoesNotExist", DoesNotExist)
        setattr(self, "MultipleObjectsReturned", MultipleObjectsReturned)


def generate_model(index, doc_type, es_url=None, es_kwargs={}):
    MyModel = type('MyModel', (ElasticSearchModel,), {})

    setattr(MyModel, "objects", QuerySet(MyModel, index=index, type=doc_type, es_url=es_url, es_kwargs=es_kwargs))
    setattr(MyModel, "DoesNotExist", DoesNotExist)
    setattr(MyModel, "MultipleObjectsReturned", MultipleObjectsReturned)
    return MyModel


class QuerySet(object):
    """
    Represents a lazy database lookup for a set of objects.
    """
    def __init__(self, model=None, using=None, index=None, type=None, es_url=None, es_kwargs={}):
        self.es_url = es_url
        self.es_kwargs = es_kwargs
        if model is None and index and type:
            model = ESModel(index, type, es_url=self.es_url, es_kwargs=self.es_kwargs)
        self.model = model

        # EmptyQuerySet instantiates QuerySet with model as None
        self._index = index
        if using:
            self._index = using
        self._type=type
        self._queries = []
        self._filters = []
        self._facets = []
        self._aggs = []
        self._ordering = []
        self._fields = [] #fields to load
        self._size=None
        self._start=0
        self._result_cache = None #hold the resultset

    def _clear_ordering(self):
        #reset ordering
        self._ordering=[]

    @property
    def index(self):
        if self._index:
            return self._index
        return self.model._index

    @property
    def type(self):
        if self._type:
            return self._type
        return self.model._type

    ########################
    # PYTHON MAGIC METHODS #
    ########################

    def __deepcopy__(self, memo):
        """
        Deep copy of a QuerySet doesn't populate the cache
        """
        obj = self.__class__()
        for k,v in self.__dict__.items():
            if k in ('_iter','_result_cache'):
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
            if len(self._queries)==1:
                query=self._queries[0]
            else:
                query=BoolQuery(must=self._queries)
        if not self._filters:
            return query
        if len(self._filters)==1:
            return FilteredQuery(query, self._filters[0])
        return FilteredQuery(query, ANDFilter(self._filters))

    def _build_search(self):
        query=Search(self._build_query())
        if self._ordering:
            query.sort=self._ordering
        if self._facets:
            for facet in self._facets:
                query.facet.add(facet)
        if self._aggs:
            for agg in self._aggs:
                query.agg.add(agg)
        if self._start is not None:
            query.start = self._start
        if self._size is not None:
            query.size = self._size
        return query

    def _do_query(self):
        return get_es_connection(self.es_url, self.es_kwargs).search(self._build_search(), indices=self.index, doc_types=self.type)


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

#    def _result_iter(self):
#        pos = 0
#        while 1:
#            upper = len(self._result_cache)
#            while pos < upper:
#                yield self._result_cache[pos]
#                pos = pos + 1
#            if not self._iter:
#                raise StopIteration
#            if len(self._result_cache) <= pos:
#                self._fill_cache()

    def __bool__(self):
        return self.__nonzero__()

    def __nonzero__(self):
        if self._result_cache is not None:
            len(self)
            return bool(self._result_cache.total!=0)
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
        if not isinstance(k, (slice,) + integer_types):
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

    def size(self, number):
        clone = self._clone()
        clone._size=number
        return clone

    def start(self, number):
        clone = self._clone()
        clone._start=number
        return clone

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
        raise NotImplementedError()

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
	meta = obj.get_meta()
        meta.connection = get_es_connection(self.es_url, self.es_kwargs)
        meta.index=self.index
        meta.type=self.type
        obj.save(force=True)
        return obj

    def bulk_create(self, objs, batch_size=None):
        """
        Inserts each of the instances into the database. This does *not* call
        save() on each of the instances, does not send any pre/post save
        signals, and does not set the primary key attribute if it is an
        autoincrement field.
        """
        # So this case is fun. When you bulk insert you don't get the primary
        # keys back (if it's an autoincrement), so you can't insert into the
        # child tables which references this. There are two workarounds, 1)
        # this could be implemented if you didn't have an autoincrement pk,
        # and 2) you could do it by doing O(n) normal inserts into the parent
        # tables to get the primary keys back, and then doing a single bulk
        # insert into the childmost table. Some databases might allow doing
        # this by using RETURNING clause for the insert query. We're punting
        # on these for now because they are relatively rare cases.
#        assert batch_size is None or batch_size > 0
#        if self.model._meta.parents:
#            raise ValueError("Can't bulk create an inherited model")
#        if not objs:
#            return objs
#        self._for_write = True
#        connection = connections[self.db]
#        fields = self.model._meta.local_fields
#        if not transaction.is_managed(using=self.db):
#            transaction.enter_transaction_management(using=self.db)
#            forced_managed = True
#        else:
#            forced_managed = False
#        try:
#            if (connection.features.can_combine_inserts_with_and_without_auto_increment_pk
#                and self.model._meta.has_auto_field):
#                self._batched_insert(objs, fields, batch_size)
#            else:
#                objs_with_pk, objs_without_pk = partition(lambda o: o.pk is None, objs)
#                if objs_with_pk:
#                    self._batched_insert(objs_with_pk, fields, batch_size)
#                if objs_without_pk:
#                    fields= [f for f in fields if not isinstance(f, AutoField)]
#                    self._batched_insert(objs_without_pk, fields, batch_size)
#            if forced_managed:
#                transaction.commit(using=self.db)
#            else:
#                transaction.commit_unless_managed(using=self.db)
#        finally:
#            if forced_managed:
#                transaction.leave_transaction_management(using=self.db)
#
#        return objs
        raise NotImplementedError()

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
            meta = obj.get_meta()
            meta.connection = get_es_connection(self.es_url, self.es_kwargs)
            meta.index=self.index
            meta.type=self.type
            obj.save(force=True)
            return obj, True

    def latest(self, field_name=None):
        """
        Returns the latest object, according to the model's 'get_latest_by'
        option or optional given field_name.
        """
        latest_by = field_name or "_id"#self.model._meta.get_latest_by
        assert bool(latest_by), "latest() requires either a field_name parameter or 'get_latest_by' in the model"
        obj = self._clone()
        obj._size=1
        obj._clear_ordering()
        obj._ordering.append({ latest_by : "desc" })
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
        get_es_connection(self.es_url, self.es_kwargs).delete_by_query(self.index, self.type, self._build_query())
        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None

    def update(self, **kwargs):
        """
        Updates all elements in the current QuerySet, setting all the given
        fields to the appropriate values.
        """
        query = self._build_query()
        connection = get_es_connection(self.es_url, self.es_kwargs)
        results = connection.search(query, indices=self.index, doc_types=self.type,
                                             model=self.model, scan=True)
        for item in results:
            item.update(kwargs)
            item.save(bulk=True)
        connection.flush_bulk(True)
        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None


    def exists(self):
        if self._result_cache is None:
            len(self)
        return bool(self._result_cache.total!=0)

    ##################################################
    # PUBLIC METHODS THAT RETURN A QUERYSET SUBCLASS #
    ##################################################

    def values(self, *fields):
        search = self._build_search()
        search.facet.reset()
        search.agg.reset()
        search.fields=fields
        return get_es_connection(self.es_url, self.es_kwargs).search(search, indices=self.index, doc_types=self.type)

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
        search.agg.reset()
        search.fields=fields
        if flat:
            return get_es_connection(self.es_url, self.es_kwargs).search(search, indices=self.index, doc_types=self.type,
                                              model=lambda x,y: y.get("fields", {}).get(fields[0], None))

        return get_es_connection(self.es_url, self.es_kwargs).search(search, indices=self.index, doc_types=self.type)

    def dates(self, field_name, kind, order='ASC'):
        """
        Returns a list of datetime objects representing all available dates for
        the given field_name, scoped to 'kind'.
        """

        assert kind in ("month", "year", "day", "week", "hour", "minute"), \
                "'kind' must be one of 'year', 'month', 'day', 'week', 'hour' and 'minute'."
        assert order in ('ASC', 'DESC'), \
                "'order' must be either 'ASC' or 'DESC'."

        search= self._build_search()
        search.facet.reset()
        search.facet.add_date_facet(name=field_name.replace("__", "."),
                 field=field_name, interval=kind)
        search.agg.reset()
        search.agg.add_date_agg(name=field_name.replace("__", "."),
                 field=field_name, interval=kind)
        search.size=0
        resulset = get_es_connection(self.es_url, self.es_kwargs).search(search, indices=self.index, doc_types=self.type)
        resulset.fix_aggs()
        entries = []
        for val in resulset.aggs.get(field_name.replace("__", ".")).get("entries", []):
            if "time" in val:
                entries.append(val["time"])
        if order=="ASC":
            return sorted(entries)

        return sorted(entries, reverse=True)

    def none(self):
        """
        Returns an empty QuerySet.
        """
        #return self._clone(klass=EmptyQuerySet)
        raise NotImplementedError()

    ##################################################################
    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
    ##################################################################

    def all(self):
        """
        Returns a new QuerySet that is a copy of the current one. This allows a
        QuerySet to proxy for a model manager in some cases.
        """
        return self._clone()

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
            if len(filters)>1:
                filters=ANDFilter(filters)
            else:
                filters=filters[0]
            clone._filters.append(NotFilter(filters))
        else:
            clone._filters.extend(filters)
        return clone

    def _build_inner_filter(self, field, value):
        modifiers = ('in', 'gt', 'gte', 'lte', 'lt', 'in', 'ne', 'exists', 'exact')
        if field.endswith(tuple(['__{0}'.format(m) for m in modifiers])):
            field, modifier = field.rsplit("__", 1)
        else:
            modifier=""
        field=field.replace("__", ".")
        if not modifier or modifier == 'exact':
            if isinstance(value, list):
                return TermsFilter(field, value)
            return TermFilter(field, value)

        if modifier=="in":
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
        elif modifier=="exists":
            if isinstance(value, bool) and value:
                return ExistsFilter(field)
            return NotFilter(ExistsFilter(field))

        raise NotImplementedError()



    def _build_filter(self, *args, **kwargs):
        filters = []
        if args:
            for f in args:
                if isinstance(f, Filter):
                    filters.append(f)
                #elif isinstance(f, dict):
                    #TODO: dict parser
                else:
                    raise TypeError('Only Filter objects can be passed as argument')
        for field, value in kwargs.items():
            filters.append(self._build_inner_filter(field, value))
        return filters

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

    def agg(self, *args, **kwargs):
        return self.annotate(*args, **kwargs)

    def annotate(self, *args, **kwargs):
        """
        Return a query set in which the returned objects have been annotated
        with data aggregated from related fields.
        """
        obj = self._clone()

        for arg in args:
            if isinstance(arg, Facet):
                obj._facets.append(arg)
            elif isinstance(arg, six.string_types):
                obj._facets.append(TermFacet(arg.replace("__", ".")))
            elif isinstance(arg, Agg):
                obj._aggs.append(arg)
            elif isinstance(arg, six.string_types):
                obj._facets.append(TermFacet(arg.replace("__", ".")))
            else:
                raise NotImplementedError("invalid type")


        # Add the aggregates/facet to the query
        for name, field in kwargs.items():
            obj._facets.append(TermFacet(field=field.replace("__", "."), name=name.replace("__", ".")))
            obj._aggs.append(TermsAgg(field=field.replace("__", "."), name=name.replace("__", ".")))
        return obj

    def order_by(self, *field_names):
        """
        Returns a new QuerySet instance with the ordering changed.
        """
        obj = self._clone()
        obj._clear_ordering()
        for field in field_names:
            if field.startswith("-"):
                obj._ordering.append({ field.lstrip("-").replace("__", ".") : "desc" })
            else:
                obj._ordering.append({ field : "asc" })
        return obj

    def distinct(self, *field_names):
        """
        Returns a new QuerySet instance that will select only distinct results.
        """
#        assert self.query.can_filter(), \
#                "Cannot create distinct fields once a slice has been taken."
#        obj = self._clone()
#        obj.query.add_distinct_fields(*field_names)
#        return obj
        raise NotImplementedError()


    def reverse(self):
        """
        Reverses the ordering of the QuerySet.
        """
        clone = self._clone()
        assert self._ordering, "You need to set an ordering for reverse"
        ordering = []
        for order in self._ordering:
            for k,v in order.items():
                if v=="asc":
                    ordering.append({k: "desc"})
                else:
                    ordering.append({k: "asc"})
        clone._ordering=ordering
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
        clone._fields=fields
        return clone

    def using(self, alias):
        """
        Selects which database this QuerySet should excecute its query against.
        """
        clone = self._clone()
        clone._index = alias
        return clone

    ###################################
    # PUBLIC INTROSPECTION ATTRIBUTES #
    ###################################

    def ordered(self):
        """
        Returns True if the QuerySet is ordered -- i.e. has an order_by()
        clause or a default ordering on the model.
        """
        return len(self._ordering)>0
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

    @property
    def facets(self):
        if len(self._facets)==0:
            return {}
        if self._result_cache is None:
            len(self)
        return self._result_cache.facets

    @property
    def aggs(self):
        if len(self._aggs)==0:
            return {}
        if self._result_cache is None:
            len(self)
        return self._result_cache.aggs

    ###################
    # PRIVATE METHODS #
    ###################

    def _clone(self, klass=None, setup=False, **kwargs):
        if klass is None:
            klass = self.__class__
        c = klass(model=self.model, using=self.index, index=self.index, type=self.type, es_url=self.es_url, es_kwargs=self.es_kwargs)
        #copy filters/queries/facet????
        c.__dict__.update(kwargs)
        c._queries=list(self._queries)
        c._filters=list(self._filters)
        c._facets=list(self._facets)
        c._aggs=list(self._aggs)
        c._fields=list(self._fields)
        c._ordering=list(self._ordering)
        c._size=self._size
        c._start=self._start
        return c


    # When used as part of a nested query, a queryset will never be an "always
    # empty" result.
    value_annotation = True
