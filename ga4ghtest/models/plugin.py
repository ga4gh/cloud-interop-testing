# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from ga4ghtest.models.base_model_ import Model
from ga4ghtest import util


class Plugin(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, name=None, version=None, api=None, test=None):  # noqa: E501
        """Plugin - a model defined in OpenAPI

        :param name: The name of this Plugin.  # noqa: E501
        :type name: str
        :param version: The version of this Plugin.  # noqa: E501
        :type version: str
        :param api: The api of this Plugin.  # noqa: E501
        :type api: str
        :param test: The test of this Plugin.  # noqa: E501
        :type test: str
        """
        self.openapi_types = {
            'name': str,
            'version': str,
            'api': str,
            'test': str
        }

        self.attribute_map = {
            'name': 'name',
            'version': 'version',
            'api': 'api',
            'test': 'test'
        }

        self._name = name
        self._version = version
        self._api = api
        self._test = test

    @classmethod
    def from_dict(cls, dikt) -> 'Plugin':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Plugin of this Plugin.  # noqa: E501
        :rtype: Plugin
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self):
        """Gets the name of this Plugin.


        :return: The name of this Plugin.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Plugin.


        :param name: The name of this Plugin.
        :type name: str
        """

        self._name = name

    @property
    def version(self):
        """Gets the version of this Plugin.


        :return: The version of this Plugin.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this Plugin.


        :param version: The version of this Plugin.
        :type version: str
        """

        self._version = version

    @property
    def api(self):
        """Gets the api of this Plugin.


        :return: The api of this Plugin.
        :rtype: str
        """
        return self._api

    @api.setter
    def api(self, api):
        """Sets the api of this Plugin.


        :param api: The api of this Plugin.
        :type api: str
        """
        allowed_values = ["WES", "TRS"]  # noqa: E501
        if api not in allowed_values:
            raise ValueError(
                "Invalid value for `api` ({0}), must be one of {1}"
                .format(api, allowed_values)
            )

        self._api = api

    @property
    def test(self):
        """Gets the test of this Plugin.


        :return: The test of this Plugin.
        :rtype: str
        """
        return self._test

    @test.setter
    def test(self, test):
        """Sets the test of this Plugin.


        :param test: The test of this Plugin.
        :type test: str
        """

        self._test = test