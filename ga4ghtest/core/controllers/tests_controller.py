from ga4ghtest.models.plugin import Plugin
from ga4ghtest.core.models.service_test import ServiceTest
from ga4ghtest.core.controllers import plugins_controller as plugins


def create_test(
    body
):  # noqa: E501
    """Create a new test

    Create a new plugin run, either right now or with a schedule. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: str
    """
    if type(body.plugin) is Plugin:
        plugin = plugins.create_plugin(
            body.plugin
        )
    test = ServiceTest(
        server=body.server,
        plugin=plugin
    )
    test_status = test.run()
    return {'test_id': 'test_1',
            'plugin_id': 'plugin_1',
            'test_status': 'SUCCESS' if test_status else 'FAIL'}


def get_test_by_id(
    test_id
):  # noqa: E501
    """Get tests

    Get the status of a given test run.  # noqa: E501

    :param test_id: test ID
    :type test_id: str

    :rtype: ServiceTest
    """
    return 'Not Implemented', 501


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
    return 'Not Implemented', 501