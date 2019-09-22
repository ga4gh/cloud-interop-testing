from ga4ghtest.core.models.server import Server


def get_servers(
    sort_by='created_at',
    order='desc',
    limit=3
):  # noqa: E501
    """Get target servers

    Get the list of available servers.  # noqa: E501

    :param sort_by: logic by which to sort matched records
    :type sort_by: str
    :param order: sort order (ascending or descending)
    :type order: str
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: str
    """
    return 'Not Implemented', 501


def register_server(
    body
):  # noqa: E501
    """Register a server

    Add an API server to the testbed. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: str
    """
    return 'Not Implemented', 501
