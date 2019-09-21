import logging

import uuid

from ga4ghtest.models.service_test import ServiceTest as ServiceTestModel

logger = logging.getLogger(__name__)


class ServiceTest(ServiceTestModel):

    def __init__(self,
                 name='',
                 **kwargs):
        super().__init__(name=name)
        for kw in kwargs:
            self.__setattr__(kw, kwargs[kw])


    def find(self, db):
        pass


    def save(self, db):
        pass


    def run(self):
        self.plugin.run()
