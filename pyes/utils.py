#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'
__all__ = ['clean_string', "string_b64encode", "string_b64decode"]
import base64

def string_b64encode(s):
    """
    This function is useful to convert a string to a valid id to be used in ES.
    You can use it to generate an ID for urls or some texts
    """
    return base64.urlsafe_b64encode(s).strip('=')

def string_b64decode(s):
    return base64.urlsafe_b64decode(s + '=' * (len(s) % 4))

# Characters that are part of Lucene query syntax must be stripped
# from user input: + - && || ! ( ) { } [ ] ^ " ~ * ? : \
# See: http://lucene.apache.org/java/3_0_2/queryparsersyntax.html#Escaping
SPECIAL_CHARS = [33, 34, 38, 40, 41, 42, 45, 58, 63, 91, 92, 93, 94, 123, 124, 125, 126]
UNI_SPECIAL_CHARS = dict((c, None) for c in SPECIAL_CHARS)
STR_SPECIAL_CHARS = ''.join([chr(c) for c in SPECIAL_CHARS])

def clean_string(text):
    """
    Remove Lucene reserved characters from query string
    """
    if isinstance(text, unicode):
        return text.translate(UNI_SPECIAL_CHARS).strip()
    return text.translate(None, STR_SPECIAL_CHARS).strip()

def keys_to_string(data):
    """
    Function to convert all the unicode keys in string keys
    """
    if isinstance(data, dict):
        for key in list(data.keys()):
            if isinstance(key, unicode):
                value = data[key]
                val = keys_to_string(value)
                del data[key]
                data[key.encode("utf8", "ignore")] = val
    return data
