=============================
 pyes - Python ElasticSearch
=============================

:Version: 0.1.0
#:Web: http://pypi.python.org/pypi/pyes/
#:Download: http://pypi.python.org/pypi/pyes/
:Source: http://github.com/aparo/pyes/
:Keywords: search, elastisearch, distribute search

--

pyes is a connector to use elasticsearch from python.

For now it is in alpha state, but working.

Usage
=====

::
	from pyes import *
	
	conn = ElasticSearch('http://127.0.0.1:9200/')
	try:
		conn.delete_index("test-index")
	except:
		pass
	
	mapping = { u'parsedtext': {'boost': 1.0,
	                     'index': 'analyzed',
	                     'store': 'yes',
	                     'type': u'string',
	                     "term_vector" : "with_positions_offsets"},
	             u'name': {'boost': 1.0,
	                        'index': 'analyzed',
	                        'store': 'yes',
	                        'type': u'string',
	                        "term_vector" : "with_positions_offsets"},
	             u'title': {'boost': 1.0,
	                        'index': 'analyzed',
	                        'store': 'yes',
	                        'type': u'string',
	                        "term_vector" : "with_positions_offsets"},
	             u'pos': {'store': 'yes',
	                        'type': u'integer'},
	             u'uuid': {'boost': 1.0,
	                       'index': 'not_analyzed',
	                       'store': 'yes',
	                       'type': u'string'}}
	conn.create_index("test-index")
	conn.put_mapping("test-type", {'properties':mapping}, ["test-index"])
	conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, "test-index", "test-type", 1)
	conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, "test-index", "test-type", 2)
	conn.refresh(["test-index"])
	
	q = TermQuery("name", "joe")
	result = self.conn.search(query = q)
	if result['hits']['total'] == 1:
	    print "ok"
	else:
		print "No results"


For more examples looks at the tests.


TODO
----

- connection pool
- multiprocess for indexing
- API rewriting for indexing and mapping part
- more docs
- more tests
- facets
- cleanup



License
=======

This software is licensed under the ``New BSD License``. See the ``LICENSE``
file in the top distribution directory for the full license text.

.. # vim: syntax=rst expandtab tabstop=4 shiftwidth=4 shiftround