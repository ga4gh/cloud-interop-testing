#
# Command line tool for scoring and managing Synapse challenges
#
# To use this script, first install the Synapse Python Client
# http://python-docs.synapse.org/
#
# Log in once using your user name and password
#   import synapseclient
#   syn = synapseclient.Synapse()
#   syn.login(<username>, <password>, rememberMe=True)
#
# Your credentials will be saved after which you may run this script with no credentials.
# 
# Author: thomasyu888
#
###############################################################################


import synapseclient
import synapseclient.utils as utils
from synapseclient.exceptions import *
from datetime import datetime, timedelta
from StringIO import StringIO
import lock
import argparse
import os
import sys
import traceback
import logging
import yaml
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%y-%m-%d %H:%M:%S')
logger = logging.getLogger()

import messages

def readYaml(yamlText):
    try:
        challenge_config = yaml.load(yamlText)
    except yaml.YAMLError as exception:
        logger.error("Please provide a correctly formatted config file. Look at example.config for help")
        raise exception
    return(challenge_config)

def runWorkflow(syn):
    pass

def validate(syn, evaluation, canCancel, dry_run=False):

    if not isinstance(evaluation, synapseclient.Evaluation):
        evaluation = syn.getEvaluation(evaluation)
    
    logger.info("-" * 60)
    logger.info("VALIDATING EVAL %s %s" % (evaluation.id, evaluation.name))
    logger.info("-" * 60)

    for submission, status in syn.getSubmissionBundles(evaluation, status='RECEIVED'):
        submission = syn.getSubmission(submission)
        logger.info("Validating %s %s" % (submission.id, submission.name))
        runWorkflow(syn, submission)

def checkAndConfigEval(syn, challenge_config, setEvalConfig=False):
    quotaKeys = ['roundDurationMillis','submissionLimit','firstRoundStart','numberOfRounds']
    evalIds = challenge_config.keys()
    for evalId in evalIds:
        try:
            evaluation = syn.getEvaluation(evalId)
            quota = {key:challenge_config[evalId].get(key) for key in quotaKeys if challenge_config[evalId].get(key) != "None"}
            if setEvalConfig:
                evaluation.quota = quota
                syn.store(evaluation)
        except Exception as exception:
            logger.error("The evaluation queue id provided: %s, make sure your firstRoundStart configuration is in quotes or it will be read in as a datetime object" % evalId)
            raise exception

## ==================================================
##  Handlers for commands
## ==================================================

def command_validate(syn, args):
    if args.all:
        for evalId in args.challenge_config.keys():
            validate(syn, evalId, args.canCancel, dry_run=args.dry_run)
    elif args.evaluation:
        validate(syn, args.evaluation, args.canCancel, dry_run=args.dry_run)
    else:
        logger.error("Validate command requires either an evaluation ID or --all to validate all queues in the challenge")


## ==================================================
##  main method
## ==================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--user", help="UserName", default=None)
    parser.add_argument("-p", "--password", help="Password", default=None)
    parser.add_argument("-c", "--config", help="Challenge Config File", required=True)
    parser.add_argument("--setEvalConfig", help="Set Evaluation quota configuration through the config file", action="store_true")

    parser.add_argument("--dry-run", help="Perform the requested command without updating anything in Synapse", action="store_true")
    parser.add_argument("--debug", help="Show verbose error output from Synapse API calls", action="store_true")

    subparsers = parser.add_subparsers(title="subcommand")

    parser_validate = subparsers.add_parser('validate', help="Validate all RECEIVED submissions to an evaluation")
    parser_validate.add_argument("evaluation", metavar="EVALUATION-ID", nargs='?', default=None)
    parser_validate.add_argument("--all", action="store_true", default=False)
    parser_validate.add_argument("--canCancel", action="store_true", default=False)
    parser_validate.set_defaults(func=command_validate)

    args = parser.parse_args()

    logger.info("\n" * 2 +  "=" * 75)

    syn = synapseclient.Synapse(debug=args.debug)
    try:
        syn.login(email=args.user, password=args.password, rememberMe=True)
    except Exception as error:
        logger.error("Please provide correct Synapse credentials")
        raise error
    
    with open(args.config) as config:
        args.challenge_config = readYaml(config)

    checkAndConfigEval(syn, args.challenge_config, args.setEvalConfig)
    
    ## Acquire lock, don't run two scoring scripts at once
    try:
        update_lock = lock.acquire_lock_or_fail('challenge', max_age=timedelta(hours=4))
    except lock.LockedException:
        logger.error("Is the scoring script already running? Can't acquire lock.")
        # can't acquire lock, so return error code 75 which is a
        # temporary error according to /usr/include/sysexits.h
        return 75

    try:
        args.func(syn, args)
    except Exception as ex1:
        logger.error('Error in scoring harness:\n')
        st = StringIO()
        traceback.print_exc(file=st)
        logger.error(st.getvalue())
        logger.error('\n')
    finally:
        update_lock.release()

    logger.info("DONE EVAL\n\n"  + "=" * 75)

if __name__ == '__main__':
    main()

