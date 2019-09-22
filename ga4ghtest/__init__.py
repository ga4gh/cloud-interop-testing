import logging
import connexion

from healthcheck import HealthCheck

from ga4ghtest.config import connex_app


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = connex_app
    app.add_api('openapi.yaml', arguments={'title': 'Provenance Service'})
    # wrap the flask app and give a heathcheck url
    health = HealthCheck(app, "/healthcheck")

    return app