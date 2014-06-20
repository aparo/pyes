#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyes

index = "test2"
doc_type = "test"

es = pyes.ES(["http://127.0.0.1:9200"])

es.create_index_if_missing(index)
for i in range(1, 100):
    es.index({"number":i}, index=index, doc_type=doc_type)

es.refresh([index])

query = pyes.QueryStringQuery("*")
search = pyes.query.Search(query=query, start=0, size=10, sort=[{"number":"asc"}], fields=["number"])
results = es.search(search, indices=[index], doc_types=[doc_type])
print [i for i in results]

query2 = pyes.QueryStringQuery("*")
search2 = pyes.query.Search(query=query2, start=20, size=20, sort=[{"number":"asc"}], fields=["number"])
results2 = es.search(search2, indices=[index], doc_types=[doc_type])
print [i for i in results2]

es.delete_index_if_exists(index)
