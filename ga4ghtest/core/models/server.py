import logging

import uuid

from ga4ghtest.models.server import Server as ServerModel

logger = logging.getLogger(__name__)


class Server(ServerModel):

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