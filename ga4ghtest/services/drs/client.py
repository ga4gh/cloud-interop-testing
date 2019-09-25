import logging
import json
import requests

from ga4gh.drs.cli.methods.get import get


def api_reponse(postresult):
    if postresult.status_code != 200:
        error = str(json.loads(postresult.text))
        logging.error(error)
        raise Exception(error)

    return json.loads(postresult.text)


class DRSClient(object):
    def __init__(self, service):
        self.auth = service['auth']  # auth headers
        self.proto = service['proto']  # http or https
        self.host = service['host']  # domain name of the website (i.e. 'ga4gh.com')
        self.path = 'ga4gh/drs/v1'
        self.base = '%s://%s/%s' % (self.proto, self.host, self.path)

        self.log_file = None
        self.expand = False
        self.max_threads = 1
        self.silent = True
        self.verbosity = 'DEBUG'
        self.suppress_ssl_verify = False

    def get_bundle(self, bundle_id):
        """
        Get a Bundle.

        :return:
        """
        result = requests.get('{base}/bundles/{bundle_id}'
                                  ''.format(base=self.base,
                                            bundle_id=bundle_id),
                                  headers=self.auth)
        return api_reponse(result)

    def get_object(self, object_id):
        """
        Get an Object

        :return:
        """
        postresult = requests.get('{base}/objects/{object_id}'.format(
                                  base=self.base,
                                  object_id=object_id),
                                  headers=self.auth)
        return api_reponse(postresult)

    def getAccessURL(self, object_id, access_id):
        """
        Get AccessURL

        :return:
        """
        postresult = requests.get('{base}/objects/{object_id}/access/{access_id}'.format(
                                  base=self.base,
                                  object_id=object_id,
                                  access_id=access_id),
                                  headers=self.auth)
        return api_reponse(postresult)

    def downloadFile(self, object_id, destPath, expand = False):
        """
        Download a File

        :return:
        """
        response = get(
            url=self.base,
            authtoken=self.auth,
            object_id=object_id,
            output_metadata='',
            logfile=self.log_file,
            silent=self.silent,
            verbosity=self.verbosity,
            suppress_ssl_verify=self.suppress_ssl_verify,
            expand=expand,
            download=True,
            output_dir=destPath,
            max_threads=1,
            validate_checksum=True)

        return response
