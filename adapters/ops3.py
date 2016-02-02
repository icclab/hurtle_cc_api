#   Copyright 2015 Zuercher Hochschule fuer Angewandte Wissenschaften
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


"""
Modules for PaaS adapters.
"""

import json
import yaml
import logging
import urlparse
import requests
import re
import string
import os

LOG = logging.getLogger(__name__)


class OpenShift3Connector(object):
    """
    Class for the connection to OpenShift
    """

    def __init__(self, uri):
        """
        Initialize a connection to OpS.
        """
        tmp = urlparse.urlparse(uri)
        if tmp.scheme != 'https':
            LOG.warn('Please use TLS!')

        self.url = uri

    @staticmethod
    def request(method, url, headers, allow_redirects=False, data=None, verify=False):
        """
        performs HTTP method against url
        """
        if data is None:
            data = {}
        if method == 'GET':
            return requests.get(url=url, headers=headers, allow_redirects=allow_redirects, data=data, verify=verify)
        if method == 'DELETE':
            return requests.delete(url=url, headers=headers, allow_redirects=allow_redirects, data=data, verify=verify)
        if method == 'POST':
            return requests.post(url=url, headers=headers, allow_redirects=allow_redirects, data=data, verify=verify)
        raise AttributeError("unsupported method specified")


class OpenShift3Adapter(object):
    """
    Connects to OpenShift.
    """

    # future improvements: eventually replace with non remote HTTP calls.

    cred = {}
    PLATFORM = 'OpenShift3'

    def __init__(self, uri, namespace, domain):
        """
        Initialize a adapter to OpS.
        """
        if namespace is None:
            raise Exception('You must configure a namespace in your config file!')

        self.namespace = namespace
        self.domain = domain
        self.url = uri
        self.conn = OpenShift3Connector(uri=uri)

    def request(self, method, url, headers, allow_redirects=False, data=None, verify=False):
        """
        performs HTTP method against url
        """
        if data is None:
            data = {}
        return self.conn.request(method=method, url=url,  headers=headers,
                                 allow_redirects=allow_redirects, data=data, verify=verify)

    def create_app(self, name, dock_image, auth_head, **kwargs):
        """
        Deploy an app on OpS3.

        dock_image is mandatory: the docker image path (e.g. if on dockerhub mcn/rcbso) environment vars in kwargs

        """
        if not name or len(name) == 0:
            raise AttributeError('Please provide a valid identifier.')

        # get a token

        # GET to https://master.ops3.cloudcomplab.ch:8443/oauth/ \
        # authorize?response_type=token&client_id=openshift-challenging-client
        # with auth Header (login, pwd)
        # without redirects (otherwise redirects to oauth then fails)
        # then extract token from Header Location
        # auth_test = ('test', 'test')

        auth_heads = self.get_auth_heads(auth_head)

        # Simple Template Generator for Service, DC, Route

        domain = os.environ.get('DOMAIN', False)
        if not domain:
            raise AttributeError('DOMAIN not set!')
        template_gen = SOTemplateGen(name, self.namespace, dock_image, domain, kwargs.get('env', {}))

        entities = [
            ('api', 'services', 'mongo_svc'),
            ('api', 'services', 'so_svc'),
            ('api', 'services', 'so_admin_svc'),
            ('oapi', 'routes', 'so_route'),
            ('oapi', 'routes', 'so_admin_route'),
            ('oapi', 'deploymentconfigs', 'mongo_dc'),
            ('oapi', 'deploymentconfigs', 'so_dc')
        ]

        for api, url_type, resource_name in entities:
            response = self.request('POST', self.url + '/' + api + '/v1/namespaces/' + self.namespace + '/' + url_type,
                                data=json.dumps(template_gen.get(resource_name)), headers=auth_heads, verify=False,
                                allow_redirects=False)
            if not response.status_code == 201:
                msg = ''
                try:
                    msg = json.loads(response.content)['message']
                except Exception:
                    pass
                raise RuntimeError('Cannot create %s %s, message given: %s' % (url_type, resource_name, msg))

        # Return values for retro-compatibility with OpS2 backend
        tmp = dict()
        tmp['data'] = {'id': name, 'scalable': 'False'}  # leave scale to false for now

        return tmp

    def retrieve_app(self, uid, auth_head):
        """
        Retrieve a previously deployed app.
        """
        # OPS3 : this needs to be the name of the app, not the full uri

        if not uid or len(uid) == 0:
            raise AttributeError('Please provide a valid identifier.')

        # Better status check:
        # Check existing RC for label=name (use first one)
        # Get metadata[annotations[openshift.io/deployment.phase]
        # Status can be Pending/Running/Complete, only when Complete is the docker container ready to be called

        auth_heads = self.get_auth_heads(auth_head)

        response = self.request('GET', self.url + '/api/v1/namespaces/' + self.namespace +
                                '/replicationcontrollers?labelSelector=name=' + uid, headers=auth_heads, verify=False)
        complete = True
        if response.status_code == 200:
            for item in response.json()['items']:
                if item['metadata']['annotations']['openshift.io/deployment.phase'] != 'Complete':
                    complete = False
                    break
        else:
            raise AttributeError('Error while retrieving app with identifier ' + uid)

        tmp = dict()
        # suffix could be retrieved
        tmp['data'] = {'app_url': uid + '.' + self.namespace + self.domain, 'name': uid,
                       'state': complete}

        return tmp, None

    def delete_app(self, uid, auth_head):
        """
        Delete an app.
        """
        if not uid or len(uid) == 0:
            raise AttributeError('Please provide a valid identifier.')

        auth_heads = self.get_auth_heads(auth_head)

        entities = [
            ('api', 'services'),
            ('oapi', 'routes'),
            ('oapi', 'deploymentconfigs'),
            ('api', 'replicationcontrollers'),
        ]

        for api, url_type in entities:
            response = self.request('GET', self.url + '/' + api + '/v1/namespaces/' + self.namespace + '/' + url_type + '?labelSelector=it.hurtle.id=' + uid,
                                    headers=auth_heads, verify=False, allow_redirects=False)
            if not response.status_code == 200:
                raise RuntimeError('Could not retrieve %s ' % url_type)
            resources = response.json()['items']
            for item in resources:
                resource_name = item['metadata']['name']
                j = self.request('DELETE', self.url + '/' + api + '/v1/namespaces/' + self.namespace + '/' + url_type + '/' + resource_name, headers=auth_heads, verify=False)
                if j.status_code != 200:
                    raise AttributeError('Could not delete %s with uid %s' % (url_type, item['metadata']['name']))


        return True

    def get_auth_heads(self, simple_auth_head):
        """
        return ops3 authentication headers (with a valid token) from basic auth
        :param simple_auth_head: the initial request auth headers
        :return: ops3 authentication headers
        """

        if not simple_auth_head:
            raise AttributeError('No auth header provided')

        response = self.request('GET', self.url +
                                '/oauth/authorize?response_type=token&client_id=openshift-challenging-client',
                                headers=simple_auth_head, verify=False, allow_redirects=False)

        # we hit a redirect, which fails with a 500 in current version,
        # so we stop redirect and check for 302 code
        if not response.status_code == 302:
            LOG.error('could not login to OpenShift with these credentials: ' + simple_auth_head)
            raise AttributeError('Login Error')

        location = response.headers['Location']
        ops_token = re.search('access_token=([^&]*)', location).group(1)
        auth_heads = dict()
        auth_heads['Authorization'] = 'Bearer ' + ops_token
        return auth_heads


class SOTemplateGen(object):
    """
    use this to generate all the needed templates for a CI/CD enabled SO
    """

    def __init__(self, so_name, namespace, is_name, base_url, env):
        self.template_dict = {
            "so_name": so_name,
            "namespace": namespace,
            "is_name": is_name,
            'base_url': base_url
        }
        self.env = self.prepare_env(env)

    @staticmethod
    def prepare_env(env):
        """
        splits a string with key=value pairs on '::'
        """
        prepared_env = []
        if '=' not in env:
            return {}
        for env_var_string in env.split('::'):
            env_var_split = env_var_string.split('=')
            env_var_dict = {"name": env_var_split[0],
                            "value": env_var_split[1]}
            prepared_env.append(env_var_dict)
        return prepared_env

    def get_file(self, name):
        from os import system

        with open('./adapters/ops3_templates/so/%s.yaml' % name) as file:
            return file.read()

    def get(self, name):
        template = string.Template(self.get_file(name))
        prepared_template = yaml.load(template.safe_substitute(self.template_dict))

        # handle env vars
        if prepared_template['kind'] == 'DeploymentConfig':
            containers = prepared_template['spec']['template']['spec']['containers']
            prepared_containers = []
            for container in containers:
                if not container['env']:
                    container['env'] = []
                for envVar in self.env:
                    container['env'].append(envVar)
                prepared_containers.append(container)
            prepared_template['spec']['template']['spec']['containers'] = prepared_containers

        return prepared_template
