#!/usr/bin/env python3
import logging
import os
import time
import connexion


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


connex_app = connexion.App(__name__, specification_dir='./openapi/')
