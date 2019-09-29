import logging

import uuid

from ga4ghtest.models.plugin import Plugin as PluginModel

logger = logging.getLogger(__name__)


class Plugin(PluginModel):

    def __init__(self,
                 name='',
                 recipe_class='',
                 **kwargs):
        super().__init__(name=name,
                         recipe_class=recipe_class)
        for kw in kwargs:
            self.__setattr__(kw, kwargs[kw])


    def find(self, db):
        pass


    def save(self, db):
        pass


    def load(self):
        self.recipe.stage()


    def run(self):
        self.recipe.run()


