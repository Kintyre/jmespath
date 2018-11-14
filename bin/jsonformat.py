#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import ast
import sys
from collections import OrderedDict
from functools import partial

import json

from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators


def from_python(s):
    try:
        return ast.literal_eval(s)
    except SyntaxError as e:
        raise ValueError(e.msg)

@Configuration()
class JsonFormatCommand(StreamingCommand):
    """ Format a that a Json field and report any errors, if requested.

    ##Syntax

    .. code-block::
        jsonformat (indent=<int>)? (order=undefined|preserve|sort) (input_mode=json|python)? (errors=<field>)? (<field> (as <field>)?)*

    """
    indent = Option(
        doc="How many spaces for each indentation.",
        require=False, default=2, validate=validators.Integer(0,10))

    order = Option(
        doc="Pick order options.  undefined (default), preserve, or sort.  Only impacts hash order",
        require=False, default="undefined", validate=validators.Set("undefined", "preserve", "sort"))

    errors = Option(
        doc="field name to capture any parsing error messages.",
        require=False, default=None, validate=validators.Fieldname())

    input_mode = Option(
        doc="Select an alternate input mode.  Supports 'json' and 'python' repr format "
            "(literals only).  In this mode, the 'preserve' order option will not work.",
        require=False, default="json", validate=validators.Set("json", "python"))

    @staticmethod
    def handle_field_as(fieldnames):
        """ Convert a list of fields, which may include "a as b" style renaming into a more usable
        output format.  The output is a list of tuples in the form of (src, dest) showing any rename\
        mappings.  In the simple case, where no renaming occurs, src and dest are the same.
        """
        fields = fieldnames[:]
        fieldpairs = []
        while fields:
            f = fields.pop(0)
            if len(fields) > 1 and fields[0].lower() == "as":
                fieldpairs.append( (f, fields[1]))
                fields = fields[2:]
            else:
                fieldpairs.append((f,f))
        return fieldpairs

    def stream(self, records):
        json_loads = json.loads
        json_dumps = partial(json.dumps, indent=self.indent)

        if self.order == "preserve":
            json_loads = partial(json.loads, object_pairs_hook=OrderedDict)
        elif self.order == "sort":
            json_dumps = partial(json.dumps, indent=self.indent, sort_keys=True)

        if self.input_mode == "python":
            json_loads = from_python

        if self.fieldnames:
            fieldpairs = self.handle_field_as(self.fieldnames)
        else:
            fieldpairs = [ ("_raw", "_raw") ]

        self.logger.info("fieldnames={}".format(self.fieldnames))
        for (src_field, dest_field) in fieldpairs:
            if src_field != dest_field:
                self.logger.info("Mapping JSON field {} -> {}".format(src_field, dest_field))
        self.logger.info("fieldpairs={}".format(fieldpairs))

        first_row = True

        for record in records:
            errors = []
            for (src_field, dest_field) in fieldpairs:
                json_string = record.get(src_field, None)
                if isinstance(json_string, (list, tuple)):
                    # XXX: Add proper support for multivalue input fields.  For now, skip.
                    json_string = None
                if json_string:
                    try:
                        data = json_loads(json_string)
                        text = json_dumps(data)
                        record[dest_field] = text
                        # Handle special case for _raw message update
                        if dest_field == "_raw":
                            record["linecount"] = len(text.splitlines())
                        del data
                    except ValueError as e:
                        if len(fieldpairs) > 1:
                            errors.append("Field {} error:  {}".format(src_field, e.message))
                        else:
                            errors.append(e.message)
                else:
                    if src_field != dest_field:
                        record[dest_field] = json_string
                if self.errors:
                    record[self.errors] = errors or "none"

            # Make sure that all of our output fields are present on the first record, since this
            # dictates the possible return fields which cannot be updated later.
            if first_row:
                first_row = False
                needed_fields = [ df for (sf, df) in fieldpairs ]
                if "_raw" in needed_fields:
                    needed_fields.append("linecount")
                for f in needed_fields:
                    if f not in record:
                        record[f] = None

            yield record

dispatch(JsonFormatCommand, sys.argv, sys.stdin, sys.stdout, __name__)
