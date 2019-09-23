from flask import Flask
from flask import request
import json
import datetime
app = Flask(__name__)

@app.route('/')
def hello_world():
    return '{Hello, World!}'

@app.route('/ga4gh/testbed/v1/dashboard', methods=['GET', 'POST'])
def make_test():
    if request.method == 'POST':
        req_data = request.get_json()
        data = dict()
        dash_json = open('dashboard_data.json')
        data = json.load(dash_json)
        data[str(datetime.datetime.now())] = req_data
        dash_json.close()
        outfile = open('dashboard_data.json', 'w')
        json.dump(data, outfile)
        outfile.close()
        return data
    else:
        return '{JSON of all the results}'
