# import logging
# import os
# import pytest
# import yaml
# import textwrap
#
# from synorchestrator import config
# from synorchestrator.util import get_yaml, save_yaml, heredoc
#
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
#
#
# @pytest.fixture(scope='function')
# def mock_orchestratorconfig(tmpdir):
#     # a mocked config file for a the orchestrator app
#     logger.info("[setup] mock orchestrator config file, create local file")
#
#     mock_config_text = """
#     evals:
#       - 123
#       - 456
#
#     toolregistries:
#       - trs1
#       - trs2
#
#     workflowservices:
#       - wes1
#       - wes2
#     """
#     mock_config_file = tmpdir.join('.orchestratorConfig')
#     logger.debug("writing config file: {}".format(str(mock_config_file)))
#     mock_config_file.write(textwrap.dedent(mock_config_text))
#
#     # point global variable to mock config
#     user_config_file = config.config_path
#     config.CONFIG_PATH = str(mock_config_file)
#
#     yield mock_config_file
#
#     # reset global variable
#     config.CONFIG_PATH = user_config_file
#     logger.info("[teardown] mock orchestrator config file, remove file")
#
#
# def test__get_orchestrator_config(mock_orchestratorconfig):
#     # GIVEN an orchestrator config file exists
#
#     # WHEN the configuration data in the file is loaded
#     test_config = config._get_orchestrator_config()
#
#     # THEN the returned object is correctly parsed from the YAML stream
#     assert(
#         test_config == {
#             'evals': [123, 456],
#             'toolregistries': ['trs1', 'trs2'],
#             'workflowservices': ['wes1', 'wes2']
#         }
#     )
#
#
# def test__get_orchestrator_config_no_config_file(tmpdir):
#     # GIVEN no orchestrator config exists
#     mock_user_home = tmpdir
#     mock_config_file = os.path.join(
#         str(mock_user_home),
#         '.orchestratorConfig'
#     )
#
#     # point global variable to mock config
#     user_config_file = config.config_path
#     config.CONFIG_PATH = mock_config_file
#
#     # WHEN the configuration data in the noexsistent file is loaded
#     test_config = config._get_orchestrator_config()
#
#     # THEN an empty object is returned
#     assert(test_config == {})
#
#     config.CONFIG_PATH = user_config_file
#
#
# def test__save_orchestrator_config(tmpdir):
#     # GIVEN an orchestrator config file exists
#     mock_config_file = mock_orchestratorconfig(tmpdir).next()
#
#     # WHEN updated configuration data is written to the file
#     config.save_yaml({'foo': 'bar'})
#
#     # THEN the file should contain the correct YAML configuration
#     mock_config_text = """foo: bar\n"""
#     with open(str(mock_config_file), 'r') as f:
#         test_config_text = f.read()
#
#     assert(test_config_text == mock_config_text)
#
#
# def test_add_eval(tmpdir):
#     # GIVEN an orchestrator config file exists
#     mock_config_file = mock_orchestratorconfig(tmpdir).next()
#
#     # WHEN an evaluation queue is added to the configuration of the
#     # workflow orchestrator app
#     config.add_eval(42)
#
#     # THEN the evaluation queue ID should be stored in the list
#     with open(str(mock_config_file), 'r') as f:
#         test_config = yaml.load(f)
#
#     assert(42 in test_config['evals'])
#
#
# def test_add_toolregistry(tmpdir):
#     # GIVEN an orchestrator config file exists
#     mock_config_file = mock_orchestratorconfig(tmpdir).next()
#
#     # WHEN a TRS endpoint is added to the configuration of the
#     # workflow orchestrator app
#     config.add_toolregistry('Dockstore')
#
#     # THEN the TRS ID should be stored in the list
#     with open(str(mock_config_file), 'r') as f:
#         test_config = yaml.load(f)
#
#     assert('Dockstore' in test_config['toolregistries'])
#
#
# def test_add_workflowservice(tmpdir):
#     # GIVEN an orchestrator config file exists
#     mock_config_file = mock_orchestratorconfig(tmpdir).next()
#
#     # WHEN a WES endpoint is added to the configuration of the
#     # workflow orchestrator app
#     config.add_workflowservice('workflow-service')
#
#     # THEN the WES ID should be stored in the list
#     with open(str(mock_config_file), 'r') as f:
#         test_config = yaml.load(f)
#
#     assert('workflow-service' in test_config['workflowservices'])
