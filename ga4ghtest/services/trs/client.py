import logging
import json
import requests


def api_reponse(postresult):
    if postresult.status_code != 200:
        error = str(json.loads(postresult.text))
        logging.error(error)
        raise Exception(error)

    return json.loads(postresult.text)


class TRSClient(object):
    def __init__(self, service):
        self.auth = service['auth']  # auth headers
        self.proto = service['proto']  # http or https
        self.host = service['host']  # domain name of the website (i.e. 'ga4gh.com')
        self.version = 'ga4gh/trs/v2'
        self.base = '%s://%s/%s' % (self.proto, self.host, self.version)

    def get_tools(self):
        """
        List all tools.

        :return:
        """
        postresult = requests.get('{base}/tools'.format(base=self.base),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_tool_types(self):
        """
        List all tool types.

        :return:
        """
        postresult = requests.get('{base}/toolClasses'.format(base=self.base),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_tool(self, tool_id):
        """
        Get one specific tool.

        :param id: A unique identifier of the tool, scoped to this registry, for example 123456.
        :return:
        """
        postresult = requests.get('{base}/tools/{tool_id}'.format(base=self.base, tool_id=tool_id),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_tool_versions(self, tool_id):
        """
        List all versions of a tool.

        :param id: A unique identifier of the tool, scoped to this registry, for example 123456.
        :return:
        """
        postresult = requests.get('{base}/tools/{tool_id}/versions'.format(base=self.base, tool_id=tool_id),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_tool_version(self, tool_id, tool_version):
        """
        Get one specific version of a tool.

        :param id: A unique identifier of the tool, scoped to this registry, for example 123456.
        :param tool_version: An identifier of the tool version, scoped to this registry, for example v1.
                           We recommend that versions use semantic versioning https://semver.org/spec/v2.0.0.html
                           (For example, 1.0.0 instead of develop)
        :return:
        """
        postresult = requests.get('{base}/tools/{tool_id}/versions/{version_id}'
                                  ''.format(base=self.base, tool_id=tool_id, version_id=tool_version),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_tool_descriptor(self, tool_id, tool_version, descriptor_type):
        """
        Get a tool descriptor for one specific version of a tool.

        :param id: A unique identifier of the tool, scoped to this registry, for example 123456.
        :param tool_version: An identifier of the tool version, scoped to this registry, for example v1.
                           We recommend that versions use semantic versioning https://semver.org/spec/v2.0.0.html
                           (For example, 1.0.0 instead of develop)
        :return:
        """
        postresult = requests.get('{base}/tools/{tool_id}/versions/{tool_version}/{tool_type}/descriptor'
                                  ''.format(base=self.base,
                                            tool_id=tool_id,
                                            tool_version=tool_version,
                                            tool_type=descriptor_type),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_relative_tool_descriptor(self, tool_id, tool_version, descriptor_type, rel_path):
        """
        Get a tool descriptor for one specific version of a tool.

        :param id: A unique identifier of the tool, scoped to this registry, for example 123456.
        :param tool_version: An identifier of the tool version, scoped to this registry, for example v1.
                           We recommend that versions use semantic versioning https://semver.org/spec/v2.0.0.html
                           (For example, 1.0.0 instead of develop)
        :return:
        """
        postresult = requests.get('{base}/tools/{tool_id}/versions/{tool_version}/{desc_type}/descriptor/{rel_path}'
                                  ''.format(base=self.base,
                                            tool_id=tool_id,
                                            tool_version=tool_version,
                                            desc_type=descriptor_type,
                                            rel_path=rel_path),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_tool_tests(self, tool_id, tool_version, descriptor_type, rel_path):
        """
        Get all test jsons for a tool.

        :param id: A unique identifier of the tool, scoped to this registry, for example 123456.
        :param tool_version: An identifier of the tool version, scoped to this registry, for example v1.
                           We recommend that versions use semantic versioning https://semver.org/spec/v2.0.0.html
                           (For example, 1.0.0 instead of develop)
        :return:
        """
        postresult = requests.get('{base}/tools/{tool_id}/versions/{tool_version}/{desc_type}/tests'
                                  ''.format(base=self.base,
                                            tool_id=tool_id,
                                            tool_version=tool_version,
                                            desc_type=descriptor_type,
                                            rel_path=rel_path),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_tools_with_relative_path(self, tool_id, tool_version, descriptor_type):
        """
        Get a list of objects that contain the relative path and file type.

        :param id: A unique identifier of the tool, scoped to this registry, for example 123456.
        :param tool_version: An identifier of the tool version, scoped to this registry, for example v1.
                           We recommend that versions use semantic versioning https://semver.org/spec/v2.0.0.html
                           (For example, 1.0.0 instead of develop)
        :return:
        """
        postresult = requests.get('{base}/tools/{tool_id}/versions/{tool_version}/{desc_type}/files'
                                  ''.format(base=self.base,
                                            tool_id=tool_id,
                                            tool_version=tool_version,
                                            desc_type=descriptor_type),
                                  headers=self.auth)
        return api_reponse(postresult)

    def get_tool_container_specs(self, tool_id, tool_version):
        """
        Get container specification(s) for a tool.

        :param id: A unique identifier of the tool, scoped to this registry, for example 123456.
        :param tool_version: An identifier of the tool version, scoped to this registry, for example v1.
                           We recommend that versions use semantic versioning https://semver.org/spec/v2.0.0.html
                           (For example, 1.0.0 instead of develop)
        :return:
        """
        postresult = requests.get('{base}/tools/{tool_id}/versions/{tool_version}/containerfile'
                                  ''.format(base=self.base,
                                            tool_id=tool_id,
                                            tool_version=tool_version),
                                  headers=self.auth)
        return api_reponse(postresult)
