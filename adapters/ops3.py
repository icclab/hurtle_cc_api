# Copyright (c) 2013-2015, ZHAW.
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
import logging
import urlparse
import requests
import re

LOG = logging.getLogger(__name__)
NAMESPACE = 'mcn'


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

    def __init__(self, uri, namespace=None):
        """
        Initialize a adapter to OpS.
        """
        if namespace is None:
            namespace = NAMESPACE

        self.namespace = namespace
        self.url = uri
        self.conn = OpenShift3Connector(uri=uri)

    def request(self, method, url, headers, allow_redirects=False, data=None, verify=False):
        """
        performs HTTP method against url
        """
        if data is None:
            data = {}
        return self.conn.request(method=method, url=url,  headers=headers, allow_redirects=allow_redirects, data=data, verify=verify)

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
        template_gen = TemplateGen(name, dock_image, kwargs["env"])

        # Create an empty service
        # ----

        response = self.request('POST', self.url + '/api/v1/namespaces/' + NAMESPACE + '/services', data=json.dumps(template_gen.get_serv()), headers=auth_heads, verify=False, allow_redirects=False)

        # response.status_code should be 201
        if not response.status_code == 201:
            raise AttributeError('Cannot create Service ' + name)

        # ----
        # create the deploymentconfig deploying a docker image
        # for now assuming we put all the env vars from the request in all pods

        response = self.request('POST', self.url + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs', data=json.dumps(template_gen.get_dc()), verify=False, headers=auth_heads)

        # response.status_code should be 201
        if not response.status_code == 201:
            raise AttributeError('Cannot create DC ' + name)

        # ----
        # Create a route of type name.namespace.apps.ops3.cloudcomplab.ch

        response = self.request('POST', self.url + '/oapi/v1/namespaces/' + NAMESPACE + '/routes', data=json.dumps(template_gen.get_route('.apps.ops3.cloudcomplab.ch')), verify=False, headers=auth_heads)

        # response.status_code should be 201
        if not response.status_code == 201:
            raise AttributeError('Cannot create Route ' + name)

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

        response = self.request('GET', self.url + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers?labelSelector=name=' + uid, headers=auth_heads, verify=False)
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
        tmp['data'] = {'app_url': uid + '.' + NAMESPACE + '.apps.ops3.cloudcomplab.ch', 'name': uid, 'state': complete}

        return tmp, None

    def delete_app(self, uid, auth_head):
        """
        Delete an app.
        """
        # OPS3 : this needs to be the name of the app, not the full uri
        if not uid or len(uid) == 0:
            raise AttributeError('Please provide a valid identifier.')

        # Delete at minimum: service, pods, rc, dc, route
        # service, rc, dc, route: delete by name
        # pods: GET with labelSelector=name=[name] then for item in result[items], DELETE pod/item[metadata][name]
        # dc seems to be like pods even if we create one
        # suppose uid = name for now

        auth_heads = self.get_auth_heads(auth_head)

        # wrap all that with exceptions

        # delete service
        response = self.request('DELETE', self.url + '/api/v1/namespaces/' + NAMESPACE + '/services/' + uid, headers=auth_heads, verify=False)
        if response.status_code != 200:
            raise AttributeError('Could not delete service with uid ' + uid)

        # delete route
        response = self.request('DELETE', self.url + '/osapi/v1beta3/namespaces/' + NAMESPACE + '/routes/' + uid, headers=auth_heads, verify=False)
        if response.status_code != 200:
            raise AttributeError('Could not delete route with uid ' + uid)

        # delete all deployment configs
        response = self.request('GET', self.url + '/osapi/v1beta3/namespaces/' + NAMESPACE + '/deploymentconfigs?labelSelector=name=' + uid, headers=auth_heads, verify=False)
        if response.status_code == 200:
            for item in response.json()['items']:
                j = self.request('DELETE', self.url + '/osapi/v1beta3/namespaces/' + NAMESPACE + '/deploymentconfigs/' + item['metadata']['name'], headers=auth_heads, verify=False)
                if j.status_code != 200:
                    raise AttributeError('Could not delete deploymentconfig with uid ' + uid)
        else:
            raise AttributeError('Could not retrieve deploymentconfigs')

        # delete all replicationcontrollers
        response = self.request('GET', self.url + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers?labelSelector=name=' + uid, headers=auth_heads, verify=False)
        if response.status_code == 200:
            for item in response.json()['items']:
                j = self.request('DELETE', self.url + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers/' + item['metadata']['name'], headers=auth_heads, verify=False)
                if j.status_code != 200:
                    raise AttributeError('Could not delete replicationcontroller with uid ' + uid)
        else:
            raise AttributeError('Could not retrieve replicationcontrollers')

        # delete all pods
        response = self.request('GET', self.url + '/api/v1/namespaces/' + NAMESPACE + '/pods?labelSelector=name=' + uid, headers=auth_heads, verify=False)
        # possibility of issue here if deletion happens too soon after creation,
        # deploy pod might create application pod during deletion time
        if response.status_code == 200:
            for item in response.json()['items']:
                j = self.request('DELETE', self.url + '/api/v1/namespaces/' + NAMESPACE + '/pods/' + item['metadata']['name'], headers=auth_heads, verify=False)
                if j.status_code != 200:
                    raise AttributeError('Could not delete pod with uid ' + uid)
        else:
            raise AttributeError('Cloud not retrieve pods')
        return True

    def get_auth_heads(self, simple_auth_head):
        """
        return ops3 authentication headers (with a valid token) from basic auth
        :param simple_auth_head: the initial request auth headers
        :return: ops3 authentication headers
        """

        if not simple_auth_head:
            raise AttributeError('No auth header provided')

        response = self.request('GET', self.url + '/oauth/authorize?response_type=token&client_id=openshift-challenging-client', headers=simple_auth_head, verify=False, allow_redirects=False)

        # we hit a redirect, which fails with a 500 in current version,
        # so we stop redirect and check for 302 code
        if not response.status_code == 302:
            raise AttributeError('Login Error')

        location = response.headers['Location']
        ops_token = re.search('access_token=([^&]*)', location).group(1)
        auth_heads = dict()
        auth_heads['Authorization'] = 'Bearer ' + ops_token
        return auth_heads


class TemplateGen(object):
    """
    generates the templates for openshift v3 resources
    """

    def __init__(self, name, docker_image, env=None):
        self.name = name
        # env is a double colon separated string of strings, of type A=B::C=D
        self.env = env
        self.docker_image = docker_image

    def get_dc(self):
        '''
        Retrieve a DeploymentConfig configured with name, docker_image, namespace and env.vars provided
        '''
        deloyment_config = {
            "kind": "DeploymentConfig",
            "apiVersion": "v1",
            "metadata": {
                "name": self.name,
                "namespace": NAMESPACE,
                "creationTimestamp": None,
                "labels": {
                    "deploymentconfig": self.name,
                    "generatedby": "CC_API",
                    "name": self.name
                }
            },
            "spec": {
                "strategy": {
                    "type": "Recreate",
                    "resources": {

                    }
                },
                "triggers": [
                    {
                        "type": "ConfigChange"
                    }
                ],
                "replicas": 1,
                "selector": {
                    "deploymentconfig": self.name
                },
                "template": {
                    "metadata": {
                        "creationTimestamp": None,
                        "labels": {
                            "deploymentconfig": self.name,
                            "generatedby": "CC_API",
                            "name": self.name
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": self.name,
                                # DOCKER PUBLIC IMAGE GOES HERE
                                "image": self.docker_image,
                                "ports": [
                                    {
                                        "name": self.name + "-tcp-8080",
                                        "containerPort": 8080,
                                        "protocol": "TCP"
                                    }
                                ],
                                "resources": {

                                },
                                "terminationMessagePath": "/dev/termination-log",
                                "imagePullPolicy": "Always",
                                "securityContext": {
                                    "capabilities": {

                                    },
                                    "privileged": False
                                },
                            }
                        ],
                        "restartPolicy": "Always",
                        "dnsPolicy": "ClusterFirst"
                    }
                }
            },
            "status": {

            }
        }

        if self.env is not None:
            prepared_env = self.prepare_env(self.env)
            for container in deloyment_config["spec"]["template"]["spec"]["containers"]:
                container["env"] = prepared_env

        return deloyment_config

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

    def get_serv(self):
        """
        Retrieve a Service template with proper name and namespace
        """
        serv = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": self.name,
                "namespace": NAMESPACE,
                "creationTimestamp": None,
                "labels": {
                    "generatedby": "CC_API",
                    "name": self.name
                }
            },
            "spec": {
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 8080,
                        "targetPort": 8080,
                        "nodePort": 0
                    }
                ],
                "selector": {
                    "deploymentconfig": self.name
                },
                "portalIP": "",
                "type": "ClusterIP",
                "sessionAffinity": "None"
            },
            "status": {
                "loadBalancer": {

                }
            }
        }
        return serv

    def get_route(self, suffix):
        """
        retrieve a route template according to name, namespace and suffix
        :param suffix: the ops3 server fqdn (e.g. .apps.ops3.cloudcomplab.ch)
        """
        hostname = self.name + "." + NAMESPACE + suffix
        route = {
            "kind": "Route",
            "apiVersion": "v1beta3",
            "metadata": {
                "name": self.name,
                "creationTimestamp": None,
                "labels": {
                    "generatedby": "CC_API",
                    "name": self.name
                }
            },
            "spec": {
                "host": hostname,
                "to": {
                    "kind": "Service",
                    "name": self.name
                }
            },
            "status": {

            }
        }
        return route
