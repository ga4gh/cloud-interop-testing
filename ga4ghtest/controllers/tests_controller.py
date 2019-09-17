import connexion
import six

from ga4ghtest import util
from ga4ghtest.core.controllers import tests_controller as controller


def create_test(
    body
):  # noqa: E501
    """Create a new test

    Create a new plugin run, either right now or with a schedule. # noqa: E501

    :param body:
    :type body: str

    :rtype: str
    """
    return controller.create_test(
        body=body
    )


def get_test_by_id(
    test_id
):  # noqa: E501
    """Get tests

    Get the status of a given test run.  # noqa: E501

    :param test_id: test ID
    :type test_id: str

    :rtype: str
    """
    return controller.get_test_by_id(
        test_id=test_id
    )


def get_tests(
    sort_by='created_at',
    order='desc',
    limit=3
):  # noqa: E501
    """Get tests

    Get the list of running or scheduled tests.  # noqa: E501

    :param sort_by: logic by which to sort matched records
    :type sort_by: str
    :param order: sort order (ascending or descending)
    :type order: str
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: str
    """
    return controller.get_tests(
        sort_by=sort_by,
        order=order,
        limit=limit
    )
