import logging
import requests
import json

import uuid

from ga4ghtest.core.models.plugins import Plugin
from ga4ghtest.models.request_recipe import RequestRecipe

logger = logging.getLogger(__name__)


class RequestPlugin(Plugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        recipe = kwargs.pop('recipe')

        api_base_opts = {
            'WES': 'ga4gh/wes/v1',
            'DRS': 'ga4gh/drs/v1',
            'TRS': 'ga4gh/trs/v2'
        }
        self.api_base_url = api_base_opts[self.api]
        self.recipe = self._build_recipe(
            recipe['request'],
            recipe['response']
        )


    def _build_recipe(self, request, response):
        req_url = '{{server}}/{api_base}/{request}'.format(
            api_base=self.api_base_url,
            request=request
        )
        def recipe(runner):
            route = req_url.format(server=runner)
            logger.info(f"Sending request: 'GET {route}'")
            res = requests.get(route)
            logger.info(f"Request status: {res.status_code}")
            return json.dumps(res.json()) == response
        return recipe


    def find(self, db):
        pass


    def save(self, db):
        pass


    def run(self, runner):
        return self.recipe(runner)