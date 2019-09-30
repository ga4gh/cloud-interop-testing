import connexion
import six

from ga4ghtest.models import ServiceTest  # noqa: E501
from ga4ghtest import util
from ga4ghtest.core.controllers import tests_controller as controller


def create_test(
    body
):  # noqa: E501
    """Create a new test

    Create a new plugin run, either right now or with a schedule. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: str
    """
    if connexion.request.is_json:
        body = ServiceTest.from_dict(connexion.request.get_json())  # noqa: E501
    return controller.create_test(
        body=body
    )


def get_test_by_id(
    test_id
):  # noqa: E501
    """Get a test

    Get the status of a given test run.  # noqa: E501

    :param test_id: test ID
    :type test_id: str

    :rtype: ServiceTest
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

    :rtype: List[ServiceTest]
    """
    return controller.get_tests(
        sort_by=sort_by,
        order=order,
        limit=limit
    )
