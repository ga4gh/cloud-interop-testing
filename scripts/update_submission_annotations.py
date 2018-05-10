import os
import sys

import synapseclient
from synapseclient import Evaluation, Submission, SubmissionStatus
import challenge_config as conf
import challenge as chal

def parse_report(syn, evaluation, submission, status_annotations):
    report, _, _ = conf.validate_submission_report(
        syn, evaluation, submission, status_annotations, dry_run=False
    )
    return report

def update_submissions(syn, evaluation, annotation_keys=None):
    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)
    
    for submission, status in syn.getSubmissionBundles(evaluation, status='VALIDATED', limit=100):
        #if submission.id not in ['9638106']:
        #     continue        
	print("> checking report status for submission {}".format(submission.id))
        status_annotations = {annot['key']: annot['value']
                              for annot in status['annotations']['stringAnnos']}
        report = parse_report(syn, evaluation, submission, status_annotations)
        for key in annotation_keys:
            current_annotation = status_annotations.get(key, None)
            if len(report[key]):
                status_annotations[key] = report[key]
            else:
                status_annotations[key] = 'pending documentation'
            print("...updating '{}': '{}' => '{}'"
                  .format(key, current_annotation, status_annotations[key]))

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
    print("backfilling submission annotations for queue {}...".format(eval_id))
    
    update_submissions(syn, eval_id, annotation_keys=['platform', 'environment'])


if __name__ == '__main__':
    main(sys.argv[1:])
