#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

__version__ = "0.1.0"

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))  # nopep8

import requests
from cypresspoint.datatype import as_bool
from cypresspoint.searchcommand import ensure_fields
from cypresspoint.spath import splunk_dot_notation
from requests.auth import HTTPBasicAuth
from splunklib.searchcommands import Configuration, Option, StreamingCommand, dispatch, validators

""" http debug logging
import logging
from http.client import HTTPConnection  # py3

log = logging.getLogger('urllib3')
log.setLevel(logging.DEBUG)
"""


@Configuration()
class JsonFormatCommand(StreamingCommand):
    """

    ##Syntax

    .. code-block::
        jsonformat =my_ field=input

    ##Description

    ##Example
    """

    output = Option(
        require=True,
        validate=validators.Fieldname())

    field_set = Option(
        require=False,
        validate=validators.Set("a", "b", "c"))

    field_int = Option(
        require=False,
        default=32,
        validate=validators.Integer(1, 128))

    field_bool = Option(
        require=False,
        default=True,
        validate=validators.Boolean())

    """ COOKIECUTTER-TODO:  Use or delete these tips'n'tricks

    *** Class-level stuff ***

    # Always run on the search head (not the indexers)
    distributed = False

    # Don't allow this to run in preview mode to limit API hits
    run_in_preview = False


    *** Method-level stuff ***

    # Log the commands given to the SPL command:
    self.logger.debug('JsonFormatCommand: %s', self)

    # Access metadata about the search, such as earliest_time for the selected time range
    self.metadata.searchinfo.earliest_time


    *** Runtime / testing ***

    Enable debug logging:

        ... | jsonformat logging_level=DEBUG ...

    """

    def __init__(self):
        super(JsonFormatCommand, self).__init__()
        # COOKIECUTTER-TODO: initialize any custom variables in __init__()

    def prepare(self):
        super(JsonFormatCommand, self).prepare()
        # COOKIECUTTER-TODO: Customize or DELETE prepare() - arg validation & REST/CONF fetch

        will_execute = bool(self.metadata.searchinfo.sid and
                            not self.metadata.searchinfo.sid.startswith("searchparsetmp_"))
        if will_execute:
            self.logger.info("Launching version %s", __version__)

        ''' COOKIECUTTER-TODO: Enable/delete: this block of code will prevent unused/unknown parameters
        # Check to see if an unused arguments remain after argument parsing
        if self.fieldnames:
            self.write_error("The following arguments to jsonformat are "
                             "unknown:  {!r}  Please check the syntax.", self.fieldnames)
            sys.exit(1)
        '''
        # COOKIECUTTER-TODO:  Implement argument validation here, if needed

        if not will_execute:
            return
        # COOKIECUTTER-TODO:  Add custom REST endpoint/conf snippet here, if needed

    def _query_external_api(self, query_string):
        # COOKIECUTTER-TODO: Implement remote Jmespath API query here
        """ Handle the query to Jmespath API that drives this SPL command
        Returns (error, payload)
        """
        query_params = {
            "search": query_string
        }
        headers = {
            'content-type': "application/json",
            'x-api-auth': self.api_auth,
            'cache-control': "no-cache"
        }
        try:
            response = requests.request("GET", self.api_url, headers=headers, params=query_params)
        except requests.ConnectionError as e:
            self.logger.error("Aborting due to API connection failure.  %s", e)
            return ("Jmespath Connection failure:  {}".format(e), [])
        except Exception:
            self.logger.exception("Failure while calling API")
            return ("Jmespath API Call failed", [])
        result = response.json()
        if isinstance(result, dict) and "message" in result:
            return ("API returned message:  {}".format(result["message"]), result)
        elif len(result) == 0:
            result = []
        return (None, result)

    def stream(self, records):
        # COOKIECUTTER-TODO: Replace this code with your own streaming logic
        """ Streaming function that processes and yields event records 1:1 to the Splunk stream pipeline, in the same order as received.
        """
        for record in records:
            record[self.output] = 'bar'
            yield record


if __name__ == '__main__':
    dispatch(JsonFormatCommand, sys.argv, sys.stdin, sys.stdout, __name__)
