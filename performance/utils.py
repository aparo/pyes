#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Brainaetic: http://www.thenetplanet.com
#Copyright 2009-2010 - The Net Planet Europe S.R.L.  All Rights Reserved. 

import random
import os
from django.contrib.webdesign.lorem_ipsum import words as li_words
import shelve
import codecs

def get_names():
    """
    Return a list of names.
    """
    return [n.strip() for n in codecs.open(os.path.join("data", "names.txt"),"rb",'utf8').readlines()]

def generate_dataset(number_items=1000):
    """
    Generate a dataset with number_items elements.
    """
    data = []
    names = get_names()
    totalnames = len(names)
    #init random seeder
    random.seed()
    #calculate items
#    names = random.sample(names, number_items)
    for i in xrange(number_items):
        data.append({"name":names[random.randint(0,totalnames-1)],
                     "age":random.randint(1,100),
                     "description":li_words(50, False)})
    return data

def generate_dataset_shelve(filename, number_items=1000):
    """
    Generate a dataset with number_items elements.
    """
    if os.path.exists(filename):
        os.remove(filename)
    data = shelve.open(filename)
    names = get_names()
    totalnames = len(names)
    #init random seeder
    random.seed()
    #calculate items
#    names = random.sample(names, number_items)
    for i in xrange(number_items):
        data[str(i+1)] = {"name":names[random.randint(0,totalnames-1)],
                     "age":random.randint(1,100),
                     "description":li_words(50, False)}
    data.close()

