#!/usr/bin/env python3
import os
import logging

import connexion
import click

from ga4ghtest import create_app


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(mock_db=None, db_size=None):
    app = create_app()

    env_host = os.environ.get('FLASK_HOST')
    flask_host = env_host if env_host is not None else 'localhost'
    app.run(host=flask_host, port=8080)


if __name__ == '__main__':
    main()