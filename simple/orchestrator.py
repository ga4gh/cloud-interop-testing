from flask import Flask
from flask import request
app = Flask(__name__)

# from https://flask.palletsprojects.com/en/1.1.x/quickstart/

@app.route('/')
def hello_world():
    return '{Hello, World!}'

@app.route('/ga4gh/testbed/v1/tests', methods=['GET', 'POST'])
def make_test():
    if request.method == 'POST':
        req_data = request.get_json()
        return '''{
  "plugin": "DRS Testing Plugin",
  "servers": {
    "drs://foo.bar.com/ga4gh/v1/drs/object/320e2c9d-1607-4397-8f54-1683469ec26a" : "PASS"
  }
}
'''
    else:
        return 'list of tests'
