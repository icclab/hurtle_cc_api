#   Copyright (c) 2013-2015, Intel Performance Learning Solutions Ltd, Intel Corporation.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


'''
Modules for PaaS adapters.
'''

import httplib
import json
import logging
import urlparse

LOG = logging.getLogger(__name__)


class OpenShiftAdapter(object):
    '''
    Connects to OpenShift.
    '''

    # XXX: eventually replace with non remote HTTP calls.

    cred = {}

    def __init__(self, uri):
        '''
        Initialize a connection to OpS.
        '''
        tmp = urlparse.urlparse(uri)
        if tmp.scheme != 'https':
            LOG.warn('Please use TLS!')

        self.conn = httplib.HTTPSConnection(tmp.hostname, tmp.port)

    def create_app(self, name, template, size, auth_head):
        '''
        Deploy an app on OpS.
        '''
        if not name or len(name) == 0:
            raise AttributeError('Please provide a valid identifier.')

        body = {
            "name": name,
            "cartridges": template,
            "gear_size": size,
        }

        # TODO: handle namespace - first call wil fail when mcn is not there!
        heads = auth_head
        heads['Content-Type'] = 'application/json'
        self.conn.request('POST', '/broker/rest/domain/mcn/applications',
                          json.dumps(body), heads)

        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        if response.status not in [201]:
            raise AttributeError('OpS could not serve request.',
                                 response.status, repr(tmp['messages']))
        return tmp

    def retrieve_app(self, uid, auth_head):
        '''
        Retrieve a previously deployed app.
        '''
        if not uid or len(uid) == 0:
            raise AttributeError('Please provide a valid identifier.')

        self.conn.request('GET', '/broker/rest/application/' + uid, None,
                          auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        if response.status not in [200]:
            raise AttributeError('Could not retrieve app from OpS.',
                                 response.status, repr(tmp['messages']))

        # Get state...a bit of a hack atm!
        self.conn.request('GET', '/broker/rest/application/' + uid +
                                 '/gear_groups', None,
                          auth_head)
        response = self.conn.getresponse()
        tmp2 = json.loads(response.read())
        self.conn.close()
        if response.status not in [200]:
            raise AttributeError('Could not retrieve app state from OpS.',
                                 response.status, repr(tmp2['messages']))
        return tmp, tmp2

    def delete_app(self, uid, auth_head):
        '''
        Delete an app.
        '''
        if not uid or len(uid) == 0:
            raise AttributeError('Please provide a valid identifier.')

        self.conn.request('DELETE', '/broker/rest/application/' + uid, None,
                          auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        if response.status not in [200]:
            raise AttributeError('Could not delete app in OpS.',
                                 response.status, repr(tmp['messages']))
        return tmp

    def list_apps(self, auth_head):
        '''
        List all app.
        '''
        self.conn.request('GET', '/broker/rest/applications', None, auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        return tmp

    def list_features(self, auth_head):
        '''
        Features are Cartridges in OpS.
        '''
        self.conn.request('GET', '/broker/rest/cartridges', None, auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        return tmp

    def list_gears(self, auth_head):
        '''
        List a set of resource template
        '''
        self.conn.request('GET', '/broker/rest/user', None, auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        return tmp

    def add_service(self, uid, service_name, auth_head):
        '''
        Add a service to an application.
        '''
        body = {'name': service_name}
        heads = self.cred.copy()
        heads['Content-Type'] = 'application/json'
        self.conn.request('POST', '/broker/rest/application/' +
                                  str(uid) + '/cartridges',
                          json.dumps(body), auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        if response.status not in [201]:
            raise AttributeError('Could not add cartridge to app in OpS.',
                                 response.status, repr(tmp['messages']))
        return tmp

    def delete_service(self, uid, service_name, auth_head):
        '''
        Delete a service component.
        '''
        self.conn.request('DELETE', '/broker/rest/application/' + str(uid) +
                                    '/cartridge/' + service_name, None,
                          auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        if response.status not in [200]:
            raise AttributeError('Could not delete cartridge from app in OpS.',
                                 response.status, repr(tmp['messages']))
        return tmp

    # Key management

    def add_key(self, uid, content, auth_head):
        '''
        Adds an public key.
        '''
        heads = self.cred.copy()
        heads['Content-Type'] = 'application/json'
        body = {'name': str(uid),
                'type': 'ssh-rsa',
                'content': str(content)}
        self.conn.request('POST', '/broker/rest/user/keys', json.dumps(body),
                          auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        if response.status not in [201]:
            raise AttributeError('Could not add ssh key.',
                                 response.status, repr(tmp['messages']))
        return tmp

    def list_keys(self, auth_head):
        '''
        Retrieves a list of keys.
        '''
        self.conn.request('GET', '/broker/rest/user/keys', None, auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        return tmp

    def delete_key(self, uid, auth_head):
        '''
        Delete a public key.
        '''
        self.conn.request('DELETE', '/broker/rest/user/keys/' + uid, None,
                          auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        self.conn.close()
        if response.status not in [200]:
            raise AttributeError('Could not delete ssh key.',
                                 response.status, repr(tmp['messages']))

    # Events

    def start_app(self, uid, auth_head):
        '''
        Start an app.
        '''
        return self._event(uid, 'start', auth_head)

    def stop_app(self, uid, auth_head):
        '''
        Stop an app.
        '''
        return self._event(uid, 'stop', auth_head)

    def _event(self, uid, name, auth_head):
        '''
        Trigger an event on the app in OpS.
        '''
        heads = self.cred.copy()
        heads['Content-Type'] = 'application/json'

        body = {'event': name}

        self.conn.request('POST', '/broker/rest/application/' + str(uid) +
                                  '/events', json.dumps(body), auth_head)
        response = self.conn.getresponse()
        tmp = json.loads(response.read())
        if response.status not in [200]:
            self.conn.close()
            raise AttributeError('Error while triggering the event with OpS.',
                                 response.status, repr(tmp['messages']))
        self.conn.close()
        return tmp
