from flask import Flask
import requests
import os
import re
import json

app = Flask('hurtle-cc-api')


@app.route('/')
def home():
    return '', 200


@app.route('/build/<name>', methods=['POST'])
def build(name):
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


@app.route('/update/<name>', methods=['POST'])
def update(name):
    if name == 'self':
        return 'CC does not support update on itself, use build instead!', 500

    namespace = os.environ.get('NAMESPACE')
    uri = os.environ.get('URI')

    response = requests.get(uri + '/oauth/authorize?response_type=token&client_id=openshift-challenging-client',
                            auth=('demo', 'LU4JiFJSuL0H3r5bCJ1A3A'), verify=False, allow_redirects=False)

    if not response.status_code == 302:
        raise AttributeError('Login Error')

    location = response.headers['Location']
    ops_token = re.search('access_token=([^&]*)', location).group(1)
    auth_heads = dict()
    auth_heads['Authorization'] = 'Bearer ' + ops_token

    r = requests.get('%s/oapi/v1/namespaces/%s/deploymentconfigs/%s' % (uri, namespace, name),
                     headers=auth_heads, verify=False)

    if r.status_code != 200:
        return 'DeploymentConfig %s not found!' % name, 404
    deployment_config = json.loads(r.content)

    deployment_config['status']['latestVersion'] += 1
    new_env = []
    found = False
    for env in deployment_config['spec']['template']['spec']['containers'][0]['env']:
        if env['name'] == 'VERSION':
            env['value'] = str(int(env['value']) + 1)
            found = True
        new_env.append(env)
    if not found:
        new_env.append({'name': 'VERSION', 'value': deployment_config['status']['latestVersion']})
    deployment_config['spec']['template']['spec']['containers'][0]['env'] = new_env

    deployment_config_json = json.dumps(deployment_config)

    r = requests.put('%s/oapi/v1/namespaces/%s/deploymentconfigs/%s' % (uri, namespace, name), headers=auth_heads, verify=False, data=deployment_config_json)

    if r.status_code == 200:
        return json.dumps(deployment_config), 200
    else:
        return 'Something went wrong!', r.status_code


def server(host, port):
    app.run(host=host, port=port, debug=False)
