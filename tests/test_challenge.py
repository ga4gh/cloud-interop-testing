import synapseclient
import pandas as pd
import mock
from nose.tools import assert_raises
import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR,"../python"))
import challenge


def test_readYaml():
    correct = """
34342:
    submissionLimit:    None
"""
    challenge_config = challenge.readYaml(correct)
    expected = {34342:{'submissionLimit':'None'}}
    #CHECK: read yaml returns correct mapping
    assert challenge_config == expected
    incorrect = """
{34342:
    submissionLimit:   foo
    wrong:    foo}
""" 
    #CHECK: incorrectly formatted yaml files will throw an error
    assert_raises(ValueError, challenge.readYaml, incorrect)

def test_checkAndConfigEval():

    syn = mock.create_autospec(synapseclient.Synapse) 
    evaluation = {}
    syn.getEvaluation.return_value=evaluation

    challenge_config = {34342:{'submissionLimit':'None',
                               'firstRoundStart':'None',
                               'roundDurationMillis':'None',
                               'numberOfRounds':'None'}}

    newEvaluation = challenge._configEval(syn, challenge_config, 34342)
    expectedEval = {'quota': {}}
    assert newEvaluation == expectedEval


test_checkAndConfigEval()