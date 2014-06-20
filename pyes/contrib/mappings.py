#!/usr/bin/env python
# -*- coding: utf-8 -*-
from future import print_function

from pyes.es import ES
from pyes import mappings

def mappings_to_code(obj, doc_count=0):
    result = []
    odict = obj.as_dict()
    if isinstance(obj, (mappings.DocumentObjectField, mappings.ObjectField, mappings.NestedObject)):
        properties = odict.pop("properties", [])
        doc_count += 1
        kwargs = ["name=%r" % obj.name,
                  "type=%r" % odict.pop("type")] +\
                 ["%s=%r" % (k, odict[k]) for k in sorted(odict.keys())]
        result.append(
            "doc%d=" % doc_count + str(type(obj)).split(".")[-1].strip("'>") + "(" + ', '.join(kwargs) + ")")
        for k in sorted(obj.properties.keys()):
            result.extend(mappings_to_code(obj.properties[k], doc_count))
    else:
        kwargs = ["name=%r" % obj.name,
                  "type=%r" % odict.pop("type"),
                  "store=%r" % obj.store,
                  "index=%r" % odict.pop("index")] +\
                 ["%s=%r" % (k, odict[k]) for k in sorted(odict.keys())]
        result.append("doc%d.add_property(" % doc_count +\
                      str(type(obj)).split(".")[-1].strip("'>") + "(" +\
                      ', '.join(kwargs) + "))")

    return result

if __name__ == '__main__':
    es = ES("192.168.1.1:9200")
    res = mappings_to_code(es.mappings.get_doctype("twitter", "twitter"))
    print("\n".join(res))
