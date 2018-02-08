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
# Author: chris.bare
#
###############################################################################


import synapseclient
import synapseclient.utils as utils
from synapseclient.exceptions import *
from synapseclient import Activity
from synapseclient import Project, Folder, File
from synapseclient import Evaluation, Submission, SubmissionStatus
from synapseclient import Wiki
from synapseclient import Column
from synapseclient.dict_object import DictObject
from synapseclient.annotations import from_submission_status_annotations
import synapseutils as synu

from collections import OrderedDict
from datetime import datetime, timedelta
from itertools import izip
from StringIO import StringIO
import copy

import argparse
import lock
import json
import math
import os
import random
import re
import sys
import tarfile
import tempfile
import time
import traceback
import urllib
import uuid
import warnings

try:
    import challenge_config as conf
except Exception as ex1:
    sys.stderr.write("\nPlease configure your challenge. See challenge_config.template.py for an example.\n\n")
    raise ex1

import messages


# the batch size can be bigger, we do this just to demonstrate batching
BATCH_SIZE = 20

# how many times to we retry batch uploads of submission annotations
BATCH_UPLOAD_RETRY_COUNT = 5

UUID_REGEX = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

# A module level variable to hold the Synapse connection
syn = None


def to_column_objects(leaderboard_columns):
    """
    Turns a list of dictionaries of column configuration information defined
    in conf.leaderboard_columns) into a list of Column objects
    """
    column_keys = ['name', 'columnType', 'maximumSize', 'enumValues', 'defaultValue']
    return [Column(**{ key: col[key] for key in column_keys if key in col}) for col in leaderboard_columns]


def get_user_name(profile):
    names = []
    if 'firstName' in profile and profile['firstName'] and profile['firstName'].strip():
        names.append(profile['firstName'])
    if 'lastName' in profile and profile['lastName'] and profile['lastName'].strip():
        names.append(profile['lastName'])
    if len(names)==0:
        names.append(profile['userName'])
    return " ".join(names)

def update_single_submission_status(status, add_annotations, force=False):
    """
    This will update a single submission's status
    :param:    Submission status: syn.getSubmissionStatus()

    :param:    Annotations that you want to add in dict or submission status annotations format.
               If dict, all submissions will be added as private submissions
    """
    existingAnnotations = status.get("annotations", dict())
    privateAnnotations = {each['key']:each['value'] for annots in existingAnnotations for each in existingAnnotations[annots] if annots not in ['scopeId','objectId'] and each['isPrivate'] == True}
    publicAnnotations = {each['key']:each['value'] for annots in existingAnnotations for each in existingAnnotations[annots] if annots not in ['scopeId','objectId'] and each['isPrivate'] == False}

    if not synapseclient.annotations.is_submission_status_annotations(add_annotations):
        privateAddedAnnotations = add_annotations
        publicAddedAnnotations = dict()
    else:
        privateAddedAnnotations = {each['key']:each['value'] for annots in add_annotations for each in add_annotations[annots] if annots not in ['scopeId','objectId'] and each['isPrivate'] == True}
        publicAddedAnnotations = {each['key']:each['value'] for annots in add_annotations for each in add_annotations[annots] if annots not in ['scopeId','objectId'] and each['isPrivate'] == False} 
    #If you add a private annotation that appears in the public annotation, it switches 
    if sum([key in publicAddedAnnotations for key in privateAnnotations]) == 0:
        pass
    elif sum([key in publicAddedAnnotations for key in privateAnnotations]) >0 and force:
        privateAnnotations = {key:privateAnnotations[key] for key in privateAnnotations if key not in publicAddedAnnotations}
    else:
        raise ValueError("You are trying to add public annotations that are already part of the existing private annotations: %s.  Either change the annotation key or specify force=True" % ", ".join([key for key in privateAnnotations if key in publicAddedAnnotations]))
    if sum([key in privateAddedAnnotations for key in publicAnnotations]) == 0:
        pass
    elif sum([key in privateAddedAnnotations for key in publicAnnotations])>0 and force:
        publicAnnotations= {key:publicAnnotations[key] for key in publicAnnotations if key not in privateAddedAnnotations}
    else:
        raise ValueError("You are trying to add private annotations that are already part of the existing public annotations: %s.  Either change the annotation key or specify force=True" % ", ".join([key for key in publicAnnotations if key in privateAddedAnnotations]))

    privateAnnotations.update(privateAddedAnnotations)
    publicAnnotations.update(publicAddedAnnotations)

    priv = synapseclient.annotations.to_submission_status_annotations(privateAnnotations, is_private=True)
    pub = synapseclient.annotations.to_submission_status_annotations(publicAnnotations, is_private=False)

    for annotType in ['stringAnnos', 'longAnnos', 'doubleAnnos']:
        if priv.get(annotType) is not None and pub.get(annotType) is not None:
            if pub.get(annotType) is not None:
                priv[annotType].extend(pub[annotType])
            else:
                priv[annotType] = pub[annotType]
        elif priv.get(annotType) is None and pub.get(annotType) is not None:
            priv[annotType] = pub[annotType]

    status.annotations = priv
    return(status)

def update_submissions_status_batch(evaluation, statuses):
    """
    Update statuses in batch. This can be much faster than individual updates,
    especially in rank based scoring methods which recalculate scores for all
    submissions each time a new submission is received.

    Work on the retry logic and have to pull down the submission statuses
    """

    for retry in range(BATCH_UPLOAD_RETRY_COUNT):
        try:
            token = None
            offset = 0
            while offset < len(statuses):
                batch = {"statuses"     : statuses[offset:offset+BATCH_SIZE],
                         "isFirstBatch" : (offset==0),
                         "isLastBatch"  : (offset+BATCH_SIZE>=len(statuses)),
                         "batchToken"   : token}
                response = syn.restPUT("/evaluation/%s/statusBatch" % evaluation.id, json.dumps(batch))
                token = response.get('nextUploadToken', None)
                offset += BATCH_SIZE
        except SynapseHTTPError as err:
            # on 412 ConflictingUpdateException we want to retry
            if err.response.status_code == 412:
                # sys.stderr.write('%s, retrying...\n' % err.message)
                time.sleep(2)
            else:
                raise


class Query(object):
    """
    An object that helps with paging through annotation query results.

    Also exposes properties totalNumberOfResults, headers and rows.
    """
    def __init__(self, query, limit=20, offset=0):
        self.query = query
        self.limit = limit
        self.offset = offset
        self.fetch_batch_of_results()

    def fetch_batch_of_results(self):
        uri = "/evaluation/submission/query?query=" + urllib.quote_plus("%s limit %s offset %s" % (self.query, self.limit, self.offset))
        results = syn.restGET(uri)
        self.totalNumberOfResults = results['totalNumberOfResults']
        self.headers = results['headers']
        self.rows = results['rows']
        self.i = 0

    def __iter__(self):
        return self

    def next(self):
        if self.i >= len(self.rows):
            if self.offset >= self.totalNumberOfResults:
                raise StopIteration()
            self.fetch_batch_of_results()
        values = self.rows[self.i]['values']
        self.i += 1
        self.offset += 1
        return values

def validate(evaluation, canCancel, dry_run=False):

    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)

    print "\n\nValidating", evaluation.id, evaluation.name
    print "-" * 60
    sys.stdout.flush()

    for submission, status in syn.getSubmissionBundles(evaluation, status='RECEIVED'):

        ## refetch the submission so that we get the file path
        ## to be later replaced by a "downloadFiles" flag on getSubmissionBundles
        submission = syn.getSubmission(submission)
        annotations = {'workflow':evaluation.name.replace("GA4GH-DREAM_","")}
        #Fill in team annotation
        profile = syn.getUserProfile(submission.userId)
        annotations['user'] = get_user_name(profile)
        if 'teamId' in submission:
            team = syn.getTeam(submission.teamId)
            if 'name' in team:
                annotations['team'] = team['name']
            else:
                annotations['team'] = submission.teamId
        else:
            annotations['team'] = annotations['user']

        ex1 = None #Must define ex1 in case there is no error
        print "validating", submission.id, submission.name
        try:
            is_valid, validation_message = conf.validate_submission(syn, evaluation, submission, annotations)
        except Exception as ex1:
            is_valid = False
            print "Exception during validation:", type(ex1), ex1, ex1.message
            traceback.print_exc()
            validation_message = str(ex1)
        ## fill in team in submission status annotations
        status.status = "VALIDATED" if is_valid else "INVALID"
        if canCancel:
            status.canCancel = True
        if not is_valid:
            annotations["FAILURE_REASON"] = validation_message
        else:
            annotations["FAILURE_REASON"] = ''

        annotations['reportStatus'] = 'EMPTY'
        annotations['reportEntityId'] = ''
 
        add_annotations = synapseclient.annotations.to_submission_status_annotations(annotations,is_private=False)
        status = update_single_submission_status(status, add_annotations)

        if not dry_run:
            status = syn.store(status)
        ## send message AFTER storing status to ensure we don't get repeat messages
        profile = syn.getUserProfile(submission.userId)
        if is_valid:
            messages.validation_passed(
                userIds=[submission.userId],
                username=get_user_name(profile),
                queue_name=evaluation.name,
                submission_id=submission.id,
                submission_name=submission.name)
        else:
            if isinstance(ex1, AssertionError):
                sendTo = [submission.userId]
                username = get_user_name(profile)
            else:
                sendTo = conf.ADMIN_USER_IDS
                username = "Challenge Administrator"

            messages.validation_failed(
                userIds= sendTo,
                username=username,
                queue_name=evaluation.name,
                submission_id=submission.id,
                submission_name=submission.name,
                message=validation_message)


def validate_reports(evaluation, canCancel, dry_run=False):

    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)

    print "\n\nValidating reports", evaluation.id, evaluation.name
    print "-" * 60
    sys.stdout.flush()

    for submission, status in syn.getSubmissionBundles(evaluation, status='VALIDATED'):
        print("checking report status for submission {}".format(submission.id))
        #if submission.id not in ['9621705', '9617386', '9622674']:
        #     continue

        status_annotations = {annot['key']: annot['value']
                              for annot in status['annotations']['stringAnnos']}
        if 'reportStatus' in status_annotations:
             if status_annotations['reportStatus'] == 'VALIDATED':
	         print "report already validated; skipping"
                 continue

        ## refetch the submission so that we get the file path
        ## to be later replaced by a "downloadFiles" flag on getSubmissionBundles
        submission = syn.getSubmission(submission)


        ex1 = None #Must define ex1 in case there is no error
        new_report = False
        print "validating report", submission.id, submission.name
        try:
            report, report_message, new_report = conf.validate_submission_report(syn, evaluation, submission, status_annotations, dry_run)

            print "checked report:", submission.id, submission.name, submission.userId, report
            add_annotations = synapseclient.annotations.to_submission_status_annotations(report, is_private=False)
            status = update_single_submission_status(status, add_annotations)
        except Exception as ex1:
            print "Exception during report validation:", type(ex1), ex1, ex1.message
            traceback.print_exc()
            report_message = str(ex1)

        if not dry_run:
            status = syn.store(status)

        ## send message AFTER storing status to ensure we don't get repeat messages
        profile = syn.getUserProfile(submission.userId)
        if new_report:
            print("sending message for initialized report...")
            messages.report_initialized(
                userIds=[submission.userId],
                username=get_user_name(profile),
                queue_name=evaluation.name,
                submission_id=submission.id,
                report_entity_id=report['reportEntityId'])
        elif report['reportStatus'] == 'VALIDATED':
            messages.report_validation_passed(
                userIds=[submission.userId],
                username=get_user_name(profile),
                queue_name=evaluation.name,
                submission_id=submission.id,
                report_entity_id=report['reportEntityId'])
        else:
            if isinstance(ex1, AssertionError):
                sendTo = [submission.userId]
                username = get_user_name(profile)
            #else:
            #    sendTo = conf.ADMIN_USER_IDS
            #    username = "Challenge Administrator"

                messages.report_validation_failed(
                    userIds= sendTo,
                    username=username,
                    queue_name=evaluation.name,
                    submission_id=submission.id,
                    report_entity_id=report['reportEntityId'],
                    message=report_message)

def score(evaluation, canCancel, dry_run=False):

    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)

    print '\n\nScoring ', evaluation.id, evaluation.name
    print "-" * 60
    sys.stdout.flush()

    for submission, status in syn.getSubmissionBundles(evaluation, status='VALIDATED'):

        status.status = "INVALID"

        ## refetch the submission so that we get the file path
        ## to be later replaced by a "downloadFiles" flag on getSubmissionBundles
        submission = syn.getSubmission(submission)

        try:
            score, message = conf.score_submission(evaluation, submission)

            print "scored:", submission.id, submission.name, submission.userId, score
            add_annotations = synapseclient.annotations.to_submission_status_annotations(score,is_private=True)
            status = update_single_submission_status(status, add_annotations)

            status.status = "SCORED"
            ### Add in DATE as a public annotation and change team annotation to not private
            ## if there's a table configured, update it
            if not dry_run and evaluation.id in conf.leaderboard_tables:
                update_leaderboard_table(conf.leaderboard_tables[evaluation.id], submission, fields=score, dry_run=False)

        except Exception as ex1:
            sys.stderr.write('\n\nError scoring submission %s %s:\n' % (submission.name, submission.id))
            st = StringIO()
            traceback.print_exc(file=st)
            sys.stderr.write(st.getvalue())
            sys.stderr.write('\n')
            message = st.getvalue()

            if conf.ADMIN_USER_IDS:
                submission_info = "submission id: %s\nsubmission name: %s\nsubmitted by user id: %s\n\n" % (submission.id, submission.name, submission.userId)
                messages.error_notification(userIds=conf.ADMIN_USER_IDS, message=submission_info+st.getvalue())

        if not dry_run:
            status = syn.store(status)

        ## send message AFTER storing status to ensure we don't get repeat messages
        profile = syn.getUserProfile(submission.userId)

        if status.status == 'SCORED':
            messages.scoring_succeeded(
                userIds=[submission.userId],
                message=message,
                username=get_user_name(profile),
                queue_name=evaluation.name,
                submission_name=submission.name,
                submission_id=submission.id)
        else:
            messages.scoring_error(
                userIds=conf.ADMIN_USER_IDS,
                message=message,
                username="Challenge Administrator,",
                queue_name=evaluation.name,
                submission_name=submission.name,
                submission_id=submission.id)

    sys.stdout.write('\n')

def invalidateSubmission(evaluation, dry_run=False):
    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)
    for submission, status in syn.getSubmissionBundles(evaluation):
        if status.cancelRequested is True:
            status.status = "INVALID"
            syn.store(status)



def create_leaderboard_table(name, columns, parent, evaluation, dry_run=False):
    if not dry_run:
        schema = syn.store(Schema(name=name, columns=cols, parent=project))
    for submission, status in syn.getSubmissionBundles(evaluation):
        annotations = synapseclient.annotations.from_submission_status_annotations(status.annotations) if 'annotations' in status else {}
        update_leaderboard_table(schema.id, submission, annotations, dry_run)


def update_leaderboard_table(leaderboard_table, submission, fields, dry_run=False):
    """
    Insert or update a record in a leaderboard table for a submission.

    :param fields: a dictionary including all scoring statistics plus the team name for the submission.
    """

    ## copy fields from submission
    ## fields should already contain scoring stats
    fields['objectId'] = submission.id
    fields['userId'] = submission.userId
    fields['entityId'] = submission.entityId
    fields['versionNumber'] = submission.versionNumber
    fields['name'] = submission.name

    results = syn.tableQuery("select * from %s where objectId=%s" % (leaderboard_table, submission.id), resultsAs="rowset")
    rowset = results.asRowSet()

    ## figure out if we're inserting or updating
    if len(rowset['rows']) == 0:
        row = {'values':[]}
        rowset['rows'].append(row)
        mode = 'insert'
    elif len(rowset['rows']) == 1:
        row = rowset['rows'][0]
        mode = 'update'
    else:
        ## shouldn't happen
        raise RuntimeError("Multiple entries in leaderboard table %s for submission %s" % (leaderboard_table,submission.id))

    ## build list of fields in proper order according to headers
    row['values'] = [fields.get(col['name'], None) for col in rowset['headers']]

    if dry_run:
        print mode, "row "+row['rowId'] if 'rowId' in row else "new row", row['values']
    else:
        return syn.store(rowset)


def query(evaluation, columns, out=sys.stdout):
    """Test the query that will be run to construct the leaderboard"""

    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)

    ## Note: Constructing the index on which the query operates is an
    ## asynchronous process, so we may need to wait a bit.
    results = Query(query="select * from evaluation_%s where status==\"SCORED\"" % evaluation.id)

    ## annotate each column with it's position in the query results, if it's there
    cols = copy.deepcopy(columns)
    for column in cols:
        if column['name'] in results.headers:
            column['index'] = results.headers.index(column['name'])
    indices = [column['index'] for column in cols if 'index' in column]
    column_index = {column['index']:column for column in cols if 'index' in column}

    def column_to_string(row, column_index, i):
        if column_index[i]['columnType']=="DOUBLE":
            return "%0.6f"%float(row[i])
        elif column_index[i]['columnType']=="STRING":
            return "\"%s\""%unicode(row[i]).encode('utf-8')
        else:
            return unicode(row[i]).encode('utf-8')

    ## print leaderboard
    out.write(",".join([column['name'] for column in cols if 'index' in column]) + "\n")
    for row in results:
        out.write(",".join(column_to_string(row, column_index, i) for i in indices))
        out.write("\n")


def list_submissions(evaluation, status=None, **kwargs):
    if isinstance(evaluation, basestring):
        evaluation = syn.getEvaluation(evaluation)
    print '\n\nSubmissions for: %s %s' % (evaluation.id, evaluation.name.encode('utf-8'))
    print '-' * 60

    for submission, status in syn.getSubmissionBundles(evaluation, status=status):
        print submission.id, submission.createdOn, status.status, submission.name.encode('utf-8'), submission.userId


def list_evaluations(project):
    print '\n\nEvaluations for project: ', utils.id_of(project)
    print '-' * 60

    evaluations = syn.getEvaluationByContentSource(project)
    for evaluation in evaluations:
        print "Evaluation: %s" % evaluation.id, evaluation.name.encode('utf-8')


def archive(evaluation, archiveType, destination=None, name=None, query=None):
    """
    Archive the submissions for the given evaluation queue and store them in the destination synapse folder.

    :param evaluation: a synapse evaluation queue or its ID
    :param destination: a synapse folder or its ID
    :param query: a query that will return the desired submissions. At least the ID must be returned.
                  defaults to _select * from evaluation_[EVAL_ID] where status=="SCORED"_.
    """
    tempdir = tempfile.mkdtemp()
    archive_dirname = 'submissions_%s' % utils.id_of(evaluation)

    if not query:
        query = 'select * from evaluation_%s where status=="SCORED"' % utils.id_of(evaluation)

    ## for each submission, download it's associated file and write a line of metadata
    results = Query(query=query)
    if 'objectId' not in results.headers:
        raise ValueError("Can't find the required field \"objectId\" in the results of the query: \"{0}\"".format(query))
    if archiveType == "submission":
        if not name:
            name = 'submissions_%s.tgz' % utils.id_of(evaluation)
        tar_path = os.path.join(tempdir, name)
        print "creating tar at:", tar_path
        print results.headers
        with tarfile.open(tar_path, mode='w:gz') as archive:
            with open(os.path.join(tempdir, 'submission_metadata.csv'), 'w') as f:
                f.write( (','.join(hdr for hdr in (results.headers + ['filename'])) + '\n').encode('utf-8') )
                for result in results:
                    ## retrieve file into cache and copy it to destination
                    submission = syn.getSubmission(result[results.headers.index('objectId')])
                    prefixed_filename = submission.id + "_" + os.path.basename(submission.filePath)
                    archive.add(submission.filePath, arcname=os.path.join(archive_dirname, prefixed_filename))
                    line = (','.join(unicode(item) for item in (result+[prefixed_filename]))).encode('utf-8')
                    print line
                    f.write(line + '\n')
            archive.add(
                name=os.path.join(tempdir, 'submission_metadata.csv'),
                arcname=os.path.join(archive_dirname, 'submission_metadata.csv'))

        entity = syn.store(File(tar_path, parent=destination), evaluation_id=utils.id_of(evaluation))
        print("created:", entity.id, entity.name)
        toReturn = entity.id
    else:
        toReturn = {}
        for result in results:
            ## retrieve file into cache and copy it to destination
            submission = syn.getSubmission(result[results.headers.index('objectId')])
            projectEntity = Project('Archived %s %s %s %s' % (time.strftime("%Y%m%d"),submission.id,submission.entity.id,submission.entity.name))
            entity = syn.store(projectEntity)
            copied = synu.copy(syn, submission.entity.id, entity.id)
            toReturn.update(copied)
    return toReturn


## ==================================================
##  Handlers for commands
## ==================================================

def command_list(args):
    """
    List either the submissions to an evaluation queue or
    the evaluation queues associated with a given project.
    """
    if args.all:
        for queue_info in conf.evaluation_queues:
            list_submissions(evaluation=queue_info['id'],
                             status=args.status)
    elif args.challenge_project:
        list_evaluations(project=args.challenge_project)
    elif args.evaluation:
        list_submissions(evaluation=args.evaluation,
                         status=args.status)
    else:
        list_evaluations(project=conf.CHALLENGE_SYN_ID)


def command_check_status(args):
    submission = syn.getSubmission(args.submission)
    status = syn.getSubmissionStatus(args.submission)
    evaluation = syn.getEvaluation(submission.evaluationId)
    ## deleting the entity key is a hack to work around a bug which prevents
    ## us from printing a submission
    del submission['entity']
    print unicode(evaluation).encode('utf-8')
    print unicode(submission).encode('utf-8')
    print unicode(status).encode('utf-8')


def command_reset(args):
    if args.rescore_all:
        for queue_info in conf.evaluation_queues:
            for submission, status in syn.getSubmissionBundles(queue_info['id'], status="SCORED"):
                status.status = args.status
                if not args.dry_run:
                    print unicode(syn.store(status)).encode('utf-8')
    elif args.rescore:
        for queue_id in args.rescore:
            for submission, status in syn.getSubmissionBundles(queue_id, status="SCORED"):
                status.status = args.status
                if args.dry_run:
                    print "dry-run: ", submission.id, status.status
                else:
                    print "reset: ", submission.id, status.status
                    #print unicode(syn.store(status)).encode('utf-8')
    else:
        for submission in args.submission:
            status = syn.getSubmissionStatus(submission)
            status.status = args.status
            if not args.dry_run:
                print unicode(syn.store(status)).encode('utf-8')


def command_validate(args):
    if args.all:
        for queue_info in conf.evaluation_queues:
            validate(queue_info['id'], args.canCancel, dry_run=args.dry_run)
    elif args.evaluation:
        validate(args.evaluation, args.canCancel, dry_run=args.dry_run)
    else:
        sys.stderr.write("\nValidate command requires either an evaluation ID or --all to validate all queues in the challenge")

def command_validate_reports(args):
    if args.all:
        for queue_info in conf.evaluation_queues:
            validate_reports(queue_info['id'], args.canCancel, dry_run=args.dry_run)
    elif args.evaluation:
        validate_reports(args.evaluation, args.canCancel, dry_run=args.dry_run)
    else:
        sys.stderr.write("\nValidate reports command requires either an evaluation ID or --all to validate all queues in the challenge")

def command_score(args):
    if args.all:
        for queue_info in conf.evaluation_queues:
            score(queue_info['id'], args.canCancel, dry_run=args.dry_run)
    elif args.evaluation:
        score(args.evaluation, args.canCancel, dry_run=args.dry_run)
    else:
        sys.stderr.write("\Score command requires either an evaluation ID or --all to score all queues in the challenge")


def command_rank(args):
    raise NotImplementedError('Implement a ranking function for your challenge')


def command_leaderboard(args):
    ## show columns specific to an evaluation, if available
    leaderboard_cols = conf.leaderboard_columns.get(args.evaluation, conf.LEADERBOARD_COLUMNS)

    ## write out to file if --out args given
    if args.out is not None:
        with open(args.out, 'w') as f:
            query(args.evaluation, columns=leaderboard_cols, out=f)
        print "Wrote leaderboard out to:", args.out
    else:
        query(args.evaluation, columns=leaderboard_cols)


def command_archive(args):
    archive(args.evaluation, args.archiveType, args.destination, name=args.name, query=args.query)


## ==================================================
##  main method
## ==================================================

def main():

    if conf.CHALLENGE_SYN_ID == "":
        sys.stderr.write("Please configure your challenge. See sample_challenge.py for an example.")

    global syn

    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--user", help="UserName", default=None)
    parser.add_argument("-p", "--password", help="Password", default=None)
    parser.add_argument("--notifications", help="Send error notifications to challenge admins", action="store_true", default=False)
    parser.add_argument("--send-messages", help="Send validation and scoring messages to participants", action="store_true", default=False)
    parser.add_argument("--acknowledge-receipt", help="Send confirmation message on passing validation to participants", action="store_true", default=False)
    parser.add_argument("--dry-run", help="Perform the requested command without updating anything in Synapse", action="store_true", default=False)
    parser.add_argument("--debug", help="Show verbose error output from Synapse API calls", action="store_true", default=False)

    subparsers = parser.add_subparsers(title="subcommand")

    parser_list = subparsers.add_parser('list', help="List submissions to an evaluation or list evaluations")
    parser_list.add_argument("evaluation", metavar="EVALUATION-ID", nargs='?', default=None)
    parser_list.add_argument("--challenge-project", "--challenge", "--project", metavar="SYNAPSE-ID", default=None)
    parser_list.add_argument("-s", "--status", default=None)
    parser_list.add_argument("--all", action="store_true", default=False)
    parser_list.set_defaults(func=command_list)

    parser_status = subparsers.add_parser('status', help="Check the status of a submission")
    parser_status.add_argument("submission")
    parser_status.set_defaults(func=command_check_status)

    parser_reset = subparsers.add_parser('reset', help="Reset a submission to RECEIVED for re-scoring (or set to some other status)")
    parser_reset.add_argument("submission", metavar="SUBMISSION-ID", type=int, nargs='*', help="One or more submission IDs, or omit if using --rescore-all")
    parser_reset.add_argument("-s", "--status", default='RECEIVED')
    parser_reset.add_argument("--rescore-all", action="store_true", default=False)
    parser_reset.add_argument("--rescore", metavar="EVALUATION-ID", type=int, nargs='*', help="One or more evaluation IDs to rescore")
    parser_reset.set_defaults(func=command_reset)

    parser_validate = subparsers.add_parser('validate', help="Validate all RECEIVED submissions to an evaluation")
    parser_validate.add_argument("evaluation", metavar="EVALUATION-ID", nargs='?', default=None)
    parser_validate.add_argument("--all", action="store_true", default=False)
    parser_validate.add_argument("--canCancel", action="store_true", default=False)
    parser_validate.set_defaults(func=command_validate)

    parser_validate_reports = subparsers.add_parser('validate_reports', help="Validate reports for all VALIDATED submissions to an evaluation")
    parser_validate_reports.add_argument("evaluation", metavar="EVALUATION-ID", nargs='?', default=None)
    parser_validate_reports.add_argument("--all", action="store_true", default=False)
    parser_validate_reports.add_argument("--canCancel", action="store_true", default=False)
    parser_validate_reports.set_defaults(func=command_validate_reports)

    parser_score = subparsers.add_parser('score', help="Score all VALIDATED submissions to an evaluation")
    parser_score.add_argument("evaluation", metavar="EVALUATION-ID", nargs='?', default=None)
    parser_score.add_argument("--all", action="store_true", default=False)
    parser_score.add_argument("--canCancel", action="store_true", default=False)
    parser_score.set_defaults(func=command_score)

    parser_rank = subparsers.add_parser('rank', help="Rank all SCORED submissions to an evaluation")
    parser_rank.add_argument("evaluation", metavar="EVALUATION-ID", default=None)
    parser_rank.set_defaults(func=command_rank)

    parser_archive = subparsers.add_parser('archive', help="Archive submissions to a challenge")
    parser_archive.add_argument("evaluation", metavar="EVALUATION-ID", default=None)
    parser_archive.add_argument("archiveType",metavar="TYPE", choices=["submission","writeup"])
    parser_archive.add_argument("destination", metavar="FOLDER-ID", default=None)
    parser_archive.add_argument("-q", "--query", default=None)
    parser_archive.add_argument("-n", "--name", default=None)
    parser_archive.set_defaults(func=command_archive)

    parser_leaderboard = subparsers.add_parser('leaderboard', help="Print the leaderboard for an evaluation")
    parser_leaderboard.add_argument("evaluation", metavar="EVALUATION-ID", default=None)
    parser_leaderboard.add_argument("--out", default=None)
    parser_leaderboard.set_defaults(func=command_leaderboard)

    args = parser.parse_args()

    print "\n" * 2, "=" * 75
    print datetime.utcnow().isoformat()

    ## Acquire lock, don't run two scoring scripts at once
    try:
        update_lock = lock.acquire_lock_or_fail('challenge', max_age=timedelta(hours=4))
    except lock.LockedException:
        print u"Is the scoring script already running? Can't acquire lock."
        # can't acquire lock, so return error code 75 which is a
        # temporary error according to /usr/include/sysexits.h
        return 75

    try:
        syn = synapseclient.Synapse(debug=args.debug)
        if not args.user:
            args.user = os.environ.get('SYNAPSE_USER', None)
        if not args.password:
            args.password = os.environ.get('SYNAPSE_PASSWORD', None)
        syn.login(email=args.user, password=args.password)

        ## initialize messages
        messages.syn = syn
        messages.dry_run = args.dry_run
        messages.send_messages = args.send_messages
        messages.send_notifications = args.notifications
        messages.acknowledge_receipt = args.acknowledge_receipt

        args.func(args)

    except Exception as ex1:
        sys.stderr.write('Error in scoring script:\n')
        st = StringIO()
        traceback.print_exc(file=st)
        sys.stderr.write(st.getvalue())
        sys.stderr.write('\n')

        if conf.ADMIN_USER_IDS:
            messages.error_notification(userIds=conf.ADMIN_USER_IDS, message=st.getvalue(), queue_name=conf.CHALLENGE_NAME)

    finally:
        update_lock.release()

    print "\ndone: ", datetime.utcnow().isoformat()
    print "=" * 75, "\n" * 2


if __name__ == '__main__':
    main()

