# -*- coding: utf-8 -*-
"""Altmetric

This is a wrapper module for Altmetric API.

Adopted from PyAltmetric (https://github.com/CenterForOpenScience/PyAltmetric)
and also pyAltmetric (https://github.com/wearp/pyaltmetric)

author: Asura Enkhbayar <asura.enkhbayar@gmail.com>
"""

import warnings
import requests


class AltmetricException(Exception):
    """Base class for any pyaltmetric error."""
    pass


class JSONParseException(AltmetricException):
    """
    Failed to turn HTTP Response into JSON.
    Site is probably in the wrong format.
    """
    pass


class AltmetricHTTPException(AltmetricException):
    """A query argument or setting was formatted incorrectly."""

    def __init__(self, status_code):
        response_codes = {
            403: "You are not authorized for this call.",
            420: "Rate Limit Reached",
            502: "API is down.",
        }
        super(AltmetricHTTPException, self).__init__(
            response_codes.get(status_code, status_code)
        )


class Altmetric(object):
    """The API access class"""

    def __init__(self, api_key=None, api_version='v1'):
        """Cache API key and version."""
        self._api_version = api_version
        if self._api_version != 'v1':
            warnings.warn("This wrapper has only been tested with API v1."
                          "If you try another version it will probably break.")

        self._api_url = "http://api.altmetric.com/{}/".format(
            self._api_version)

        self._api_key = {}
        if api_key:
            self._api_key = {'key': api_key}

    def doi(self, doi, fetch=False, **kwargs):
        """Fetch Altmetric data for DOI."""
        if fetch:
            return self._get_altmetrics_detailed("doi", doi, **kwargs)
        else:
            return self._get_altmetrics("doi", doi, **kwargs)

    def pmid(self, pmid, fetch=False, **kwargs):
        """Fetch Altmetric data for PMID."""
        if fetch:
            return self._get_altmetrics_detailed("pmid", pmid, **kwargs)
        else:
            return self._get_altmetrics("pmid", pmid, **kwargs)

    def uri(self, uri, fetch=False, **kwargs):
        """Fetch Altmetric data for URI."""
        if fetch:
            return self._get_altmetrics_detailed("uri", uri, **kwargs)
        else:
            return self._get_altmetrics("uri", uri, **kwargs)

    def _get_altmetrics(self, method, *args, **kwargs):
        """
        Request information from Altmetric. Return a dictionary.
        """
        request_url = self._api_url + method + \
            "/" + "/".join([a for a in args])
        params = kwargs or {}
        params.update(self._api_key)
        response = requests.get(request_url, params=params)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                raise JSONParseException(str(type(e))+str(e.args))
        elif response.status_code in (404, 400):
            return {}
        else:
            raise AltmetricHTTPException(response.status_code)

    def _get_altmetrics_detailed(self, method, *args, **kwargs):
        """
        Request information from Altmetric. Return a dictionary.
        """
        request_url = self._api_url + "fetch/" + \
            method + "/" + "/".join([a for a in args])
        params = kwargs or {}
        params.update(self._api_key)
        response = requests.get(request_url, params=params)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                raise JSONParseException(str(type(e))+str(e.args))
        elif response.status_code in (404, 400):
            return {}
        else:
            raise AltmetricHTTPException(response.status_code)
