#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Brainaetic: http://www.thenetplanet.com
#Copyright 2009-2010 - The Net Planet Europe S.R.L.  All Rights Reserved. 
import os
import sys

def generate_datafile_old(number_items=1000):
    """
    Create the samples.py file
    """
    from utils import get_names, generate_dataset
    from pprint import pprint
    filename = "samples.py"
    dataset = generate_dataset(number_items)
    fo = open(filename, "wb")
    fo.write("#!/usr/bin/env python\n")
    fo.write("# -*- coding: utf-8 -*-\n")
    fo.write("#Brainaetic: http://www.thenetplanet.com\n\n")
    fo.write("SAMPLES = ")
    pprint(dataset, fo)
    fo.close()
    print "%s generated with %d samples" % (filename, number_items)

def generate_datafile(number_items=20000):
    """
    Create the samples.py file
    """
    from utils import generate_dataset_shelve
    filename = "samples.shelve"
    dataset = generate_dataset_shelve(filename, number_items)
    print "%s generated with %d samples" % (filename, number_items)

if __name__ == '__main__':
    """
    Usage: 
            python generate_dataset.py 60000

    (Dataset size defaults to 1000 if not specified)
    """
    try:
        generate_datafile(int(sys.argv[1]))
    except IndexError:
        generate_datafile()
