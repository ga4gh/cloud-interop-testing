import logging
import requests

import uuid

from ga4ghtest.core.models.plugins import Plugin

logger = logging.getLogger(__name__)


class RequestPlugin(Plugin):

    def __init__(self,
                 name='',
                 request='',
                 response='',
                 **kwargs):
        super().__init__(name=name)
        for kw in kwargs:
            self.__setattr__(kw, kwargs[kw])
        self.recipe = _build_recipe(request, response)

    def _build_recipe(self, request, response):
        req_url = '{{server}}/{api_base}/{request}'.format(
            api_base=self.api_base_url,
            request=request
        )
        def recipe(req_url, response):
            res = requests.get(req_url)
            return res == response
        return recipe

    # def find(self, db):
    #     pass


    # def save(self, db):
    #     pass


    # def load(self):
    #     self.recipe.stage()


    def run(self):
        self.recipe.run()