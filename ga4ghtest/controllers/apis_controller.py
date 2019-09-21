import connexion
import six

from ga4ghtest import util
from ga4ghtest.core.controllers import apis_controller as controller


def get_apis(
    sort_by='created_at',
    order='desc',
    limit=3
):  # noqa: E501
    """Get APIs

    Get the list of available APIs.  # noqa: E501

    :param sort_by: logic by which to sort matched records
    :type sort_by: str
    :param order: sort order (ascending or descending)
    :type order: str
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: str
    """
    return controller.get_apis(
        sort_by=sort_by,
        order=order,
        limit=limit
    )
