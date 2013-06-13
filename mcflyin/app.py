# -*- coding: utf-8 -*-
'''

McFlyin App: A RESTish API for transforming time series data

'''
import json
import pandas as pd
import numpy as np
from flask import Flask, request
import requests
import transformations as tr


@tr.jsonify
def get_github(user='public'):
    '''Pull Github event data.

    Parameters
    ----------
    user: str, default Firehose
        Github username. Defaults to the global github stream

    Returns
    -------
    Pandas DataFrame of event timestamps

    '''

    if user == 'public':
        uri = 'https://api.github.com/events'
    else:
        uri = 'https://api.github.com/users/{0}/events'.format(user)
    response = requests.get(uri)

    timestamps = []
    for event in response.json:
        timestamps.append(event['created_at'])

    index = pd.to_datetime(timestamps)
    ones = np.ones(len(index))
    df = pd.DataFrame({'Event': ones}, index=index)
    return df

app = Flask(__name__)


@app.route('/github/<username>', methods=['GET'])
def github(username):
    '''Return the last 30 github event timestamps'''
    if request.method == 'GET':
        return json.dumps(get_github(username))


@app.route('/resample', methods=['POST'])
def resample():
    '''Return a JSON of resampled timestamp data'''
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        freq = json.loads(request.form['freq'])
        df = tr.to_df(data)
        json_return = tr.resample(df=df, freq=freq)
        return json.dumps(json_return)


def run():
    '''Run the McFlyin API'''
    app.run(debug='True')

if __name__ == '__main__':
    app.run(debug='True')