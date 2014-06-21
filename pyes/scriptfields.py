# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .exceptions import ScriptFieldsError


class ScriptField(object):
    def __init__(self, script, lang="mvel", params=None, ignore_failure=False):
        self.script = script
        self.lang = lang
        self.params = params
        self.ignore_failure = ignore_failure


class ScriptFields(object):
    """
    This object create the script_fields definition
    """
    _internal_name = "script_fields"

    def __init__(self, name=None, script=None, lang=None, params=None, ignore_failure=False):
        self.fields = {}
        if name:
            self.add_field(name, script, lang, params or {}, ignore_failure)

    def add_field(self, name, script, lang=None, params=None, ignore_failure=False):
        """
        Add a field to script_fields
        """
        data = {}
        if lang:
            data["lang"] = lang

        if script:
            data['script'] = script
        else:
            raise ScriptFieldsError("Script is required for script_fields definition")
        if params:
            if isinstance(params, dict):
                if len(params):
                    data['params'] = params
            else:
                raise ScriptFieldsError("Parameters should be a valid dictionary")
        if ignore_failure:
            data['ignore_failure'] = ignore_failure
        self.fields[name] = data

    def add_parameter(self, field_name, param_name, param_value):
        """
        Add a parameter to a field into script_fields

        The ScriptFields object will be returned, so calls to this can be chained.
        """
        try:
            self.fields[field_name]['params'][param_name] = param_value
        except Exception as ex:
            raise ScriptFieldsError("Error adding parameter %s with value %s :%s" % (param_name, param_value, ex))

        return self

    def serialize(self):
        return self.fields
