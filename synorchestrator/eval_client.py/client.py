import synapseclient
import os
import logging
import yml
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.expanduser('~'), './evals.yml')

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
            quota = {key:challenge_config[evalId].get(key) for key in configuration if challenge_config[evalId].get(key) != "None"}
            evaluation.quota = quota  
            syn.store(evaluation)
            with open(CONFIG_FILE,"r") as stream:
                evalConfig = yaml.load(stream)
            evalConfig
            data_loaded[]

    except Exception as exception:
        logger.error("The evaluation queue id provided: %s, make sure your firstRoundStart configuration is in quotes or it will be read in as a datetime object" % evalId)
        raise ValueError
    return(evaluation)

def create_queue(...):
    """
    Create (and configure) a new Synapse evaluation queue.
    """

    evalEnt = synapseclient.Evaluation(name="name",description="description",contentSource="parentId",submissionReceiptMessage="message",submissionInstructionsMessage="instructions")
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


