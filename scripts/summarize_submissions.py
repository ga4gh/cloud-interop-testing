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


def filter_submissions(submission_df):
    """
    Keep only those submissions with 'status' and 'reportStatus' that 
    are 'VALIDATED'; clean up columns a bit.
    """
    is_valid = (submission_df.status == 'VALIDATED') & (submission_df.reportStatus == 'VALIDATED')
    keep_cols = ['objectId', 'modifiedOn', 'workflow', 'platform', 'environment', 'scopeId', 
                 'user', 'submitterId',  'team', 'teamId',
                 'name', 'entityId', 'versionNumber', 'status', 
                 'reportEntityId', 'reportStatus']
    return submission_df[keep_cols][is_valid]


def update_validated_submissions_table(syn, project_id, valid_df):
    """
    Push the latest version of the combined validated submissions 
    table to Synapse.
    """
    try:
        print("Searching for existing 'ValidatedSubmissions' table...")
        schema_id = [t for t in syn.getChildren(project_id, includeTypes=['table'])
                     if t['name'] == 'ValidatedSubmissions'][0]['id']
        schema = syn.get(schema_id)
        validated_subs_table = syn.tableQuery('select * from {}'.format(schema_id))
        if validated_subs_table.asDataFrame().shape[0] == valid_df.shape[0]:
            print("No new valid submissions since last update.")
        validated_subs_table.schema = schema
        print("Updating 'ValidatedSubmissions' table...")
        update_table = synapseclient.Table(schema, valid_df)
        validated_subs_table = _update_syn_table(validated_subs_table, update_table, 'objectId')
    except IndexError:
        print("Creating 'ValidatedSubmissions' table...")
        project = syn.get(project_id)
        cols = synapseclient.as_table_columns(valid_df)
        schema = synapseclient.Schema(name='ValidatedSubmissions', columns=cols, parent=project)
        validated_subs_table = synapseclient.Table(schema, valid_df)
    print("Storing 'ValidatedSubmissions' table...")
    validated_subs_table = syn.store(validated_subs_table)


def compute_team_stats(valid_df):
    """
    Summarize validated submissions for each team.
    """
    try:
        print("Computing team stats from validated submissions...")
        team_stats_df = (valid_df
                         .groupby(['team'])['workflow', 'platform', 'user']
                         .agg(['nunique']))
        team_stats_df.columns = team_stats_df.columns.droplevel(1)
        team_stats_df['team'] = team_stats_df.index
        colname_map = {'workflow': 'numWorkflows', 'platform': 'numPlatforms', 'user': 'numUsers'}
        return (team_stats_df[['team', 'workflow', 'platform', 'user']]
                .rename(columns=colname_map))
    except IndexError:
        print("No valid submissions; initializing empty team stats table...")
        return pd.DataFrame(columns=['team', 'numWorkflows', 'numPlatforms', 'numUsers'])


def update_team_stats_table(syn, project_id, team_stats_df):
    """
    Push the latest version of the team stats table to Synapse.
    """
    try:
        print("Searching for existing 'TeamStats' table...")
        schema_id = [t for t in syn.getChildren(project_id, includeTypes=['table'])
                     if t['name'] == 'TeamStats'][0]['id']
        schema = syn.get(schema_id)
        team_stats_table = syn.tableQuery('select * from {}'.format(schema_id))
        team_stats_table.schema = schema
        print("Updating 'TeamStats' table...")
        update_table = synapseclient.Table(schema, team_stats_df)
        team_stats_table = _update_syn_table(team_stats_table, update_table, 'team')
    except IndexError:
        print("Creating 'TeamStats' table...")
        project = syn.get(project_id)
        cols = synapseclient.as_table_columns(team_stats_df)
        schema = synapseclient.Schema(name='TeamStats', columns=cols, parent=project)
        team_stats_table = synapseclient.Table(schema, team_stats_df)
    print("Storing 'TeamStats' table...")
    team_stats_table = syn.store(team_stats_table)


def compute_overall_stats(valid_df, team_stats_df):
    overall_stats_uniquser = (valid_df
                              .drop_duplicates(['team', 'platform', 'workflow'])
                              .groupby(['team'])
                              .size())
    overall_stats_allusers = (valid_df
                              .groupby(['team'])
                              .size())
    overall_dfs = [overall_stats_allusers, overall_stats_uniquser]
    submission_stats_df = (pd.concat(overall_dfs, axis=1)
                           .rename(columns={0: 'totalSubmissions', 
                                            1: 'uniqueSubmissions'}))
    return pd.concat([team_stats_df, submission_stats_df], axis=1)


def update_overall_stats_table(syn, project_id, overall_stats_df):
    """
    Push the latest version of the overall stats table to Synapse.
    """
    try:
        print("Searching for existing 'OverallStats' table...")
        schema_id = [t for t in syn.getChildren(project_id, includeTypes=['table'])
                     if t['name'] == 'OverallStats'][0]['id']
        schema = syn.get(schema_id)
        overall_stats_table = syn.tableQuery('select * from {}'.format(schema_id))
        overall_stats_table.schema = schema
        print("Updating 'OverallStats' table...")
        update_table = synapseclient.Table(schema, overall_stats_df)
        overall_stats_table = _update_syn_table(overall_stats_table, update_table, 'team')
    except IndexError:
        print("Creating 'OverallStats' table...")
        project = syn.get(project_id)
        cols = synapseclient.as_table_columns(overall_stats_df)
        schema = synapseclient.Schema(name='OverallStats', columns=cols, parent=project)
        overall_stats_table = synapseclient.Table(schema, overall_stats_df)
    print("Storing 'OverallStats' table...")
    overall_stats_table = syn.store(overall_stats_table)


def main():
    syn = synapseclient.Synapse()
    user = os.environ.get('SYNAPSE_USER', None)
    password = os.environ.get('SYNAPSE_PASSWORD', None)
    syn.login(email=user, password=password)

    project_id = conf.CHALLENGE_SYN_ID
    submission_df = collect_submissions(syn, project_id)

    valid_df = filter_submissions(submission_df)
    update_validated_submissions_table(syn, project_id, valid_df) 

    team_stats_df = compute_team_stats(valid_df)
    update_team_stats_table(syn, project_id, team_stats_df)

    overall_stats_df = compute_overall_stats(valid_df, team_stats_df)
    update_overall_stats_table(syn, project_id, overall_stats_df)

if __name__ == '__main__':
    main()
