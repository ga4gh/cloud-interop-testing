import connexion
import six

from ga4ghtest.models import Plugin  # noqa: E501
from ga4ghtest import util
from ga4ghtest.core.controllers import plugins_controller as controller


def create_plugin(
    body
):  # noqa: E501
    """Create a test plugin

    Add a plugin for testing functionality of an API. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: str
    """
    if connexion.request.is_json:
        body = Plugin.from_dict(connexion.request.get_json())  # noqa: E501
    return controller.create_plugin(
        body=body
    )


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
    return controller.get_plugins(
        sort_by=sort_by,
        order=order,
        limit=limit
    )
