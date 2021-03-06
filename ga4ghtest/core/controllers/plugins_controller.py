import logging

from ga4ghtest.models.request_recipe import RequestRecipe
from ga4ghtest.core.models.plugins.request_plugin import RequestPlugin


logger = logging.getLogger(__name__)


def create_plugin(
    body
):  # noqa: E501
    """Create a test plugin

    Add a plugin for testing functionality of an API. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: str
    """
    if body.recipe_class == 'requestCheck':
        logging.info(f"Initializing plugin of type '{body.recipe_class}'")
        body.recipe = RequestRecipe(body.recipe['request'],
                                    body.recipe['response'])
        plugin = RequestPlugin(**body.to_dict())
    return plugin


def get_plugins(
    sort_by='created_at',
    order='desc',
    limit=3
):  # noqa: E501
    """Get test plugins

    Get the list of available test plugins.  # noqa: E501

    :param sort_by: logic by which to sort matched records
    :type sort_by: str
    :param order: sort order (ascending or descending)
    :type order: str
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: str
    """
    return 'Not Implemented', 501
