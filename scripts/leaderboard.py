import sys
import urllib
import copy

import pandas as pd
from synapseclient import Evaluation


class Query(object):
    """
    An object that helps with paging through annotation query results.

    Also exposes properties totalNumberOfResults, headers and rows.
    """
    def __init__(self, syn, query, limit=1000, offset=0):
        self.syn = syn
        self.query = query
        self.limit = limit
        self.offset = offset
        self.fetch_batch_of_results()

    def fetch_batch_of_results(self):
        uri = "/evaluation/submission/query?query=" + urllib.quote_plus("%s limit %s offset %s" % (self.query, self.limit, self.offset))
        results = self.syn.restGET(uri)
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

    def to_dataframe(self):
        return pd.DataFrame.from_records(
            map(lambda x: x['values'], self.rows), 
                columns=self.headers
        )


def leaderboardQuery(syn, evaluation):

    if type(evaluation) != Evaluation:
        evaluation = syn.getEvaluation(evaluation)

    query = 'select * from evaluation_{}'.format(evaluation.id)
    return Query(syn, query).to_dataframe() 
