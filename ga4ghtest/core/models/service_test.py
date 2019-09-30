import logging

import uuid

from ga4ghtest.models.service_test import ServiceTest as ServiceTestModel

logger = logging.getLogger(__name__)


class ServiceTest(ServiceTestModel):

    def __init__(self,
                 server,
                 plugin,
                 **kwargs):
        super().__init__(server=server, plugin=plugin)
        for kw in kwargs:
            self.__setattr__(kw, kwargs[kw])
        self.runner = f"{server.proto}://{server.host}"


    def find(self, db):
        pass


    def save(self, db):
        pass


    def run(self):
        logger.info(f"Running test plugin on '{self.runner}'")
        return self.plugin.run(runner=self.runner)
