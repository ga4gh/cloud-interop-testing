import os
import sys

import synapseclient
from synapseclient import Evaluation, Submission, SubmissionStatus
import challenge_config as conf
import challenge as chal


def update_submissions(syn, evaluation):
    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)

    participant_team = {
        '3363440': 'UCSC GA4GH-DREAM Challenge Team',
        '3360642': 'ETH Zurich NEXUS Workflow Handler',
        '3361538': 'ISB-CGC',
        '3352048': 'EMBL GA4GH-DREAM Challenge Team'
    }    

    for submission, status in syn.getSubmissionBundles(evaluation, status='VALIDATED', limit=100):
	print("> checking team for submission {}".format(submission.id))
        status_annotations = {annot['key']: annot['value']
                              for annot in status['annotations']['stringAnnos']}
        if submission['userId'] in participant_team:
            current_annotation = status_annotations.get('team', None)
            if not current_annotation == participant_team[submission['userId']]:
                status_annotations['team'] = participant_team[submission['userId']]
                print("...updating 'team': '{}' => '{}'"
                      .format(current_annotation, status_annotations['team']))

        add_annotations = synapseclient.annotations.to_submission_status_annotations(
            status_annotations, is_private=False
        )
        status = chal.update_single_submission_status(status, add_annotations)
        syn.store(status)


def main(argv):
    syn = synapseclient.Synapse()
    user = os.environ.get('SYNAPSE_USER', None)
    password = os.environ.get('SYNAPSE_PASSWORD', None)
    syn.login(email=user, password=password)

    project_id = conf.CHALLENGE_SYN_ID
    #for queue_info in conf.evaluation_queues:
    eval_id = argv[0]
    print("updating team annotations for queue {}...".format(eval_id))
    
    update_submissions(syn, eval_id)


if __name__ == '__main__':
    main(sys.argv[1:])
