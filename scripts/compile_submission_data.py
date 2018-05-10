import os
import sys
import re

import synapseclient
from synapseclient import Evaluation, Submission, SubmissionStatus
import challenge_config as conf
import challenge as chal


def collect_report_data(syn, report_id):
    # get submission report wiki
    report_wiki = syn.getWiki(report_id)

    print('checking report')
    # validate report
    report_dict = conf._parse_wiki_yaml(report_wiki.markdown)
    
    return report_dict, report_wiki.markdown


def update_submissions(syn, evaluation, out_folder, annotation_keys=None):
    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)
    
    for submission, status in syn.getSubmissionBundles(evaluation, status='VALIDATED', limit=100):
	print("> checking report status for submission {}".format(submission.id))
        status_annotations = {annot['key']: annot['value']
                              for annot in status['annotations']['stringAnnos']}
        report_status, report_id = (
            status_annotations['reportStatus'],
            status_annotations['reportEntityId']
        )
        if report_status != 'VALIDATED':
            continue
 
        report_dict, report_markdown = collect_report_data(syn, report_id)

        out_subfolder = os.path.join(
            out_folder,
            conf.evaluation_queue_by_id[int(evaluation.id)]['handle'], 
        )
        if not os.path.exists(out_subfolder):
            os.mkdir(out_subfolder)

        report_md_path = os.path.join(out_subfolder,
                                      '{}_report.md'.format(submission.id))
        with open(report_md_path, 'w') as f:
            f.write(report_markdown.encode('utf-8'))

        if annotation_keys is None:
            get_keys = [key for key in report_dict.keys()
                        if not re.search('_ex$', key)]
        else:
            get_keys = annotation_keys

        for key in get_keys:
            current_annotation = status_annotations.get(key, None)
            if current_annotation != report_dict[key]:
                status_annotations[key] = report_dict[key]
                print("...updating '{}': '{}' => '{}'"
                      .format(key, current_annotation, 
                              status_annotations[key].encode('utf-8')))

        add_annotations = synapseclient.annotations.to_submission_status_annotations(
            status_annotations, is_private=False
        )
        status = chal.update_single_submission_status(status, add_annotations)
        syn.store(status)
    print("done.")


def main(argv):
    syn = synapseclient.Synapse()
    user = os.environ.get('SYNAPSE_USER', None)
    password = os.environ.get('SYNAPSE_PASSWORD', None)
    syn.login(email=user, password=password)

    project_id = conf.CHALLENGE_SYN_ID
    out_folder = argv[0]
    for queue_info in conf.evaluation_queues:
        print("backfilling submission annotations for queue {}..."
              .format(queue_info['id']))
        update_submissions(syn, queue_info['id'], out_folder)


if __name__ == '__main__':
    main(sys.argv[1:])
