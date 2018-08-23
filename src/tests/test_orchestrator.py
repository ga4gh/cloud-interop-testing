#!/usr/bin/env python

import unittest
import os
from synorchestrator import orchestrator, util


class OrchestratorTests(unittest.TestCase):

    def setUp(self):
        super(OrchestratorTests, self).setUp()
        self.queue_loc = os.path.join(os.path.expanduser('~'), 'submission_queue.json')

    def tearDown(self):
        super(OrchestratorTests, self).tearDown()

        try:
            os.remove(self.queue_loc)
        except OSError:
            pass

    def testQueuePathWritesFile(self):
        """Make sure that if 'submission_queue.json' does not exist, queue_path() will create one."""
        expected_loc = self.queue_loc
        self.assertFalse(os.path.isfile(expected_loc))
        orch = orchestrator.Orchestrator()
        returned_loc = orch.queue_path  # Should write file.
        self.assertEqual(expected_loc, returned_loc)
        self.assertTrue(os.path.isfile(returned_loc))
        with open(orch.queue_path, 'r') as f:
            self.assertEqual(f.read(), '{}\n')

    def testQueuePathFindsFile(self):
        """Make sure that queue_path() finds the appropriate file."""
        with open(self.queue_loc, 'w') as f:
            f.write('test')
        orch = orchestrator.Orchestrator()
        with open(orch.queue_path, 'r') as f:
            self.assertEqual(f.read(), 'test')

    def testCreateSubmission(self):
        """Test create_submission correctly loads dummy information to submission_queue.json"""
        service = 'service'
        submissions = dict()
        submissions[service] = dict()
        presubmit_ids = ['foo', 'bar']

        for pre_id in presubmit_ids:
            submissions[service][pre_id] = pre_id
        pre_len = len(submissions[service])

        orch = orchestrator.Orchestrator()

        util.save_json(self.queue_loc, submissions)
        new_id = orch.create_submission(service, 'data', 'wf_type', 'wf_name', 'sample')
        submissions = util.get_json(self.queue_loc)

        for pre_id in presubmit_ids:
            self.assertEqual(submissions[service][pre_id], pre_id)

        # Check that new entry was added appropriately.
        self.assertEqual(pre_len + 1, len(submissions[service]))
        self.assertFalse(new_id in presubmit_ids)
        self.assertTrue((new_id in submissions[service]))

        # Check that entry has correct data.
        self.assertEqual(submissions[service][new_id]['status'], 'RECEIVED')
        self.assertEqual(submissions[service][new_id]['data'], 'data')
        self.assertEqual(submissions[service][new_id]['wf_id'], 'wf_name')
        self.assertEqual(submissions[service][new_id]['type'], 'wf_type')
        self.assertEqual(submissions[service][new_id]['sample'], 'sample')
