import os
import sys
import time

import synapseclient
from synapseclient import Evaluation, Submission, SubmissionStatus
import challenge_config as conf
import challenge as chal
import messages


def send_reminders(syn, evaluation):
    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)
    
    for submission, status in syn.getSubmissionBundles(evaluation, status='VALIDATED', limit=100):
        if submission.id in ['9622071']:
             continue        
	print("> checking report status for submission {}".format(submission.id))
        status_annotations = {annot['key']: annot['value']
                              for annot in status['annotations']['stringAnnos']}

        if 'reportStatus' in status_annotations:
             if status_annotations['reportStatus'] == 'VALIDATED':
                 print "report already validated; skipping"
                 continue

        print("sending message for initialized / in progress report...")
        profile = syn.getUserProfile(submission.userId)
        messages.report_reminder(
            userIds=[submission.userId],
            username=chal.get_user_name(profile),
            queue_name=evaluation.name,
            submission_id=submission.id,
            report_entity_id=status_annotations['reportEntityId'])
        time.sleep(10)


def main(argv):
    syn = synapseclient.Synapse()
    user = os.environ.get('SYNAPSE_USER', None)
    password = os.environ.get('SYNAPSE_PASSWORD', None)
    syn.login(email=user, password=password)
    messages.syn = syn
    project_id = conf.CHALLENGE_SYN_ID
    for queue_info in conf.evaluation_queues:
    #eval_id = argv[0]
        if queue_info['id'] > 9603664:
            print("sending report reminders for queue {}..."
                  .format(queue_info['id']))
            send_reminders(syn, queue_info['id'])


if __name__ == '__main__':
    main(sys.argv[1:])
