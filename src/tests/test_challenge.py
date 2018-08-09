# import synapseclient
# import pandas as pd
# import mock
# from nose.tools import assert_raises
# import os
# import sys
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(SCRIPT_DIR,"../scripts"))
# import challenge


# def test_readYaml():
#     correct = """
# 34342:
#     submissionLimit:    None
# """
#     challenge_config = challenge.readYaml(correct)
#     expected = {34342:{'submissionLimit':'None'}}
#     #CHECK: read yaml returns correct mapping
#     assert challenge_config == expected
#     incorrect = """
# {34342:
#     submissionLimit:   foo
#     wrong:    foo}
# """
#     #CHECK: incorrectly formatted yaml files will throw an error
#     assert_raises(ValueError, challenge.readYaml, incorrect)

# def test_checkAndConfigEval():
#     def my_side_effect(*args, **kwargs):
#         if args[0] == 34342:
#             return(synapseclient.Evaluation(name="temp",contentSource="syn123"))

#     syn = mock.create_autospec(synapseclient.Synapse)
#     syn.getEvaluation.side_effect=my_side_effect

#     challenge_config = {34342:{'submissionLimit':'None',
#                                'firstRoundStart':'None',
#                                'roundDurationMillis':'None',
#                                'numberOfRounds':'None'}}

#     newEvaluation = challenge._configEval(syn, challenge_config, 34342)
#     expectedEval = synapseclient.Evaluation(name="temp",contentSource="syn123",quota={})

#     challenge_config = {34342:{'submissionLimit':2,
#                                'firstRoundStart':"2017-11-02T07:00:00.000Z",
#                                'roundDurationMillis':1645199000,
#                                'numberOfRounds':2}}

#     newEvaluation = challenge._configEval(syn, challenge_config, 34342)
#     expectedEval = synapseclient.Evaluation(name="temp",contentSource="syn123",quota={'submissionLimit':2,
#                                'firstRoundStart':"2017-11-02T07:00:00.000Z",
#                                'roundDurationMillis':1645199000,
#                                'numberOfRounds':2})

#     assert newEvaluation == expectedEval

#     assert_raises(ValueError, challenge._configEval, syn, challenge_config, 33)
