#!/usr/bin/env python

import unittest
import os
import json
from synorchestrator import config, util


class ConfigTests(unittest.TestCase):

    def setUp(self):
        super(ConfigTests, self).setUp()
        self.default_loc = os.path.join(os.path.expanduser('~'), 'orchestrator_config.json')
        self.config_loc = os.path.join(os.path.expanduser('~'), 'test_orchestrator_config.json')

    def tearDown(self):
        super(ConfigTests, self).tearDown()

        try:
            os.remove(self.config_loc)
        except OSError:
            try:
                os.remove(self.default_loc)
            except OSError:
                pass

    def testConfigInitWritesDefaultLoc(self):
        """Test that Config() writes the default json to the default location."""
        self.assertFalse(os.path.exists(self.default_loc))
        c1 = config.Config()  # Writes to the same location as self.default_loc
        self.assertTrue(os.path.exists(self.default_loc))
        self.assertEqual(c1.config_path, self.default_loc)
        with open(c1.config_path, 'r') as f:
            self.assertEqual(f.read(), '{"workflows": {},\n'
                                        ' "toolregistries": {},\n'
                                        ' "workflowservices": {}'
                                        '}\n')

    def testConfigInitWritesSpecifiedLoc(self):
        """Test that Config() writes the default json to a specified location."""
        self.assertFalse(os.path.exists(self.config_loc))
        c1 = config.Config(self.config_loc)  # Writes to the same location as self.default_loc
        self.assertTrue(os.path.exists(self.config_loc))
        self.assertEqual(c1.config_path, self.config_loc)
        with open(c1.config_path, 'r') as f:
            self.assertEqual(f.read(), '{"workflows": {},\n'
                                        ' "toolregistries": {},\n'
                                        ' "workflowservices": {}'
                                        '}\n')

    def testConfigInitFindsExistingFile(self):
        """Test that Config() finds the proper file."""
        with open(self.config_loc, 'w') as f:
            f.write('test')

        c = config.Config(self.config_loc)
        self.assertEqual(self.config_loc, c.config_path)

        with open(c.config_path, 'r') as f:
            self.assertEqual(f.read(), 'test')

    def testConfigs(self):
        """
        Make sure that the various config fetching functions reads the right data from the config file.

        This test checks that the following functions return as expected:
            config.wf_config()
            config.trs_config()
            config.wes_config()
        """
        c = config.Config(self.config_loc)
        config_entries = {'workflows': c.wf_config,
                          'toolregistries': c.trs_config,
                          'workflowservices': c.wes_config}

        for entry, get_func in config_entries.items():
            config_file = util.get_json(c.config_path)
            config_file[entry] = entry  # X_config() returns whatever is stored here.
            util.save_json(c.config_path, config_file)
            self.assertEqual(get_func(), entry)

    def testAddWorkflow(self):
        """Test that add_workflow() adds entries to the config properly."""
        c = config.Config(self.config_loc)  # Write the empty file.
        c.add_workflow('cactus',
                        'Toil',
                        'wf_url',
                        'workflow_attachments',
                        'submission_type',
                        'trs_id',
                        'version_id')
        config_file = util.get_json(self.config_loc)

        self.assertTrue('workflows' in config_file)
        self.assertTrue('cactus' in config_file['workflows'])
        var_name = config_file['workflows']['cactus']
        self.assertEqual(var_name['submission_type'], 'submission_type')
        self.assertEqual(var_name['trs_id'], 'trs_id')
        self.assertEqual(var_name['version_id'], 'version_id')
        self.assertEqual(var_name['workflow_url'], 'wf_url')
        self.assertEqual(var_name['workflow_attachments'], 'workflow_attachments')
        self.assertEqual(var_name['workflow_type'], 'Toil')
