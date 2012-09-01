#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The main QuerySet implementation. This provides the public API for the ORM.

Taken from django one and from django-elasticsearch.
"""


import copy

# The maximum number of items to display in a QuerySet.__repr__
import six
from .es import ES
from .filters import ANDFilter, ORFilter, NotFilter, Filter, TermsFilter, TermFilter, RangeFilter, ExistsFilter
from pyes.models import ElasticSearchModel
from .query import MatchAllQuery, BoolQuery, FilteredQuery, Search
from .utils import ESRange

REPR_OUTPUT_SIZE = 20

class DoesNotExist(Exception):
    pass


class MultipleObjectsReturned(Exception):
    pass

def get_es_connection():
    return ES()

class ESModel(ElasticSearchModel):

    def __init__(self, index, type):
        self._index=index
        self._type=type
        self.objects = QuerySet(self)
        setattr(self, "DoesNotExist", DoesNotExist)
        setattr(self, "MultipleObjectsReturned", MultipleObjectsReturned)

def generate_model(index, doc_type):
    MyModel = type(
           'MyModel',
           (ElasticSearchModel,),
           {}
           )
    setattr(MyModel, "objects", QuerySet(MyModel, index=index, type=doc_type))
    setattr(MyModel, "DoesNotExist", DoesNotExist)
    setattr(MyModel, "MultipleObjectsReturned", MultipleObjectsReturned)
    return MyModel

class QuerySet(object):
    """
    Represents a lazy database lookup for a set of objects.
    """
    def __init__(self, model=None, using=None, index=None, type=None):
        if model is None and index and type:
            model = ESModel(index, type)
        self.model = model
        # EmptyQuerySet instantiates QuerySet with model as None
        self._index=index
        if using:
            self._index = using
        self._type=type

        self._queries = []
        self._filters = []
        self._facets = []
        self._ordering = []
        self._fields = [] #fields to load
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


    def _do_query(self):
        query=Search(self._build_query())
        if self._ordering:
            query.sort=self._ordering
        return get_es_connection().search(query, indices=self.index, doc_types=self.type)


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
        if isinstance(other, EmptyQuerySet):
            return other._clone()
        combined = self._clone()
        combined.query.combine(other.query, ANDFilter)
        return combined

    def __or__(self, other):
        combined = self._clone()
        if isinstance(other, EmptyQuerySet):
            return combined
        combined.query.combine(other.query, ORFilter)
        raise NotImplementedError()
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
        obj.save(force_insert=True, using=self.index)
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
            meta.connection = get_es_connection()
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
        obj.size=1
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
        get_es_connection().delete_by_query(self._build_query())
        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None

    def update(self, **kwargs):
        """
        Updates all elements in the current QuerySet, setting all the given
        fields to the appropriate values.
        """
        query = self._build_query()

        for item in

        query.add_update_values(kwargs)
        updates=[{"script": 'ctx._source.%s=value'%k,"params": {"value": v}} for k,v in kwargs.items()]
        get_es_connection().update_by_query(indices=self.index, doc_types=self.type, query=query, updates=updates)
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
        raise NotImplementedError()
#        return self._clone(klass=ValuesQuerySet, setup=True, _fields=fields)

    def values_list(self, *fields, **kwargs):
#        flat = kwargs.pop('flat', False)
#        if kwargs:
#            raise TypeError('Unexpected keyword arguments to values_list: %s'
#                    % (kwargs.keys(),))
#        if flat and len(fields) > 1:
#            raise TypeError("'flat' is not valid when values_list is called with more than one field.")
#        return self._clone(klass=ValuesListQuerySet, setup=True, flat=flat,
#                _fields=fields)
        raise NotImplementedError()

    def dates(self, field_name, kind, order='ASC'):
        """
        Returns a list of datetime objects representing all available dates for
        the given field_name, scoped to 'kind'.
        """
#        assert kind in ("month", "year", "day"), \
#                "'kind' must be one of 'year', 'month' or 'day'."
#        assert order in ('ASC', 'DESC'), \
#                "'order' must be either 'ASC' or 'DESC'."
#        return self._clone(klass=DateQuerySet, setup=True,
#                _field_name=field_name, _kind=kind, _order=order)
        raise NotImplementedError()

    def none(self):
        """
        Returns an empty QuerySet.
        """
        return self._clone(klass=EmptyQuerySet)

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
        if "__" in field:
            field, modifier = field.rsplit("__", 1)
            field=field.replace("__", ".")
        else:
            modifier=""
        if not modifier:
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
        else:
            return self._filter_or_exclude(None, **filter_obj)


    def annotate(self, *args, **kwargs):
        """
        Return a query set in which the returned objects have been annotated
        with data aggregated from related fields.
        """
#        for arg in args:
#            if arg.default_alias in kwargs:
#                raise ValueError("The named annotation '%s' conflicts with the "
#                                 "default name for another annotation."
#                                 % arg.default_alias)
#            kwargs[arg.default_alias] = arg
#
#        names = getattr(self, '_fields', None)
#        if names is None:
#            names = set(self.model._meta.get_all_field_names())
#        for aggregate in kwargs:
#            if aggregate in names:
#                raise ValueError("The annotation '%s' conflicts with a field on "
#                    "the model." % aggregate)
#
#        obj = self._clone()
#
#        obj._setup_aggregate_query(kwargs.keys())
#
#        # Add the aggregates to the query
#        for (alias, aggregate_expr) in kwargs.items():
#            obj.query.add_aggregate(aggregate_expr, self.model, alias,
#                is_summary=False)
#
#        return obj
        raise NotImplementedError()

    def order_by(self, *field_names):
        """
        Returns a new QuerySet instance with the ordering changed.
        """
        obj = self._clone()
        obj._clear_ordering()
        for field in field_names:
            if field.startswith("-"):
                obj._ordering.append({ field.lstrip("-") : "desc" })
            else:
                obj._ordering.append(field)
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

    def extra(self, select=None, where=None, params=None, tables=None,
              order_by=None, select_params=None):
        """
        Adds extra SQL fragments to the query.
        """
#        assert self.query.can_filter(), \
#                "Cannot change a query once a slice has been taken"
#        clone = self._clone()
#        clone.query.add_extra(select, select_params, where, params, tables, order_by)
#        return clone
        raise NotImplementedError()

    def reverse(self):
        """
        Reverses the ordering of the QuerySet.
        """
#        clone = self._clone()
#        clone.query.standard_ordering = not clone.query.standard_ordering
#        return clone
        raise NotImplementedError()

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
#        if self.query.extra_order_by or self.query.order_by:
#            return True
#        elif self.query.default_ordering and self.query.model._meta.ordering:
#            return True
#        else:
#            return False
        raise NotImplementedError()
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

    def _clone(self, klass=None, setup=False, **kwargs):
        if klass is None:
            klass = self.__class__
        c = klass(model=self.model, using=self.index, index=self.index, type=self.type)
        #copy filters/queries/facet????
        c.__dict__.update(kwargs)
        c._queries=list(self._queries)
        c._filters=list(self._filters)
        c._facets=list(self._facets)
        c._fields=list(self._fields)
        return c

    # When used as part of a nested query, a queryset will never be an "always
    # empty" result.
    value_annotation = True


class EmptyQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None):
        super(EmptyQuerySet, self).__init__(model, query, using)
        self._result_cache = []

    def __and__(self, other):
        return self._clone()

    def __or__(self, other):
        return other._clone()

    def count(self):
        return 0

    def delete(self):
        pass

    def _clone(self, klass=None, setup=False, **kwargs):
        c = super(EmptyQuerySet, self)._clone(klass, setup=setup, **kwargs)
        c._result_cache = []
        return c

    def iterator(self):
        # This slightly odd construction is because we need an empty generator
        # (it raises StopIteration immediately).
        yield next(iter([]))

    def all(self):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def filter(self, *args, **kwargs):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def exclude(self, *args, **kwargs):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def complex_filter(self, filter_obj):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def select_related(self, *fields, **kwargs):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def annotate(self, *args, **kwargs):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def order_by(self, *field_names):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def distinct(self, fields=None):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def extra(self, select=None, where=None, params=None, tables=None,
              order_by=None, select_params=None):
        """
        Always returns EmptyQuerySet.
        """
        assert self.query.can_filter(), \
                "Cannot change a query once a slice has been taken"
        return self

    def reverse(self):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def defer(self, *fields):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def only(self, *fields):
        """
        Always returns EmptyQuerySet.
        """
        return self

    def update(self, **kwargs):
        """
        Don't update anything.
        """
        return 0

    def aggregate(self, *args, **kwargs):
        """
        Return a dict mapping the aggregate names to None
        """
        for arg in args:
            kwargs[arg.default_alias] = arg
        return dict([(key, None) for key in kwargs])

    # EmptyQuerySet is always an empty result in where-clauses (and similar
    # situations).
    value_annotation = False
