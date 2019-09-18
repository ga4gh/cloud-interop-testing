import connexion
import six

from ga4ghtest import util
from ga4ghtest.core.controllers import endpoints_controller as controller


def get_endpoints(
    sort_by='created_at',
    order='desc',
    limit=3
):  # noqa: E501
    """Get target endpoints

    Get the list of available endpoints.  # noqa: E501

    :param sort_by: logic by which to sort matched records
    :type sort_by: str
    :param order: sort order (ascending or descending)
    :type order: str
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: str
    """
    return controller.get_endpoints(
        sort_by=sort_by,
        order=order,
        limit=limit
    )


def register_endpoint(
    body
):  # noqa: E501
    """Register an endpoint

    Add an API server endpoint to the testbed. # noqa: E501

    :param body: 
    :type body: str

    :rtype: str
    """
    return controller.register_endpoint(
        body=body
    )
