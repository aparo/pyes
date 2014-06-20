import sys

#sys.path.insert(0, "../")

#from pyes import ES
from pyes.es import ES
from datetime import datetime
import shelve
conn = ES('127.0.0.1:9500')
#conn = ES('192.168.2.50:9200')
try:
    conn.delete_index("test-index")
except:
    pass

dataset = shelve.open("samples.shelve")

mapping = {u'description': {'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "term_vector": "with_positions_offsets"
},
           u'name': {'boost': 1.0,
                     'index': 'analyzed',
                     'store': 'yes',
                     'type': u'string',
                     "term_vector": "with_positions_offsets"
           },
           u'age': {'store': 'yes',
                    'type': u'integer'},
           }
conn.create_index("test-index")
conn.put_mapping("test-type", {'properties': mapping}, ["test-index"])

start = datetime.now()
for k, userdata in dataset.items():
#    conn.index(userdata, "test-index", "test-type", k)
    conn.index(userdata, "test-index", "test-type", k, bulk=True)
conn.force_bulk()
end = datetime.now()

print "time:", end - start
dataset.close()

