import synapseclient
import os
import logging
import yml
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.orchestratorConfig')
EVALUATION_CONFIG = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'eval.config')
syn = synapseclient.login()

def _configure_queue(evalId, configuration = None):
    """
    Configure external properties of a Synapse evaluation queue,
    either based on a config file (YAML) or set of key-value pairs;
    if the latter, save configuration to config file.
    """

    quotaKeys = ['roundDurationMillis','submissionLimit','firstRoundStart','numberOfRounds']
    try:
        evaluation = syn.getEvaluation(evalId)
        if configuration is not None:
            quota = {key:configuration.get(key) for key in quotaKeys}
            evaluation.quota = quota
            syn.store(evaluation)
            with open(EVALUATION_CONFIG,"r") as stream:
                evalConfig = yaml.load(stream)
            if evalConfig.get(evalId) is None:
                evalConfig[evalId] = quota
            with open(EVALUATION_CONFIG,"w") as stream:
                yaml.dump(evalConfig, stream, default_flow_style=False)
    except Exception as exception:
        logger.error("The evaluation queue id provided: %s, make sure your firstRoundStart configuration is in quotes or it will be read in as a datetime object" % evalId)
        raise ValueError
    return(evaluation)

def create_queue(evaluation_name, description, contentSource, submissionReceiptMessage, submissionInstructionsMessage):
    """
    Create (and configure) a new Synapse evaluation queue.
    """

    evalEnt = synapseclient.Evaluation(name=evaluation_name,description=description,contentSource=contentSource,submissionReceiptMessage=submissionReceiptMessage,submissionInstructionsMessage=submissionInstructionsMessage)
    syn.store(evalEnt)


def update_queue(...):
    """
    Update properties or configuration for an evaluation queue.
    """

    evalEnt = syn.getEvaluation(evalId)
    syn.store(evalEnt)


def create_submission(...):
    """
    Create a new submission for an evaluation queue.
    """

    pass

def get_submissions(evaluation, status):
    """
    Retrieve submission bundles for an evaluation queue.
    """
    if isinstance(evaluation, basestring):
        evaluation = syn.getEvaluation(evaluation)
    return(syn.getSubmissionBundles(evaluation, status=status))


def list_submissions(evaluation, status):
    """
    List submissions for an evaluation queue.
    """

    if isinstance(evaluation, basestring):
        evaluation = syn.getEvaluation(evaluation)
    print '\n\nSubmissions for: %s %s' % (evaluation.id, evaluation.name.encode('utf-8'))
    print '-' * 60

    for submission, status in get_submissions(evaluation, status):
        print submission.id, submission.createdOn, status.status, submission.name.encode('utf-8'), submission.userId


