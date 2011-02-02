#!/usr/bin/env python

import pyes

conn = pyes.ES('127.0.0.1:9200')

try:
    conn.delete_index("test-index")
    conn.delete_index("test-index2")
    conn.delete_index("test-index3")
except Exception, e: print e

conn.create_index("test-index")
conn.create_index("test-index2")
conn.create_index('test-index3')
conn.delete_index('test-index3')

