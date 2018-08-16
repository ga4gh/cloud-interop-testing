

# def get_workflow_checker(self, id):
#     """
#     Return entry for the specified workflow's "checker workflow."
#     """
#     checker_url = urllib.unquote(self.get_workflow(id=id)['checker_url'])
#     checker_id = re.sub('^.*#workflow/', '', checker_url)
#     logger.info("found checker workflow: {}".format(checker_id))
#     return self.get_workflow(id=checker_id)

# def post_verification(self, id, version_id, type, relative_path, requests):
#     """
#     Annotate test JSON with information on whether it ran successfully on particular platforms plus metadata
#     """
#     id = _format_workflow_id(id)
#     endpoint ='extended/{}/versions/{}/{}/tests/{}'.format(
#         id, version_id, type, relative_path
#     )
#     return _post_to_endpoint(self, endpoint, requests)