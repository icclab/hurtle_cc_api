from flask import Flask
import requests
import os

app = Flask('hurtle-cc-api')


@app.route('/')
def home():
    return '', 200


@app.route('/update', methods=['POST'])
def self_update():
    url = os.environ.get('SELF_REBUILD_URL', False)
    if not url:
        return 'CC not configured properly! no SELF_REBUILD_URL found!', 500
    response = requests.post(url=url, verify=False)
    return response.content, response.status_code


def server(host, port):
    app.run(host=host, port=port, debug=False)
