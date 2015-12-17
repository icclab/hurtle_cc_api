from flask import Flask
import requests
import os

app = Flask('hurtle-cc-api')


@app.route('/')
def home():
    return '', 200


@app.route('/update/<name>', methods=['POST'])
def update(name):
    if name == 'self':
        webhook_url = os.environ.get('SELF_REBUILD_URL', False)
        if not webhook_url:
            return 'CC not configured properly! no SELF_REBUILD_URL found!', 500

    else:
        if name == '':
            return 'You must provide a valid name!', 404
        uri = os.environ.get('URI', False)
        namespace = os.environ.get('NAMESPACE', False)
        secret = os.environ.get('SECRET', False)
        if not uri:
            return 'CC not configured properly! no URI found!', 500
        if not namespace:
            return 'CC not configured properly! no NAMESPACE found!', 500
        if not secret:
            return 'CC not configured properly! no SECRET found!', 500

        webhook_url = '%s/oapi/v1/namespaces/%s/buildconfigs/%s/webhooks/%s/generic' % (uri, namespace, name, secret)

    response = requests.post(url=webhook_url, verify=False)
    return response.content, response.status_code


def server(host, port):
    app.run(host=host, port=port, debug=False)
