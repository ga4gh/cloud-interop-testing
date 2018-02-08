# -*- coding: utf-8 -*-
import os
import pandas as pd
import synapseclient
import challenge_config as conf
from leaderboard import leaderboardQuery


def collect_submissions(syn, challenge_id):
    """
    Combine submissions from all evaluation queues into a single
    table and return as dataframe.
    """
    print("Collecting all submissions for '{}'".format(challenge_id))
    evaluations = syn.getEvaluationByContentSource(challenge_id) 
    evaluation_dfs = [leaderboardQuery(syn, evaluation) 
                      for evaluation in evaluations]
    return pd.concat(evaluation_dfs)


def _update_syn_table(syn_table, update_table, update_key):
    """
    Update a Synapse table object based on a local dataframe, using
    a specified key to match rows.
    """
    syn_df = syn_table.asDataFrame()
    update_df = update_table.asDataFrame().set_index(update_key, drop=False)
    for idx, row in syn_df.iterrows():
        update_idx = syn_df.loc[idx, update_key]
        if not syn_df.loc[idx].equals(update_df.loc[update_idx]):
            syn_df.loc[idx] = update_df.loc[update_idx]
    syn_df = syn_df.append(update_df[~update_df[update_key].isin(syn_df[update_key])])
    return synapseclient.Table(syn_table.schema, syn_df)


def update_all_submissions_table(syn, project_id, submission_df):
    """
    Push the latest version of the combined submissions 
    table to Synapse.
    """
    try:
        print("Searching for existing 'AllSubmissions' table...")
        schema_id = [t for t in syn.getChildren(project_id, includeTypes=['table'])
                     if t['name'] == 'AllSubmissions_Annotated'][0]['id']
        schema = syn.get(schema_id)
        all_subs_table = syn.tableQuery('select * from {}'.format(schema_id))
        if all_subs_table.asDataFrame().shape[0] == submission_df.shape[0]:
            print("No new submissions since last update.")
        all_subs_table.schema = schema
        print("Updating 'AllSubmissions' table...")
        update_table = synapseclient.Table(schema, submission_df)
        all_subs_table = _update_syn_table(all_subs_table, update_table, 'objectId')
    except IndexError:
        print("Creating 'AllSubmissions' table...")
        project = syn.get(project_id)
        cols = synapseclient.as_table_columns(submission_df)
        schema = synapseclient.Schema(name='AllSubmissions_Annotated', columns=cols, parent=project)
        all_subs_table = synapseclient.Table(schema, submission_df)
    print("Storing 'AllSubmissions' table...")
    all_subs_table = syn.store(all_subs_table)


def main():
    syn = synapseclient.Synapse()
    user = os.environ.get('SYNAPSE_USER', None)
    password = os.environ.get('SYNAPSE_PASSWORD', None)
    syn.login(email=user, password=password)

    project_id = conf.CHALLENGE_SYN_ID
    submission_df = collect_submissions(syn, project_id)
    submission_df = (submission_df
                     .replace([None], '')
                     .apply(lambda col: col.map(
                         lambda x: x.encode('unicode-escape')
                                    .decode('utf-8')
                     )))         
    update_all_submissions_table(syn, project_id, submission_df)


if __name__ == '__main__':
    main()
