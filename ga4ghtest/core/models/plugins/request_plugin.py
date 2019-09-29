import logging
import requests
import json

import uuid

from ga4ghtest.core.models.plugins import Plugin
from ga4ghtest.models.request_recipe import RequestRecipe

logger = logging.getLogger(__name__)


class RequestPlugin(Plugin):

    def __init__(self,
                 recipe,
                 name='',
                 **kwargs):
        super().__init__(name=name)
        for kw in kwargs:
            self.__setattr__(kw, kwargs[kw])

        self.api_base_url = 'ga4gh/wes/v1'
        self.recipe = self._build_recipe(
            recipe.request,
            recipe.response
        )


    def _build_recipe(self, request, response):
        req_url = '{{server}}/{api_base}/{request}'.format(
            api_base=self.api_base_url,
            request=request
        )
        def recipe(runner):
            res = requests.get(req_url.format(server=runner))
            return json.dumps(res.json()) == response
        return recipe


    def find(self, db):
        pass


    def save(self, db):
        pass


    def run(self, runner):
        return self.recipe(runner)